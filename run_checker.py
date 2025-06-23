#!/usr/bin/env python3
"""
Simple launcher for the Valorant Combo Checker
"""

import subprocess
import sys
import os

def main():
    print("Starting Valorant Combo Checker...")
    print("Note: This will open an interactive session.")
    print("Press Ctrl+C to exit at any time.\n")
    
    try:
        # Run the CLI checker with proper terminal handling
        result = subprocess.run([sys.executable, "cli_checker.py"], 
                              stdin=sys.stdin, 
                              stdout=sys.stdout, 
                              stderr=sys.stderr)
        
        if result.returncode != 0:
            print(f"\nChecker exited with code: {result.returncode}")
    
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")
    except Exception as e:
        print(f"\nError running checker: {e}")

if __name__ == "__main__":
    main()