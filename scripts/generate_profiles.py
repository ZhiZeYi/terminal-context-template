#!/usr/bin/env python3
"""
Generate profile.json from template-source fragments.

This script scans the template-source directory for JSON fragment files,
validates them, and merges them into the final templates/profile.json file.

Usage:
    python generate_profiles.py           # Generate profile.json
    python generate_profiles.py --validate # Validate fragments only
    python generate_profiles.py --dry-run  # Preview without writing
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Paths relative to script location
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATE_SOURCE_DIR = PROJECT_ROOT / "template-source"
OUTPUT_FILE = PROJECT_ROOT / "templates" / "profile.json"


def load_fragment(file_path: Path) -> Optional[Dict]:
    """Load and validate a single fragment file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Basic validation
        required_fields = ["id", "name", "description", "category", "variables"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            print(f"  [ERROR] {file_path.name}: Missing required fields: {missing}")
            return None
        
        # Validate id matches filename
        expected_id = file_path.stem
        if data["id"] != expected_id:
            print(f"  [WARN]  {file_path.name}: id '{data['id']}' doesn't match filename")
        
        return data
    except json.JSONDecodeError as e:
        print(f"  [ERROR] {file_path.name}: Invalid JSON - {e}")
        return None
    except Exception as e:
        print(f"  [ERROR] {file_path.name}: Error - {e}")
        return None


def collect_fragments() -> List[Dict]:
    """Collect all valid fragment files from template-source directory."""
    fragments = []
    
    if not TEMPLATE_SOURCE_DIR.exists():
        print(f"[ERROR] Template source directory not found: {TEMPLATE_SOURCE_DIR}")
        return fragments
    
    # Get all JSON files except those starting with underscore
    json_files = sorted([
        f for f in TEMPLATE_SOURCE_DIR.glob("*.json")
        if not f.name.startswith("_")
    ])
    
    print(f"[DIR] Scanning {TEMPLATE_SOURCE_DIR}")
    print(f"   Found {len(json_files)} fragment files\n")
    
    for file_path in json_files:
        fragment = load_fragment(file_path)
        if fragment:
            fragments.append(fragment)
            print(f"  [OK] {file_path.name}: {fragment['name']}")
    
    return fragments


def sort_fragments(fragments: List[Dict]) -> List[Dict]:
    """Sort fragments by category, then by id."""
    # Define category order
    category_order = [
        "Development",
        "AI", 
        "Cloud",
        "DevOps",
        "Database",
        "Network",
        "CI/CD"
    ]
    
    def sort_key(f):
        category = f.get("category", "ZZZ")
        try:
            cat_index = category_order.index(category)
        except ValueError:
            cat_index = len(category_order)
        return (cat_index, f.get("id", ""))
    
    return sorted(fragments, key=sort_key)


def generate_profile(fragments: List[Dict]) -> Dict:
    """Generate the final profile.json structure."""
    return {
        "version": "1.0.0",
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "author": "TCM Community",
        "description": "Terminal Context Manager - Profile Templates & Environment Variables Dictionary",
        "repository": "https://github.com/ZhiZeYi/terminal-context-template",
        "templates": fragments
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate profile.json from template-source fragments"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate fragments only, don't generate output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview output without writing to file"
    )
    args = parser.parse_args()
    
    print("=" * 50)
    print("TCM Profile Generator")
    print("=" * 50 + "\n")
    
    # Collect and validate fragments
    fragments = collect_fragments()
    
    if not fragments:
        print("\n[ERROR] No valid fragments found!")
        sys.exit(1)
    
    print(f"\n[SUMMARY] {len(fragments)} valid fragments\n")
    
    if args.validate:
        print("[OK] Validation complete")
        sys.exit(0)
    
    # Sort fragments
    sorted_fragments = sort_fragments(fragments)
    
    # Generate profile
    profile = generate_profile(sorted_fragments)
    
    # Output
    output_json = json.dumps(profile, indent=2, ensure_ascii=False)
    
    if args.dry_run:
        print("[DRY-RUN] Would generate:\n")
        print(f"   Output: {OUTPUT_FILE}")
        print(f"   Templates: {len(sorted_fragments)}")
        print(f"   Size: {len(output_json)} bytes")
        print("\n--- Preview (first 500 chars) ---")
        print(output_json[:500] + "..." if len(output_json) > 500 else output_json)
    else:
        # Ensure output directory exists
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write(output_json)
            f.write("\n")
        
        print(f"[OK] Generated: {OUTPUT_FILE}")
        print(f"   Templates: {len(sorted_fragments)}")
        print(f"   Size: {len(output_json)} bytes")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
