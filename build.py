#!/usr/bin/env python3
"""
Only Code Editor - Build Script
Cross-platform build system using PyInstaller.

Usage:
    python build.py              # Build for current platform
    python build.py --clean      # Clean build artifacts
    python build.py --onefile    # Build single executable
    python build.py --package    # Build and create distributable archive
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path

# Application info
APP_NAME = 'OnlyCode'
APP_VERSION = '0.6.0'

# Directories
ROOT_DIR = Path(__file__).parent.absolute()
DIST_DIR = ROOT_DIR / 'dist'
BUILD_DIR = ROOT_DIR / 'build'
SPEC_FILE = ROOT_DIR / 'onlycode.spec'


def get_platform():
    """Get current platform name."""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'


def clean():
    """Remove build artifacts."""
    print("Cleaning build artifacts...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_path}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"  Removed {SPEC_FILE}")
    print("Clean complete.")


def check_dependencies():
    """Check that required build dependencies are installed."""
    print("Checking dependencies...")
    # Map display name to import name
    required = {'PyInstaller': 'PyInstaller', 'textual': 'textual'}
    missing = []
    for display_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(display_name)
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + ' '.join(missing))
        return False
    print("All dependencies found.")
    return True


def build(onefile=False):
    """Build the application."""
    platform = get_platform()
    print(f"\n{'='*50}")
    print(f"Building Only Code for {platform}")
    print(f"{'='*50}\n")

    if not check_dependencies():
        sys.exit(1)

    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--name', APP_NAME,
        '--add-data', f'onlycode:onlycode',
        '--hidden-import', 'onlycode',
        '--hidden-import', 'onlycode.app',
        '--hidden-import', 'onlycode.app.application',
        '--hidden-import', 'onlycode.app.screens',
        '--hidden-import', 'onlycode.app.widgets',
        '--hidden-import', 'onlycode.editor',
        '--hidden-import', 'textual',
        '--hidden-import', 'tree_sitter',
        '--collect-all', 'textual',
        '--collect-all', 'tree_sitter',
        # Tree-sitter language packages for syntax highlighting
        '--collect-all', 'tree_sitter_python',
        '--collect-all', 'tree_sitter_javascript',
        '--collect-all', 'tree_sitter_html',
        '--collect-all', 'tree_sitter_css',
        '--collect-all', 'tree_sitter_json',
        '--collect-all', 'tree_sitter_yaml',
        '--collect-all', 'tree_sitter_toml',
        '--collect-all', 'tree_sitter_markdown',
        '--collect-all', 'tree_sitter_rust',
        '--collect-all', 'tree_sitter_go',
        '--collect-all', 'tree_sitter_bash',
        '--collect-all', 'tree_sitter_sql',
        '--collect-all', 'tree_sitter_java',
        '--collect-all', 'tree_sitter_xml',
        '--collect-all', 'tree_sitter_regex',
    ]

    if onefile:
        cmd.append('--onefile')

    # TUI app - always use console
    cmd.append('--console')
    cmd.append('run_onlycode.py')

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=ROOT_DIR)

    if result.returncode != 0:
        print("\nBuild failed!")
        sys.exit(1)

    # Post-build info
    print(f"\n{'='*50}")
    print("Build complete!")
    print(f"{'='*50}")

    if onefile:
        if platform == 'windows':
            output = DIST_DIR / f'{APP_NAME}.exe'
        else:
            output = DIST_DIR / APP_NAME
        if output.exists():
            print(f"\nOutput: {output}")
            print(f"Size: {output.stat().st_size / (1024*1024):.1f} MB")
            print(f"\nTo run: {output}")
    else:
        output_dir = DIST_DIR / APP_NAME
        if output_dir.exists():
            print(f"\nOutput: {output_dir}")
            total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
            print(f"Size: {total_size / (1024*1024):.1f} MB")
            if platform == 'windows':
                print(f"\nTo run: {output_dir / f'{APP_NAME}.exe'}")
            else:
                print(f"\nTo run: {output_dir / APP_NAME}")

    return DIST_DIR


def package(onefile=False):
    """Create distributable archive from built application."""
    import tarfile
    import zipfile

    platform = get_platform()

    print(f"\n{'='*50}")
    print(f"Packaging Only Code for {platform}")
    print(f"{'='*50}\n")

    # Determine what to package
    if onefile:
        if platform == 'windows':
            source = DIST_DIR / f'{APP_NAME}.exe'
        else:
            source = DIST_DIR / APP_NAME
    else:
        source = DIST_DIR / APP_NAME

    if not source.exists():
        print(f"Error: {source} not found. Run build first.")
        sys.exit(1)

    # Create archive name with version and platform
    archive_base = f'{APP_NAME}-{APP_VERSION}-{platform}'

    if platform == 'linux':
        archive_path = DIST_DIR / f'{archive_base}.tar.gz'
        print(f"Creating {archive_path.name}...")
        with tarfile.open(archive_path, 'w:gz') as tar:
            if onefile:
                tar.add(source, arcname=source.name)
            else:
                tar.add(source, arcname=APP_NAME)
    else:  # windows or macos
        archive_path = DIST_DIR / f'{archive_base}.zip'
        print(f"Creating {archive_path.name}...")
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if onefile:
                zf.write(source, source.name)
            else:
                for file in source.rglob('*'):
                    if file.is_file():
                        arcname = Path(APP_NAME) / file.relative_to(source)
                        zf.write(file, arcname)

    archive_size = archive_path.stat().st_size / (1024 * 1024)
    print(f"\nPackage created: {archive_path}")
    print(f"Size: {archive_size:.1f} MB")

    return archive_path


def main():
    parser = argparse.ArgumentParser(description='Build Only Code Editor')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--onefile', action='store_true', help='Build single executable')
    parser.add_argument('--package', action='store_true', help='Create distributable archive after build')

    args = parser.parse_args()

    if args.clean:
        clean()
        if not args.onefile and not args.package:
            return

    build(onefile=args.onefile)

    if args.package:
        package(onefile=args.onefile)


if __name__ == '__main__':
    main()

