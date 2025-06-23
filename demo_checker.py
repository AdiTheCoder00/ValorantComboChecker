#!/usr/bin/env python3
"""
Valorant Account Combo Checker - Demo Version
Demonstrates the functionality without requiring interactive input
"""

import time
from combo_checker import ComboChecker

def demo_single_check():
    """Demonstrate single account checking"""
    print("="*60)
    print("VALORANT COMBO CHECKER - DEMO")
    print("="*60)
    print("\nDISCLAIMER: Educational purposes only. Only test accounts you own.")
    print("\nDemonstrating single account check...")
    
    # Demo credentials (these are fake for demonstration)
    test_username = "demo_user@example.com"
    test_password = "demo_password123"
    
    print(f"\nChecking account: {test_username}")
    print("Please wait...")
    
    checker = ComboChecker()
    result = checker.check_single_combo(test_username, test_password)
    
    print(f"\nResult:")
    print(f"Username: {result['username']}")
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))}")
    
    return result

def demo_batch_check():
    """Demonstrate batch checking with sample file"""
    print("\n" + "-"*60)
    print("BATCH CHECK DEMO")
    print("-"*60)
    
    sample_file = "sample_combos.txt"
    print(f"Loading combos from: {sample_file}")
    
    try:
        checker = ComboChecker()
        combos = checker.parse_combo_file(sample_file)
        
        print(f"Found {len(combos)} combo(s) to check")
        print("Starting batch check with 1 second delay...")
        print("-" * 50)
        
        checker.delay = 1.0  # 1 second delay for demo
        results = []
        
        for i, (username, password) in enumerate(combos, 1):
            print(f"[{i}/{len(combos)}] Checking {username}...", end=" ")
            
            result = checker.check_single_combo(username, password)
            results.append(result)
            
            # Display result with color coding
            if result['status'] == 'valid':
                print("✓ VALID")
            elif result['status'] == 'invalid':
                print("✗ INVALID")
            else:
                print(f"! {result['status'].upper()} - {result['message']}")
            
            time.sleep(1)  # Demo delay
        
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
        
        # Show valid accounts (if any)
        if valid_count > 0:
            print(f"\nVALID ACCOUNTS:")
            print("-" * 20)
            for result in results:
                if result['status'] == 'valid':
                    print(f"{result['username']}:{result['password']}")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main demo function"""
    print("Starting Valorant Combo Checker Demo...")
    
    # Demo single check
    demo_single_check()
    
    # Demo batch check
    demo_batch_check()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nTo use the interactive version, run: python cli_checker.py")
    print("To use the GUI version, run: python main.py")

if __name__ == "__main__":
    main()