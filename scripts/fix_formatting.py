#!/usr/bin/env python3
"""
Fix formatting issues in Bible translation JSON files.

Issues fixed:
- :— → : — (colon-dash without space, NRT direct speech)
- .А → . А (no space after period before Cyrillic)
- ,а → , а (no space after comma before Cyrillic)
- ;А → ; А (no space after semicolon before Cyrillic)
- ?А → ? А (no space after question mark before Cyrillic)
- !А → ! А (no space after exclamation mark before Cyrillic)
"""

import json
import re
import os
from pathlib import Path

# Cyrillic letter pattern (uppercase and lowercase)
CYRILLIC = r'[А-Яа-яЁё]'

# Patterns to fix: (regex, replacement, description)
PATTERNS = [
    # Colon followed by em-dash without space
    (r':—', r': —', 'colon-dash'),
    # Punctuation followed by Cyrillic letter without space
    (rf'\.({CYRILLIC})', r'. \1', 'period'),
    (rf',({CYRILLIC})', r', \1', 'comma'),
    (rf';({CYRILLIC})', r'; \1', 'semicolon'),
    (rf'\?({CYRILLIC})', r'? \1', 'question'),
    (rf'!({CYRILLIC})', r'! \1', 'exclamation'),
]


def fix_text(text: str) -> tuple[str, dict]:
    """Fix formatting issues in text, return fixed text and stats."""
    stats = {}
    for pattern, replacement, name in PATTERNS:
        count = len(re.findall(pattern, text))
        if count > 0:
            text = re.sub(pattern, replacement, text)
            stats[name] = count
    return text, stats


def fix_json_file(filepath: Path) -> dict:
    """Fix formatting in a JSON file, return stats."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed_content, stats = fix_text(content)

    if stats:  # Only write if changes were made
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    return stats


def main():
    data_dir = Path(__file__).parent.parent / 'data'

    total_stats = {'synodal': {}, 'nrt': {}}

    # Fix main files
    for translation in ['synodal', 'nrt']:
        main_file = data_dir / f'{translation}.json'
        if main_file.exists():
            print(f"\nProcessing {main_file.name}...")
            stats = fix_json_file(main_file)
            for key, count in stats.items():
                total_stats[translation][key] = total_stats[translation].get(key, 0) + count
            print(f"  Fixed: {stats}")

    # Fix per-book files
    for translation in ['synodal', 'nrt']:
        book_dir = data_dir / translation
        if book_dir.exists():
            print(f"\nProcessing {translation}/ directory...")
            for book_file in sorted(book_dir.glob('*.json')):
                stats = fix_json_file(book_file)
                for key, count in stats.items():
                    total_stats[translation][key] = total_stats[translation].get(key, 0) + count
                if stats:
                    print(f"  {book_file.name}: {stats}")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    grand_total = 0
    for translation, stats in total_stats.items():
        if stats:
            total = sum(stats.values())
            grand_total += total
            print(f"\n{translation.upper()}: {total} fixes")
            for issue, count in sorted(stats.items(), key=lambda x: -x[1]):
                print(f"  {issue}: {count}")

    print(f"\nGRAND TOTAL: {grand_total} fixes applied")


if __name__ == '__main__':
    main()
