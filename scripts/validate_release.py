#!/usr/bin/env python3
"""
validate_release.py — Release-state validator for Saudi Real Estate Data

Audits the repo for publishing-readiness:

  1. Every data file is in an accepted format: .csv, .csv.gz, .pdf, .json,
     .md, .png, .yml, .yaml. Flags .xlsx, .xls, .db (data files only).
  2. Every "large" data CSV (>10 MB plain) is gzip-compressed.
  3. Every data subdirectory has a README explaining its contents.
  4. Registry CSVs (data/registry_*.csv + registry.json + schema.json)
     are not stale — diff against a fresh re-run of build_registry.py.

Exit code 0 = clean. Exit code 1 = drift detected. Outputs a human-readable
report to stdout.

No external dependencies — stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()

# Directories whose contents are considered "data" for publication purposes.
DATA_DIRS = ["gastat", "kapsarc", "moj", "rega", "sama", "data"]

# Accepted file extensions in data directories.
ACCEPTED_EXTS = {
    ".csv",
    ".gz",
    ".pdf",
    ".json",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".yml",
    ".yaml",
    ".txt",
}

# Flagged extensions — should be converted or removed.
FLAGGED_EXTS = {
    ".xlsx": "Excel format — convert to .csv (verify integrity first)",
    ".xls": "Legacy Excel format — convert to .csv (verify integrity first)",
    ".db": "SQLite database — should be gitignored; consumers regenerate locally",
    ".sqlite": "SQLite database — should be gitignored",
    ".sqlite3": "SQLite database — should be gitignored",
}

# Files >10 MB plain CSV should be .csv.gz instead.
LARGE_CSV_THRESHOLD_BYTES = 10 * 1024 * 1024  # 10 MB

# Registry artifacts that must be present and fresh.
REGISTRY_ARTIFACTS = [
    "data/registry_files.csv",
    "data/registry_fields.csv",
    "data/registry_enums.csv",
    "data/registry_samples.csv",
    "data/registry_field_aliases.csv",
    "data/registry.json",
    "data/schema.json",
]


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def note(self, msg: str):
        self.info.append(msg)

    def print(self):
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  • {e}")
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  • {w}")
        if self.info:
            print(f"\nℹ️  Info ({len(self.info)}):")
            for i in self.info:
                print(f"  • {i}")

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def is_gitignored(path: Path) -> bool:
    """True if the given path is excluded by .gitignore.

    Uses `git check-ignore` for authoritative behavior. Files not in a git
    repo, or untracked-but-not-gitignored, return False.
    """
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=str(BASE_DIR),
            capture_output=True,
        )
        # exit 0 = ignored, 1 = not ignored, 128 = error
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_file_formats(report: Report):
    """Walk data dirs; flag unaccepted formats.

    Gitignored files are skipped — they don't ship to consumers, so their
    format is a local-tooling concern, not a publishing one.
    """
    flagged_count = 0
    for top in DATA_DIRS:
        top_dir = BASE_DIR / top
        if not top_dir.exists():
            continue
        for root, dirs, files in os.walk(top_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for f in files:
                if f.startswith(".") or f == "__pycache__":
                    continue
                path = Path(root) / f
                rel = path.relative_to(BASE_DIR)
                ext = path.suffix.lower()
                # Handle .csv.gz as accepted
                if f.lower().endswith(".csv.gz"):
                    continue
                # Skip gitignored files — not part of the publishing surface
                if is_gitignored(path):
                    continue
                if ext in FLAGGED_EXTS:
                    report.warn(f"{rel} — {FLAGGED_EXTS[ext]}")
                    flagged_count += 1
                elif ext not in ACCEPTED_EXTS and ext:
                    report.warn(f"{rel} — unrecognized format {ext}")
                    flagged_count += 1
    if flagged_count == 0:
        report.note("All data files are in accepted formats")
    else:
        report.note(f"{flagged_count} flagged-format files (see warnings)")


def check_large_uncompressed_csvs(report: Report):
    """Flag plain .csv files larger than the threshold — should be .csv.gz.

    Gitignored files are skipped — they aren't shipped, so their size is a
    local-tooling concern, not a publishing one.
    """
    large_count = 0
    for top in DATA_DIRS:
        top_dir = BASE_DIR / top
        if not top_dir.exists():
            continue
        for root, dirs, files in os.walk(top_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for f in files:
                if not f.lower().endswith(".csv"):
                    continue
                path = Path(root) / f
                if is_gitignored(path):
                    continue
                size = path.stat().st_size
                if size > LARGE_CSV_THRESHOLD_BYTES:
                    rel = path.relative_to(BASE_DIR)
                    mb = size / (1024 * 1024)
                    report.warn(
                        f"{rel} — {mb:.1f} MB uncompressed CSV "
                        f"(> {LARGE_CSV_THRESHOLD_BYTES // 1024 // 1024} MB threshold). "
                        f"Compress with `gzip -k {rel}` and remove the original after verifying."
                    )
                    large_count += 1
    if large_count == 0:
        report.note(
            f"No CSV files exceed the {LARGE_CSV_THRESHOLD_BYTES // 1024 // 1024} MB threshold uncompressed"
        )
    else:
        report.note(f"{large_count} CSV files should be gzip-compressed")


def check_readmes(report: Report):
    """Every data subdirectory (and the top-level data dirs) should have a README."""
    missing = []
    # Top-level data dirs
    for top in DATA_DIRS:
        top_dir = BASE_DIR / top
        if not top_dir.exists():
            continue
        # Top-level data dirs are covered by repo root README.md, so skip those
        # checks unless the dir is /data/ (new subtree pattern).
        if top == "data":
            # Check immediate subdirs of /data/
            for sub in top_dir.iterdir():
                if sub.is_dir() and not sub.name.startswith("."):
                    if not (sub / "README.md").exists():
                        missing.append(sub.relative_to(BASE_DIR))
    if missing:
        for m in missing:
            report.warn(f"{m}/ — no README.md (per-dataset doc expected)")
    else:
        report.note("All /data/ subdirectories have README.md")


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_registry_freshness(report: Report, skip: bool = False):
    """Re-run build_registry.py against a temp copy of data/ and diff."""
    if skip:
        report.note("Registry freshness check SKIPPED (--no-rebuild)")
        return

    script = BASE_DIR / "scripts" / "build_registry.py"
    if not script.exists():
        report.warn("scripts/build_registry.py not found — skipping freshness check")
        return

    # Check existence first
    missing = [a for a in REGISTRY_ARTIFACTS if not (BASE_DIR / a).exists()]
    if missing:
        for m in missing:
            report.error(
                f"{m} — registry artifact missing; run scripts/build_registry.py"
            )
        return

    # Snapshot current artifact hashes
    before = {a: file_md5(BASE_DIR / a) for a in REGISTRY_ARTIFACTS}

    # Re-run build into a tempdir (so we don't clobber a clean state mid-check)
    # Easier: run in place and snapshot after, then restore from `before` if needed.
    # For simplicity here: just re-run and compare.
    print("  (rebuilding registry to compare against committed artifacts…)")
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        report.error(
            "scripts/build_registry.py timed out (>30 min) — registry freshness UNKNOWN"
        )
        return
    if result.returncode != 0:
        report.error(
            f"scripts/build_registry.py failed (exit {result.returncode}). Stderr tail:\n{result.stderr[-1000:]}"
        )
        return

    drifted = []
    for a in REGISTRY_ARTIFACTS:
        after = file_md5(BASE_DIR / a)
        if before[a] != after:
            drifted.append(a)

    if drifted:
        report.error(
            f"Registry artifacts are stale ({len(drifted)} drifted): "
            + ", ".join(drifted)
            + ". `git add data/registry_* data/registry.json data/schema.json && git commit`"
        )
    else:
        report.note(
            f"All {len(REGISTRY_ARTIFACTS)} registry artifacts match a fresh rebuild"
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Skip the build_registry.py rebuild step (faster, but freshness not verified)",
    )
    ap.add_argument("--quiet", action="store_true", help="Only print summary")
    args = ap.parse_args()

    print(f"validate_release.py — auditing {BASE_DIR}")
    print()

    report = Report()
    print("• checking file formats…")
    check_file_formats(report)
    print("• checking large uncompressed CSVs…")
    check_large_uncompressed_csvs(report)
    print("• checking READMEs in /data/…")
    check_readmes(report)
    print("• checking registry artifact freshness…")
    check_registry_freshness(report, skip=args.no_rebuild)

    if not args.quiet:
        report.print()

    print()
    print(
        f"Summary: {len(report.errors)} errors, {len(report.warnings)} warnings, {len(report.info)} notes"
    )
    if report.has_errors:
        print("❌ FAIL — fix errors above before publishing.")
        sys.exit(1)
    else:
        print("✅ PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
