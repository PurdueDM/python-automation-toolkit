"""
Smart File Organizer — GridGuard AI Python Automation Toolkit

Sorts files in a directory by type or by date into organized subfolders.
Supports dry-run mode to preview changes before committing.

Usage:
    python -m toolkit.file_organizer --source FOLDER --mode type
    python -m toolkit.file_organizer --source FOLDER --mode date --dry-run
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from typing import List, Tuple

CATEGORY_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".rtf", ".tex"},
    "Text": {".txt", ".md", ".csv", ".tsv", ".log", ".rst", ".yaml", ".yml", ".toml", ".ini", ".cfg"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".rb", ".php", ".sh", ".bat", ".ps1", ".sql", ".html", ".css", ".jsx", ".tsx", ".vue", ".swift", ".kt"},
    "Data": {".json", ".xml", ".jsonl", ".parquet", ".feather", ".hdf5", ".sqlite", ".db"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz", ".tgz"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "Video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
    "Executables": {".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".appimage"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2", ".eot"},
}


def get_category(ext):
    # type: (str) -> str
    ext = ext.lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return "Other"


def get_date_folder(filepath):
    # type: (str) -> str
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime)
    return dt.strftime("%Y-%m")


def _resolve_collision(dest_path):
    # type: (str) -> str
    """If dest_path exists, append a counter to the filename."""
    if not os.path.exists(dest_path):
        return dest_path

    base, ext = os.path.splitext(dest_path)
    counter = 1
    while os.path.exists("{}_{}{}".format(base, counter, ext)):
        counter += 1
    return "{}_{}{}".format(base, counter, ext)


def organize_by_type(source, dry_run=False):
    # type: (str, bool) -> List[Tuple[str, str]]
    """Sort files into subfolders by file type category."""
    source = os.path.abspath(source)
    moves = []  # type: List[Tuple[str, str]]

    for entry in os.scandir(source):
        if not entry.is_file():
            continue

        ext = os.path.splitext(entry.name)[1]
        category = get_category(ext) if ext else "Other"

        dest_dir = os.path.join(source, category)
        dest_path = os.path.join(dest_dir, entry.name)

        if os.path.abspath(entry.path) == os.path.abspath(dest_path):
            continue

        dest_path = _resolve_collision(dest_path)
        moves.append((entry.path, dest_path))

        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(entry.path, dest_path)

    return moves


def organize_by_date(source, dry_run=False):
    # type: (str, bool) -> List[Tuple[str, str]]
    """Sort files into subfolders by last-modified month (YYYY-MM)."""
    source = os.path.abspath(source)
    moves = []  # type: List[Tuple[str, str]]

    for entry in os.scandir(source):
        if not entry.is_file():
            continue

        date_folder = get_date_folder(entry.path)
        dest_dir = os.path.join(source, date_folder)
        dest_path = os.path.join(dest_dir, entry.name)

        if os.path.abspath(entry.path) == os.path.abspath(dest_path):
            continue

        dest_path = _resolve_collision(dest_path)
        moves.append((entry.path, dest_path))

        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(entry.path, dest_path)

    return moves


def print_plan(moves, dry_run):
    # type: (List[Tuple[str, str]], bool) -> None
    prefix = "[DRY RUN] " if dry_run else ""
    if not moves:
        print("{}No files to organize.".format(prefix))
        return

    for src, dst in moves:
        src_name = os.path.basename(src)
        dst_folder = os.path.basename(os.path.dirname(dst))
        print("{}{} -> {}/".format(prefix, src_name, dst_folder))

    action = "would be" if dry_run else ""
    print("\n{}{} file(s) {} organized.".format(prefix, len(moves), action))


def main():
    parser = argparse.ArgumentParser(
        description="Smart file organizer -- sort files by type or date."
    )
    parser.add_argument("--source", required=True, help="Source directory to organize")
    parser.add_argument("--mode", choices=["type", "date"], default="type",
                        help="Organize by file type or by date (default: type)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without moving files")

    args = parser.parse_args()

    source = os.path.abspath(args.source)
    if not os.path.isdir(source):
        print("Error: '{}' is not a valid directory.".format(source))
        sys.exit(1)

    print("[organizer] Scanning: {}".format(source))
    print("[organizer] Mode: {}".format(args.mode))
    if args.dry_run:
        print("[organizer] DRY RUN -- no files will be moved\n")

    if args.mode == "type":
        moves = organize_by_type(source, dry_run=args.dry_run)
    else:
        moves = organize_by_date(source, dry_run=args.dry_run)

    print_plan(moves, args.dry_run)


if __name__ == "__main__":
    main()
