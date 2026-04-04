#!/usr/bin/env python3
"""Add or fix `slug` metadata in post frontmatter.

The slug value is always the post directory name.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "posts"


@dataclass
class Change:
    file_path: Path
    action: str
    old_slug: str | None
    new_slug: str


def split_frontmatter(content: str) -> tuple[str, str, str] | None:
    """Return (frontmatter_with_markers, frontmatter_body, rest_content)."""
    match = re.match(r"^(---\n)(.*?)(\n---\n)(.*)$", content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1) + match.group(2) + match.group(3)
    body = match.group(2)
    rest = match.group(4)
    return frontmatter, body, rest


def upsert_slug(frontmatter_body: str, slug: str) -> tuple[str, str, str | None]:
    """Upsert slug in frontmatter body.

    Returns:
        (new_frontmatter_body, action, old_slug)
    """
    slug_pattern = re.compile(r"^slug:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
    existing = slug_pattern.search(frontmatter_body)

    if existing:
        old_slug = existing.group(1).strip()
        if old_slug == slug:
            return frontmatter_body, "unchanged", old_slug

        replaced = slug_pattern.sub(f'slug: "{slug}"', frontmatter_body, count=1)
        return replaced, "updated", old_slug

    lines = frontmatter_body.split("\n")

    insert_after = 0
    for i, line in enumerate(lines):
        if line.startswith("title:"):
            insert_after = i + 1
            break

    lines.insert(insert_after, f'slug: "{slug}"')
    return "\n".join(lines), "added", None


def process_post(index_file: Path, dry_run: bool) -> tuple[Change | None, bool]:
    slug = index_file.parent.name
    content = index_file.read_text(encoding="utf-8")

    split = split_frontmatter(content)
    if not split:
        return None, False

    original_frontmatter, frontmatter_body, rest = split
    new_body, action, old_slug = upsert_slug(frontmatter_body, slug)
    if action == "unchanged":
        return None, True

    new_content = f"---\n{new_body}\n---\n{rest}"
    if not dry_run:
        index_file.write_text(new_content, encoding="utf-8")

    return Change(index_file, action, old_slug, slug), True


def find_post_index_files() -> list[Path]:
    index_files: list[Path] = []
    for category_dir in sorted(POSTS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for post_dir in sorted(category_dir.iterdir()):
            if not post_dir.is_dir():
                continue
            index_file = post_dir / "index.md"
            if index_file.exists():
                index_files.append(index_file)
    return index_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add or fix slug metadata in blog post frontmatter."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without writing files.",
    )
    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"[ERROR] posts directory not found: {POSTS_DIR}")
        return 1

    index_files = find_post_index_files()
    if not index_files:
        print("No posts found.")
        return 0

    changes: list[Change] = []
    skipped_no_frontmatter = 0

    for index_file in index_files:
        try:
            result, has_frontmatter = process_post(index_file, dry_run=args.dry_run)
            if result:
                changes.append(result)
            if not has_frontmatter:
                skipped_no_frontmatter += 1
        except UnicodeDecodeError:
            print(f"[SKIP] Cannot decode file as UTF-8: {index_file}")
            continue
        except Exception as exc:
            print(f"[ERROR] Failed to process {index_file}: {exc}")
            continue

    if not changes:
        print("No slug changes needed.")
    else:
        for change in changes:
            rel = change.file_path.relative_to(POSTS_DIR.parent)
            if change.action == "added":
                print(f'[ADD] {rel} -> slug: "{change.new_slug}"')
            else:
                print(
                    f'[UPDATE] {rel} -> slug: "{change.old_slug}" to "{change.new_slug}"'
                )

        print()
        mode = "DRY RUN" if args.dry_run else "APPLIED"
        print(f"{mode}: {len(changes)} file(s) changed.")

    if skipped_no_frontmatter:
        print(f"Skipped {skipped_no_frontmatter} file(s) without frontmatter.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
