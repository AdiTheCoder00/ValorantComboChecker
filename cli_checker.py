#!/usr/bin/env python3
"""
Valorant Account Combo Checker - Command Line Interface
Simple shell-based version for checking account combinations

DISCLAIMER: This tool is for educational purposes only.
Only use this tool on accounts you own or have explicit permission to test.
Unauthorized access to accounts is illegal and violates terms of service.
"""

import sys
import time
import os
import tkinter as tk
from tkinter import filedialog
from combo_checker import ComboChecker
from utils import validate_email, format_duration

def show_disclaimer():
    """Show disclaimer and get user consent"""
    print("\n" + "="*60)
    print("VALORANT ACCOUNT COMBO CHECKER")
    print("="*60)
    print("\nIMPORTANT DISCLAIMER:")
    print("This tool is for educational and legitimate testing purposes only.")
    print("\nBy using this application, you agree that you will:")
    print("• Only test accounts that you own or have explicit written permission to test")
    print("• Not attempt to gain unauthorized access to any accounts")
    print("• Comply with all applicable laws and terms of service")
    print("• Take full responsibility for your usage of this tool")
    print("\nUnauthorized access to computer systems is illegal and may result in criminal prosecution.")
    print("\n" + "="*60)
    
    while True:
        response = input("\nDo you agree to use this tool responsibly and legally? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def single_check():
    """Check a single account"""
    print("\n" + "-"*40)
    print("SINGLE ACCOUNT CHECK")
    print("-"*40)
    
    username = input("Enter username/email: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return
        
    password = input("Enter password: ").strip()
    if not password:
        print("Error: Password cannot be empty")
        return
    
    print(f"\nChecking account: {username}")
    print("Please wait...")
    
    checker = ComboChecker()
    result = checker.check_single_combo(username, password)
    
    print(f"\nResult for {username}:")
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))}")
    
    return result

def select_file():
    """Open file browser to select combo file"""
    print("Opening file browser... (a small window will appear)")
    
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring to front
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select your combo file",
        filetypes=[
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"), 
            ("All files", "*.*")
        ],
        initialdir=os.getcwd()
    )
    
    root.destroy()  # Clean up
    return file_path

def batch_check():
    """Check multiple accounts from file"""
    print("\n" + "-"*40)
    print("BATCH ACCOUNT CHECK")
    print("-"*40)
    
    print("Choose how to select your combo file:")
    print("1. Browse with file explorer (recommended)")
    print("2. Type file path manually")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        file_path = select_file()
        if not file_path:
            print("No file selected. Returning to main menu.")
            return
    elif choice == "2":
        file_path = input("Enter path to combo file: ").strip()
        if not file_path:
            print("Error: File path cannot be empty")
            return
    else:
        print("Invalid choice. Returning to main menu.")
        return
        
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return
    
    print(f"Selected file: {os.path.basename(file_path)}")
    
    try:
        checker = ComboChecker()
        combos = checker.parse_combo_file(file_path)
        
        if not combos:
            print("Error: No valid combos found in file")
            return
            
        print(f"\nFound {len(combos)} combo(s) to check")
        
        # Get delay setting
        while True:
            try:
                delay = float(input(f"Enter delay between checks in seconds (default 2.0): ").strip() or "2.0")
                if delay < 0.1:
                    print("Delay must be at least 0.1 seconds")
                    continue
                break
            except ValueError:
                print("Please enter a valid number")
        
        estimated_time = format_duration(len(combos) * delay)
        print(f"Estimated time: {estimated_time}")
        
        confirm = input("\nProceed with batch check? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Batch check cancelled")
            return
        
        checker.delay = delay
        results = []
        
        print(f"\nStarting batch check...")
        print("-" * 50)
        
        for i, (username, password) in enumerate(combos, 1):
            print(f"[{i}/{len(combos)}] Checking {username}...", end=" ")
            
            result = checker.check_single_combo(username, password)
            results.append(result)
            
            # Display result
            status_display = result['status'].upper()
            if result['status'] == 'valid':
                print(f"✓ {status_display}")
            elif result['status'] == 'invalid':
                print(f"✗ {status_display}")
            else:
                print(f"! {status_display} - {result['message']}")
            
            # Apply delay (except for last item)
            if i < len(combos):
                time.sleep(delay)
        
        # Show summary
        print("\n" + "="*50)
        print("BATCH CHECK COMPLETE")
        print("="*50)
        
        valid_count = sum(1 for r in results if r['status'] == 'valid')
        invalid_count = sum(1 for r in results if r['status'] == 'invalid')
        error_count = len(results) - valid_count - invalid_count
        
        print(f"Total checked: {len(results)}")
        print(f"Valid accounts: {valid_count}")
        print(f"Invalid accounts: {invalid_count}")
        print(f"Errors: {error_count}")
        
        # Show valid accounts
        if valid_count > 0:
            print(f"\nVALID ACCOUNTS:")
            print("-" * 20)
            for result in results:
                if result['status'] == 'valid':
                    print(f"{result['username']}:{result['password']}")
        
        # Ask to export results
        if results:
            export = input(f"\nExport results to file? (yes/no): ").strip().lower()
            if export in ['yes', 'y']:
                export_results(results)
                
        return results
        
    except Exception as e:
        print(f"Error during batch check: {e}")
        return None

def save_file_dialog():
    """Open save file dialog"""
    print("Opening save dialog... (a small window will appear)")
    
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring to front
    
    # Open save dialog
    file_path = filedialog.asksaveasfilename(
        title="Save results as...",
        defaultextension=".txt",
        filetypes=[
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ],
        initialdir=os.getcwd(),
        initialfile="valorant_results.txt"
    )
    
    root.destroy()  # Clean up
    return file_path

def export_results(results):
    """Export results to file"""
    if not results:
        print("No results to export")
        return
    
    print("Choose how to save your results:")
    print("1. Browse with file explorer (recommended)")
    print("2. Type filename manually")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        filename = save_file_dialog()
        if not filename:
            print("Save cancelled.")
            return
    elif choice == "2":
        filename = input("Enter filename (default: valorant_results.txt): ").strip()
        if not filename:
            filename = "valorant_results.txt"
    else:
        print("Invalid choice.")
        return
    
    # Determine file format from extension
    file_format = 'csv' if filename.lower().endswith('.csv') else 'txt'
    
    try:
        checker = ComboChecker()
        checker.export_results(results, filename, file_format)
        print(f"Results exported to: {filename}")
        print(f"Format: {file_format.upper()}")
    except Exception as e:
        print(f"Error exporting results: {e}")

def main_menu():
    """Display main menu and handle user input"""
    while True:
        print("\n" + "="*40)
        print("VALORANT COMBO CHECKER - MAIN MENU")
        print("="*40)
        print("1. Single Account Check")
        print("2. Batch Account Check")
        print("3. Exit")
        print("-"*40)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            single_check()
        elif choice == '2':
            batch_check()
        elif choice == '3':
            print("\nExiting... Stay safe!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Main application entry point"""
    try:
        # Show disclaimer
        if not show_disclaimer():
            print("Application terminated. Goodbye!")
            sys.exit(0)
        
        # Run main menu
        main_menu()
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()