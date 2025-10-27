#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files and directories considered non-essential for the playable game
DELETE_FILES = [
    'BRANDING_GUIDE.md',
    'CLEANUP_SUMMARY.md',
    'CODEWARS_ADAPTATION_PLAN.md',
    'COMPETITION_STRATEGY.md',
    'COMPLETE_CHECKLIST.md',
    'GAME_ANALYSIS.md',
    'INTEGRATION_GUIDE.py',
    'PITCH_GUIDE.md',
    'QUICK_START.md',
    'RELEASE_NOTES.md',
    'STAGE2_COMPLETE.md',
    'SUBMISSION_README.md',
    'THEME_ADAPTATION_PLAN.md',
    'demo_features.py',
    'invisible_system.py',
    'memory_manager.py',
    'theme_systems.py',  # root copy, Stage 2 uses local module under stage 2/code
    'DPS_rohini.exe',
    '.DS_Store',
]

DELETE_DIRS = [
    '__pycache__',
    'tiled-maps',
    'venv',
    str(Path('stage 2')/ 'code' / '__pycache__'),
]

# Always keep these
SAFE_KEEP = {
    'README.md',
    'TROUBLESHOOTING.md',
    'requirements.txt',
    'main.py',
    'start_screen.py',
    'fonts',
    'hearts',
    'stage 1',
    'stage 2',
    '.gitignore',
    '.vscode',
}


def remove_path(p: Path, apply: bool):
    if not p.exists():
        return False, 'missing'
    if apply:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return True, 'deleted'
    else:
        return True, 'would-delete'


def main():
    parser = argparse.ArgumentParser(description='Clean non-essential files from repo.')
    parser.add_argument('--apply', action='store_true', help='Actually delete files (default is dry-run)')
    args = parser.parse_args()

    print(f"Repo root: {ROOT}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}\n")

    removed = []

    for rel in DELETE_FILES:
        p = ROOT / rel
        ok, status = remove_path(p, args.apply)
        print(f"FILE  {rel:<35} -> {status}")
        if ok and args.apply and status == 'deleted':
            removed.append(rel)

    for rel in DELETE_DIRS:
        p = ROOT / rel
        ok, status = remove_path(p, args.apply)
        print(f"DIR   {rel:<35} -> {status}")
        if ok and args.apply and status == 'deleted':
            removed.append(rel + '/')

    # Safety print: show that we keep the core game files
    print('\nKept (not touched):')
    for item in sorted(SAFE_KEEP):
        print(f"  - {item}")

    if not args.apply:
        print('\nDry-run only. Re-run with --apply to delete listed items.')

if __name__ == '__main__':
    main()
