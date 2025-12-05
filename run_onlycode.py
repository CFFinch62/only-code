#!/usr/bin/env python3
"""
Only Code Editor - Entry Point for PyInstaller
This script serves as the main entry point when running the packaged application.
"""

import sys
import os

# Ensure the application can find its resources when frozen
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
    # Add the path to sys.path for imports
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Import and run the application
from onlycode.app.application import OnlyCodeApp


def main():
    app = OnlyCodeApp()
    app.run()


if __name__ == "__main__":
    main()

