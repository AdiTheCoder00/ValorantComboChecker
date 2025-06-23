"""
GUI interface for the Valorant Combo Checker
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
from typing import List, Dict
from combo_checker import ComboChecker
from config import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE,
    SUPPORTED_FILE_TYPES, EXPORT_FORMATS,
    DEFAULT_DELAY_BETWEEN_CHECKS, MIN_DELAY, MAX_DELAY
)

class ComboCheckerGUI:
    """Main GUI class for the combo checker"""
    
    def __init__(self, root):
        self.root = root
        self.combo_checker = ComboChecker()
        self.results = []
        self.checking_thread = None
        
        self.setup_gui()
        self.setup_variables()
        
    def setup_variables(self):
        """Initialize GUI variables"""
        self.delay_var = tk.DoubleVar(value=DEFAULT_DELAY_BETWEEN_CHECKS)
        self.progress_var = tk.IntVar()
        self.status_var = tk.StringVar(value="Ready")
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*WINDOW_MIN_SIZE)
        
        # Create main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Single check tab
        self.create_single_check_tab(notebook)
        
        # Batch check tab
        self.create_batch_check_tab(notebook)
        
        # Results tab
        self.create_results_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
        
        # Status bar
        self.create_status_bar()
        
    def create_single_check_tab(self, parent):
        """Create single account check tab"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Single Check")
        
        # Main frame
        main_frame = ttk.LabelFrame(frame, text="Single Account Check", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Username/Email field
        ttk.Label(main_frame, text="Username/Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.single_username_entry = ttk.Entry(main_frame, width=40)
        self.single_username_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Password field
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.single_password_entry = ttk.Entry(main_frame, width=40, show="*")
        self.single_password_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Check button
        self.single_check_btn = ttk.Button(main_frame, text="Check Account", 
                                          command=self.check_single_account)
        self.single_check_btn.grid(row=2, column=1, sticky=tk.E, pady=10)
        
        # Result display
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding=10)
        result_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        self.single_result_text = scrolledtext.ScrolledText(result_frame, height=10, width=60)
        self.single_result_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        
    def create_batch_check_tab(self, parent):
        """Create batch check tab"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Batch Check")
        
        # File selection frame
        file_frame = ttk.LabelFrame(frame, text="Combo File", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(file_frame, text="Browse", command=self.browse_combo_file).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Control frame
        control_frame = ttk.LabelFrame(frame, text="Batch Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Progress bar
        ttk.Label(control_frame, text="Progress:").pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_batch_btn = ttk.Button(btn_frame, text="Start Batch Check", 
                                         command=self.start_batch_check)
        self.start_batch_btn.pack(side=tk.LEFT)
        
        self.stop_batch_btn = ttk.Button(btn_frame, text="Stop Check", 
                                        command=self.stop_batch_check, state=tk.DISABLED)
        self.stop_batch_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(btn_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.RIGHT)
        
        # Live results frame
        results_frame = ttk.LabelFrame(frame, text="Live Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results treeview
        columns = ("Username", "Status", "Message", "Time")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_results_tab(self, parent):
        """Create results summary tab"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Results Summary")
        
        # Summary frame
        summary_frame = ttk.LabelFrame(frame, text="Summary Statistics", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=8, width=60)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Detailed results frame
        details_frame = ttk.LabelFrame(frame, text="Detailed Results", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
    def create_settings_tab(self, parent):
        """Create settings tab"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Settings")
        
        settings_frame = ttk.LabelFrame(frame, text="Check Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Delay setting
        ttk.Label(settings_frame, text="Delay between checks (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5)
        delay_spinbox = ttk.Spinbox(settings_frame, from_=MIN_DELAY, to=MAX_DELAY, 
                                   increment=0.1, textvariable=self.delay_var, width=10)
        delay_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Apply button
        ttk.Button(settings_frame, text="Apply Settings", 
                  command=self.apply_settings).grid(row=1, column=1, sticky=tk.E, pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(frame, text="Usage Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = """
Usage Instructions:

1. Single Check: Enter username/email and password, then click "Check Account"

2. Batch Check: 
   - Prepare a text file with combos in format: username:password (one per line)
   - Supported separators: : , ; or tab
   - Lines starting with # are ignored as comments
   - Click "Browse" to select your combo file
   - Click "Start Batch Check" to begin

3. Results can be exported as TXT or CSV files

4. Adjust delay between checks to avoid rate limiting

IMPORTANT: Only use this tool on accounts you own or have permission to test.
Unauthorized access attempts are illegal and against terms of service.
        """
        
        info_display = tk.Text(info_frame, wrap=tk.WORD, height=15)
        info_display.insert(tk.END, info_text.strip())
        info_display.config(state=tk.DISABLED)
        info_display.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)
        
    def check_single_account(self):
        """Check a single account"""
        username = self.single_username_entry.get().strip()
        password = self.single_password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        self.single_check_btn.config(state=tk.DISABLED)
        self.status_var.set("Checking account...")
        
        def check_thread():
            try:
                result = self.combo_checker.check_single_combo(username, password)
                
                # Display result
                self.root.after(0, lambda: self.display_single_result(result))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Check failed: {e}"))
            finally:
                self.root.after(0, lambda: self.single_check_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_var.set("Ready"))
                
        threading.Thread(target=check_thread, daemon=True).start()
        
    def display_single_result(self, result):
        """Display single check result"""
        self.single_result_text.delete(1.0, tk.END)
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))
        
        result_text = f"""
Check Result for: {result['username']}
Status: {result['status'].upper()}
Message: {result['message']}
Time: {timestamp}

Details:
- Username/Email: {result['username']}
- Password: {'*' * len(result['password'])}
- Result: {result['status']}
- Additional Info: {result['message']}
        """
        
        self.single_result_text.insert(tk.END, result_text.strip())
        
        # Color coding
        if result['status'] == 'valid':
            self.single_result_text.config(fg='green')
        elif result['status'] == 'invalid':
            self.single_result_text.config(fg='red')
        else:
            self.single_result_text.config(fg='orange')
            
    def browse_combo_file(self):
        """Browse for combo file"""
        file_path = filedialog.askopenfilename(
            title="Select Combo File",
            filetypes=SUPPORTED_FILE_TYPES
        )
        if file_path:
            self.file_path_var.set(file_path)
            
    def start_batch_check(self):
        """Start batch checking process"""
        file_path = self.file_path_var.get().strip()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid combo file")
            return
            
        try:
            # Parse combo file
            combos = self.combo_checker.parse_combo_file(file_path)
            if not combos:
                messagebox.showerror("Error", "No valid combos found in file")
                return
                
            total_combos = len(combos)
            result = messagebox.askyesno("Confirm", 
                                       f"Found {total_combos} combo(s) to check.\n"
                                       f"This will take approximately {total_combos * self.delay_var.get():.1f} seconds.\n\n"
                                       "Do you want to continue?")
            if not result:
                return
                
            # Clear previous results
            self.results.clear()
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
                
            # Update UI state
            self.start_batch_btn.config(state=tk.DISABLED)
            self.stop_batch_btn.config(state=tk.NORMAL)
            self.progress_var.set(0)
            self.progress_bar.config(maximum=total_combos)
            
            # Start checking thread
            self.checking_thread = threading.Thread(
                target=self.batch_check_worker,
                args=(combos,),
                daemon=True
            )
            self.checking_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start batch check: {e}")
            
    def batch_check_worker(self, combos):
        """Worker thread for batch checking"""
        try:
            self.combo_checker.delay = self.delay_var.get()
            
            def progress_callback(current, total):
                progress = int((current / total) * 100)
                self.root.after(0, lambda: self.progress_var.set(current))
                self.root.after(0, lambda: self.status_var.set(f"Checking {current}/{total}..."))
                
            def result_callback(result):
                self.results.append(result)
                self.root.after(0, lambda: self.add_result_to_tree(result))
                
            # Check combos
            self.combo_checker.check_combo_list(
                combos,
                progress_callback=progress_callback,
                result_callback=result_callback
            )
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Batch check failed: {e}"))
        finally:
            # Reset UI state
            self.root.after(0, lambda: self.start_batch_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_batch_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Batch check completed"))
            self.root.after(0, lambda: self.update_results_summary())
            
    def add_result_to_tree(self, result):
        """Add result to the results tree"""
        timestamp = time.strftime('%H:%M:%S', time.localtime(result['timestamp']))
        
        # Determine row color based on status
        tags = []
        if result['status'] == 'valid':
            tags = ['valid']
        elif result['status'] == 'invalid':
            tags = ['invalid']
        else:
            tags = ['error']
            
        self.results_tree.insert('', tk.END, values=(
            result['username'],
            result['status'],
            result['message'],
            timestamp
        ), tags=tags)
        
        # Configure tag colors
        self.results_tree.tag_configure('valid', foreground='green')
        self.results_tree.tag_configure('invalid', foreground='red')
        self.results_tree.tag_configure('error', foreground='orange')
        
        # Auto-scroll to bottom
        children = self.results_tree.get_children()
        if children:
            self.results_tree.see(children[-1])
            
    def stop_batch_check(self):
        """Stop the current batch check"""
        self.combo_checker.stop_checking_process()
        self.stop_batch_btn.config(state=tk.DISABLED)
        self.status_var.set("Stopping batch check...")
        
    def export_results(self):
        """Export results to file"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            filetypes=EXPORT_FORMATS,
            defaultextension=".txt"
        )
        
        if file_path:
            try:
                format_type = 'csv' if file_path.lower().endswith('.csv') else 'txt'
                self.combo_checker.export_results(self.results, file_path, format_type)
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
                
    def apply_settings(self):
        """Apply settings changes"""
        try:
            delay = self.delay_var.get()
            if MIN_DELAY <= delay <= MAX_DELAY:
                self.combo_checker.delay = delay
                messagebox.showinfo("Success", "Settings applied successfully")
            else:
                messagebox.showerror("Error", f"Delay must be between {MIN_DELAY} and {MAX_DELAY} seconds")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
            
    def update_results_summary(self):
        """Update the results summary tab"""
        if not self.results:
            return
            
        # Calculate statistics
        total = len(self.results)
        valid = sum(1 for r in self.results if r['status'] == 'valid')
        invalid = sum(1 for r in self.results if r['status'] == 'invalid')
        errors = total - valid - invalid
        
        # Update summary
        summary = f"""
Batch Check Summary
==================

Total Accounts Checked: {total}
Valid Accounts: {valid} ({valid/total*100:.1f}%)
Invalid Accounts: {invalid} ({invalid/total*100:.1f}%)
Errors/Timeouts: {errors} ({errors/total*100:.1f}%)

Check Duration: {time.strftime('%H:%M:%S', time.gmtime(sum(1 for r in self.results)))}
Average Check Time: {self.delay_var.get():.1f} seconds per account
        """
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary.strip())
        
        # Update detailed results
        self.details_text.delete(1.0, tk.END)
        
        if valid > 0:
            self.details_text.insert(tk.END, "VALID ACCOUNTS:\n")
            self.details_text.insert(tk.END, "=" * 50 + "\n")
            for result in self.results:
                if result['status'] == 'valid':
                    self.details_text.insert(tk.END, f"{result['username']}:{result['password']}\n")
            self.details_text.insert(tk.END, "\n")
            
        if errors > 0:
            self.details_text.insert(tk.END, "ERRORS/ISSUES:\n")
            self.details_text.insert(tk.END, "=" * 50 + "\n")
            for result in self.results:
                if result['status'] not in ['valid', 'invalid']:
                    self.details_text.insert(tk.END, f"{result['username']}: {result['message']}\n")
