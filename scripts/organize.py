#!/usr/bin/env python3
"""
Blog content organization scripts.
Automatically categorize and validate blog posts.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

POSTS_DIR = Path(__file__).parent.parent / "posts"

def extract_date_from_frontmatter(md_file: Path) -> Optional[datetime]:
    """Extract date from markdown frontmatter."""
    try:
        content = md_file.read_text(encoding='utf-8')
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            return None
        
        fm_text = fm_match.group(1)
        # Match date field with various formats
        date_match = re.search(r'^date:\s*(.+)$', fm_text, re.MULTILINE)
        if not date_match:
            return None
        
        date_str = date_match.group(1).strip().strip('"\'')
        
        # Try ISO 8601 with timezone
        for fmt in [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]:
            try:
                # Handle +08:00 format (need to remove colon in timezone)
                if '+' in date_str and ':' in date_str.split('+')[-1]:
                    date_str_fixed = re.sub(r'\+(\d{2}):(\d{2})$', r'+\1\2', date_str)
                    return datetime.strptime(date_str_fixed, fmt)
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    except Exception as e:
        print(f"  Error reading {md_file}: {e}")
        return None


def organize_by_year():
    """
    Organize posts into year directories based on their frontmatter date.
    Moves posts from wrong year directories to correct ones.
    """
    print("=" * 60)
    print("Organizing posts by year...")
    print("=" * 60)
    
    # Find all posts (excluding weekly)
    year_dirs = [d for d in POSTS_DIR.iterdir() 
                 if d.is_dir() and d.name.isdigit()]
    
    moves = []
    
    for year_dir in sorted(year_dirs):
        for post_dir in year_dir.iterdir():
            if not post_dir.is_dir():
                continue
            
            index_file = post_dir / "index.md"
            if not index_file.exists():
                print(f"  [WARN] No index.md in {post_dir.relative_to(POSTS_DIR)}")
                continue
            
            date = extract_date_from_frontmatter(index_file)
            if not date:
                print(f"  [WARN] Cannot parse date in {post_dir.relative_to(POSTS_DIR)}")
                continue
            
            correct_year = str(date.year)
            current_year = year_dir.name
            
            if correct_year != current_year:
                moves.append({
                    'post_dir': post_dir,
                    'slug': post_dir.name,
                    'current_year': current_year,
                    'correct_year': correct_year,
                    'date': date,
                })
    
    if not moves:
        print("\n✓ All posts are in correct year directories!")
        return
    
    print(f"\nFound {len(moves)} posts in wrong year directories:\n")
    
    for move in moves:
        print(f"  {move['slug']}")
        print(f"    Date: {move['date'].strftime('%Y-%m-%d')}")
        print(f"    {move['current_year']} → {move['correct_year']}")
        print()
    
    # Perform moves
    response = input("Move these posts to correct directories? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    for move in moves:
        target_year_dir = POSTS_DIR / move['correct_year']
        target_year_dir.mkdir(exist_ok=True)
        target_path = target_year_dir / move['slug']
        
        if target_path.exists():
            print(f"  [ERROR] Target already exists: {target_path}")
            continue
        
        shutil.move(str(move['post_dir']), str(target_path))
        print(f"  Moved: {move['slug']} → {move['correct_year']}/")
    
    # Clean up empty year directories
    for year_dir in year_dirs:
        if year_dir.exists() and not any(year_dir.iterdir()):
            year_dir.rmdir()
            print(f"  Removed empty directory: {year_dir.name}/")
    
    print("\n✓ Organization complete!")


def validate_posts():
    """
    Validate all posts for common issues.
    """
    print("=" * 60)
    print("Validating posts...")
    print("=" * 60)
    
    issues = []
    
    # Check all directories
    for category_dir in POSTS_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        for post_dir in category_dir.iterdir():
            if not post_dir.is_dir():
                continue
            
            rel_path = post_dir.relative_to(POSTS_DIR)
            index_file = post_dir / "index.md"
            
            # Check index.md exists
            if not index_file.exists():
                issues.append(f"[MISSING] {rel_path}: No index.md")
                continue
            
            content = index_file.read_text(encoding='utf-8')
            
            # Check frontmatter exists
            if not content.startswith('---'):
                issues.append(f"[FORMAT] {rel_path}: Missing frontmatter")
                continue
            
            fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not fm_match:
                issues.append(f"[FORMAT] {rel_path}: Invalid frontmatter")
                continue
            
            fm_text = fm_match.group(1)
            
            # Check required fields
            if 'title:' not in fm_text:
                issues.append(f"[FIELD] {rel_path}: Missing title")
            
            if 'date:' not in fm_text:
                issues.append(f"[FIELD] {rel_path}: Missing date")
            
            # Check cover image exists if specified
            cover_match = re.search(r'^cover:\s*["\']?\.\/([^"\']+)["\']?', fm_text, re.MULTILINE)
            if cover_match:
                cover_file = post_dir / cover_match.group(1)
                if not cover_file.exists():
                    issues.append(f"[ASSET] {rel_path}: Cover not found: {cover_match.group(1)}")
    
    if not issues:
        print("\n✓ All posts are valid!")
    else:
        print(f"\nFound {len(issues)} issues:\n")
        for issue in issues:
            print(f"  {issue}")
    
    return len(issues) == 0


def list_stats():
    """Print statistics about the blog posts."""
    print("=" * 60)
    print("Blog Statistics")
    print("=" * 60)
    
    stats = {}
    total = 0
    
    for category_dir in sorted(POSTS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        count = sum(1 for p in category_dir.iterdir() 
                   if p.is_dir() and (p / "index.md").exists())
        stats[category_dir.name] = count
        total += count
    
    print(f"\n{'Category':<20} {'Count':>10}")
    print("-" * 32)
    
    for category, count in stats.items():
        print(f"{category:<20} {count:>10}")
    
    print("-" * 32)
    print(f"{'Total':<20} {total:>10}")
    print()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python organize.py <command>")
        print()
        print("Commands:")
        print("  organize  - Move posts to correct year directories")
        print("  validate  - Check all posts for issues")
        print("  stats     - Show blog statistics")
        print("  all       - Run all checks")
        return
    
    command = sys.argv[1]
    
    if command == 'organize':
        organize_by_year()
    elif command == 'validate':
        validate_posts()
    elif command == 'stats':
        list_stats()
    elif command == 'all':
        list_stats()
        print()
        validate_posts()
        print()
        organize_by_year()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
