#!/usr/bin/env python3
"""
Valorant Account Combo Checker
Main entry point for the application

DISCLAIMER: This tool is for educational purposes only.
Only use this tool on accounts you own or have explicit permission to test.
Unauthorized access to accounts is illegal and violates terms of service.
"""

import sys
import tkinter as tk
from tkinter import messagebox
import logging
from gui import ComboCheckerGUI

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('combo_checker.log'),
            logging.StreamHandler()
        ]
    )

def show_disclaimer():
    """Show disclaimer dialog"""
    disclaimer_text = """
IMPORTANT DISCLAIMER

This tool is for educational and legitimate testing purposes only.

By using this application, you agree that you will:
• Only test accounts that you own or have explicit written permission to test
• Not attempt to gain unauthorized access to any accounts
• Comply with all applicable laws and terms of service
• Take full responsibility for your usage of this tool

Unauthorized access to computer systems is illegal and may result in criminal prosecution.

Do you agree to use this tool responsibly and legally?
    """
    
    result = messagebox.askyesno("Legal Disclaimer", disclaimer_text.strip())
    return result

def main():
    """Main application entry point"""
    setup_logging()
    
    # Show disclaimer
    if not show_disclaimer():
        print("Application terminated by user.")
        sys.exit(0)
    
    try:
        # Create and run the GUI
        root = tk.Tk()
        app = ComboCheckerGUI(root)
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
