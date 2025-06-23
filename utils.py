"""
Utility functions for the Valorant Combo Checker
"""

import re
import hashlib
import os
import json
from typing import List, Dict, Optional, Tuple
import logging

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str, min_length: int = 8) -> Tuple[bool, List[str]]:
    """
    Validate password strength
    
    Args:
        password: Password string to validate
        min_length: Minimum password length
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if len(password) < min_length:
        issues.append(f"Password must be at least {min_length} characters long")
        
    if not re.search(r'[A-Z]', password):
        issues.append("Password should contain at least one uppercase letter")
        
    if not re.search(r'[a-z]', password):
        issues.append("Password should contain at least one lowercase letter")
        
    if not re.search(r'[0-9]', password):
        issues.append("Password should contain at least one digit")
        
    return len(issues) == 0, issues

def hash_password(password: str) -> str:
    """
    Create a hash of the password for logging purposes
    
    Args:
        password: Password to hash
        
    Returns:
        SHA256 hash of the password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def sanitize_username(username: str) -> str:
    """
    Sanitize username for safe logging
    
    Args:
        username: Username to sanitize
        
    Returns:
        Sanitized username
    """
    # Remove any potentially harmful characters
    sanitized = re.sub(r'[^\w@.\-]', '', username)
    return sanitized

def parse_combo_line(line: str) -> Optional[Tuple[str, str]]:
    """
    Parse a single combo line into username and password
    
    Args:
        line: Line to parse
        
    Returns:
        Tuple of (username, password) or None if invalid
    """
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None
        
    # Try different separators
    separators = [':', ',', ';', '\t', '|']
    
    for sep in separators:
        if sep in line:
            parts = line.split(sep, 1)
            if len(parts) == 2:
                username = parts[0].strip()
                password = parts[1].strip()
                
                if username and password:
                    return (sanitize_username(username), password)
                    
    return None

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def estimate_check_time(combo_count: int, delay_per_check: float) -> str:
    """
    Estimate total time for checking combos
    
    Args:
        combo_count: Number of combos to check
        delay_per_check: Delay between each check in seconds
        
    Returns:
        Estimated time string
    """
    total_seconds = combo_count * delay_per_check
    return format_duration(total_seconds)

def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename with timestamp
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup filename
    """
    import time
    
    base, ext = os.path.splitext(original_path)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return f"{base}_backup_{timestamp}{ext}"

def safe_file_write(file_path: str, content: str, create_backup: bool = True) -> bool:
    """
    Safely write content to file with optional backup
    
    Args:
        file_path: Path to write to
        content: Content to write
        create_backup: Whether to create backup if file exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create backup if file exists
        if create_backup and os.path.exists(file_path):
            backup_path = create_backup_filename(file_path)
            import shutil
            shutil.copy2(file_path, backup_path)
            
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
        
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {e}")
        return False

def load_config(config_path: str) -> Dict:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    default_config = {
        'delay_between_checks': 2.0,
        'max_retries': 3,
        'request_timeout': 30,
        'log_level': 'INFO'
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                default_config.update(config)
                
    except Exception as e:
        logging.warning(f"Failed to load config from {config_path}: {e}")
        
    return default_config

def save_config(config: Dict, config_path: str) -> bool:
    """
    Save configuration to JSON file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save config
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
        
    except Exception as e:
        logging.error(f"Failed to save config to {config_path}: {e}")
        return False

def clean_log_files(log_dir: str = '.', max_age_days: int = 7) -> None:
    """
    Clean old log files
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days
    """
    import time
    
    try:
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(log_dir, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    logging.info(f"Removed old log file: {filename}")
                    
    except Exception as e:
        logging.error(f"Failed to clean log files: {e}")

def get_user_data_dir() -> str:
    """
    Get user data directory for storing app data
    
    Returns:
        Path to user data directory
    """
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        data_dir = os.path.join(os.getenv('APPDATA', ''), 'ValorantComboChecker')
    elif system == "Darwin":  # macOS
        data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'ValorantComboChecker')
    else:  # Linux and others
        data_dir = os.path.join(os.path.expanduser('~'), '.valorant_combo_checker')
        
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    return data_dir

class ResultsFormatter:
    """Class for formatting check results in various formats"""
    
    @staticmethod
    def format_as_text(results: List[Dict], include_invalid: bool = False) -> str:
        """Format results as plain text"""
        output = []
        output.append("Valorant Account Check Results")
        output.append("=" * 50)
        output.append("")
        
        # Summary
        total = len(results)
        valid = sum(1 for r in results if r['status'] == 'valid')
        invalid = sum(1 for r in results if r['status'] == 'invalid')
        errors = total - valid - invalid
        
        output.append("SUMMARY:")
        output.append(f"Total checked: {total}")
        output.append(f"Valid accounts: {valid}")
        output.append(f"Invalid accounts: {invalid}")
        output.append(f"Errors: {errors}")
        output.append("")
        
        # Valid accounts
        if valid > 0:
            output.append("VALID ACCOUNTS:")
            output.append("-" * 20)
            for result in results:
                if result['status'] == 'valid':
                    output.append(f"{result['username']}:{result['password']}")
            output.append("")
            
        # Invalid accounts (if requested)
        if include_invalid and invalid > 0:
            output.append("INVALID ACCOUNTS:")
            output.append("-" * 20)
            for result in results:
                if result['status'] == 'invalid':
                    output.append(f"{result['username']} - {result['message']}")
            output.append("")
            
        # Errors
        if errors > 0:
            output.append("ERRORS:")
            output.append("-" * 20)
            for result in results:
                if result['status'] not in ['valid', 'invalid']:
                    output.append(f"{result['username']} - {result['message']}")
                    
        return "\n".join(output)
    
    @staticmethod
    def format_as_json(results: List[Dict]) -> str:
        """Format results as JSON"""
        return json.dumps(results, indent=2, default=str)
    
    @staticmethod
    def format_valid_only(results: List[Dict]) -> str:
        """Format only valid results in username:password format"""
        valid_results = []
        for result in results:
            if result['status'] == 'valid':
                valid_results.append(f"{result['username']}:{result['password']}")
        return "\n".join(valid_results)
