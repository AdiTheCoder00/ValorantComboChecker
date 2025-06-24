// Valorant Combo Checker - Frontend JavaScript
class ValorantComboChecker {
    constructor() {
        this.currentSessionId = null;
        this.isChecking = false;
        this.startTime = null;
        this.lastProgressUpdate = null;
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.initializeEventListeners();
        this.initializeTheme();
    }

    initializeEventListeners() {
        // Single check form
        document.getElementById('singleCheckForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.checkSingleAccount();
        });

        // File upload
        document.getElementById('comboFile').addEventListener('change', () => {
            this.handleFileSelect();
        });

        document.getElementById('uploadBtn').addEventListener('click', () => {
            this.uploadFile();
        });

        // Batch checking
        document.getElementById('startBatchBtn').addEventListener('click', () => {
            this.startBatchCheck();
        });

        document.getElementById('stopBatchBtn').addEventListener('click', () => {
            this.stopBatchCheck();
        });

        // Export results - handled by onclick in dropdown
        
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Initialize keyboard shortcuts
        this.initializeKeyboardShortcuts();
    }
    
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key.toLowerCase()) {
                    case 't':
                        e.preventDefault();
                        this.toggleTheme();
                        break;
                    case 'u':
                        e.preventDefault();
                        document.getElementById('comboFile').click();
                        break;
                    case 's':
                        e.preventDefault();
                        if (!this.isChecking) {
                            const startBtn = document.getElementById('startBatchBtn');
                            if (startBtn.style.display !== 'none') {
                                this.startBatchCheck();
                            }
                        }
                        break;
                    case 'x':
                        e.preventDefault();
                        if (this.isChecking) {
                            this.stopBatchCheck();
                        }
                        break;
                    case 'e':
                        e.preventDefault();
                        this.exportResults();
                        break;
                }
            }
        });
        
        // Show shortcuts help after a delay
        setTimeout(() => {
            this.showShortcutsHelp();
        }, 2000);
    }
    
    showShortcutsHelp() {
        const helpDiv = document.getElementById('shortcutsHelp');
        helpDiv.classList.add('show');
        
        setTimeout(() => {
            helpDiv.classList.remove('show');
        }, 4000);
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.showNotification(`Switched to ${this.currentTheme} theme`, 'success');
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeIcon = document.getElementById('themeIcon');
        if (theme === 'light') {
            themeIcon.className = 'fas fa-sun';
        } else {
            themeIcon.className = 'fas fa-moon';
        }
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer;">&times;</button>
            </div>
        `;
        
        const container = document.getElementById('notificationContainer');
        container.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-remove notification
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
    
    getNotificationIcon(type) {
        switch(type) {
            case 'success': return 'check-circle';
            case 'warning': return 'exclamation-triangle';
            case 'error': return 'times-circle';
            default: return 'info-circle';
        }
    }
    
    initializeTheme() {
        this.applyTheme(this.currentTheme);
    }

    async checkSingleAccount() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const submitBtn = document.querySelector('#singleCheckForm button[type="submit"]');
        const spinner = submitBtn.querySelector('.loading-spinner');
        const btnText = submitBtn.querySelector('.btn-text');

        if (!username || !password) {
            this.showAlert('Please enter both username and password', 'danger');
            return;
        }

        // Show loading state
        spinner.style.display = 'inline-block';
        btnText.textContent = 'Checking...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/check_single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();

            if (response.ok) {
                this.displaySingleResult(result);
            } else {
                this.showAlert(result.error || 'Check failed', 'danger');
            }
        } catch (error) {
            this.showAlert('Network error occurred', 'danger');
        } finally {
            // Reset button state
            spinner.style.display = 'none';
            btnText.textContent = 'Check Account';
            submitBtn.disabled = false;
        }
    }

    displaySingleResult(result) {
        const resultDiv = document.getElementById('singleResult');
        const timestamp = new Date(result.timestamp * 1000).toLocaleString();
        
        let statusClass = 'result-error';
        let statusIcon = 'fas fa-exclamation-triangle';
        let statusText = result.status.toUpperCase();

        if (result.status === 'valid') {
            statusClass = 'result-valid';
            statusIcon = 'fas fa-check-circle';
        } else if (result.status === 'invalid') {
            statusClass = 'result-invalid';
            statusIcon = 'fas fa-times-circle';
        }

        resultDiv.innerHTML = `
            <div class="result-item ${statusClass} fade-in">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6><i class="${statusIcon} me-2"></i>${statusText}</h6>
                        <p class="mb-1"><strong>Username:</strong> ${result.username}</p>
                        <p class="mb-1"><strong>Message:</strong> ${result.message}</p>
                        <p class="mb-0 text-muted small"><strong>Time:</strong> ${timestamp}</p>
                    </div>
                </div>
            </div>
        `;
        resultDiv.style.display = 'block';
    }

    handleFileSelect() {
        const fileInput = document.getElementById('comboFile');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (fileInput.files.length > 0) {
            uploadBtn.textContent = `Upload ${fileInput.files[0].name}`;
        } else {
            uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload File';
        }
    }

    async uploadFile() {
        const fileInput = document.getElementById('comboFile');
        const file = fileInput.files[0];

        if (!file) {
            this.showAlert('Please select a file first', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        const uploadBtn = document.getElementById('uploadBtn');
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';

        try {
            const response = await fetch('/api/upload_file', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                document.getElementById('fileInfo').style.display = 'block';
                document.getElementById('fileInfoText').textContent = 
                    `File uploaded: ${result.filename} (${result.combo_count} combinations found)`;
                
                document.getElementById('startBatchBtn').style.display = 'block';
                uploadBtn.style.display = 'none';
                
                this.showAlert(`File uploaded successfully! Found ${result.combo_count} combinations.`, 'success');
            } else {
                this.showAlert(result.error || 'Upload failed', 'danger');
            }
        } catch (error) {
            this.showAlert('Upload failed', 'danger');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload File';
        }
    }

    async startBatchCheck() {
        const delay = parseFloat(document.getElementById('delay').value);
        const maxWorkers = parseInt(document.getElementById('maxWorkers').value);
        
        if (delay < 2.0 || delay > 30) {
            this.showAlert('Delay must be between 2.0 and 30 seconds for optimal performance', 'warning');
            return;
        }
        
        if (maxWorkers < 1 || maxWorkers > 5) {
            this.showAlert('Workers must be between 1-5 for optimal rate limiting', 'warning');
            return;
        }

        const startBtn = document.getElementById('startBatchBtn');
        const stopBtn = document.getElementById('stopBatchBtn');
        const spinner = startBtn.querySelector('.loading-spinner');
        const btnText = startBtn.querySelector('.btn-text');

        // Show loading state
        spinner.style.display = 'inline-block';
        btnText.textContent = 'Starting...';
        startBtn.disabled = true;

        try {
            const response = await fetch('/api/start_batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ delay, max_workers: maxWorkers })
            });

            const result = await response.json();

            if (response.ok) {
                this.currentSessionId = result.session_id;
                this.isChecking = true;
                this.startTime = Date.now();
                this.lastProgressUpdate = 0;
                
                // Update UI
                startBtn.style.display = 'none';
                stopBtn.style.display = 'block';
                document.getElementById('batchProgress').style.display = 'block';
                document.getElementById('batchNotStarted').style.display = 'none';
                
                // Clear previous results
                document.getElementById('liveResults').innerHTML = '';
                
                // Start polling for updates
                this.pollBatchStatus();
                
                this.showNotification(`Batch check started! Processing ${result.total_combos} combinations with ${result.max_workers} concurrent threads.`, 'success');
            } else {
                this.showNotification(result.error || 'Failed to start batch check', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to start batch check', 'error');
        } finally {
            spinner.style.display = 'none';
            btnText.textContent = 'Start Batch Check';
            startBtn.disabled = false;
        }
    }

    async stopBatchCheck() {
        if (!this.currentSessionId) return;

        try {
            await fetch(`/api/stop_batch/${this.currentSessionId}`, {
                method: 'POST'
            });
            
            this.isChecking = false;
            this.updateBatchUI(false);
            this.showAlert('Batch check stopped', 'info');
        } catch (error) {
            this.showAlert('Failed to stop batch check', 'danger');
        }
    }

    async pollBatchStatus() {
        if (!this.isChecking || !this.currentSessionId) return;

        try {
            const response = await fetch(`/api/batch_status/${this.currentSessionId}`);
            const status = await response.json();

            if (response.ok) {
                this.updateBatchProgress(status);
                
                if (status.completed || !status.is_checking) {
                    this.isChecking = false;
                    this.updateBatchUI(false);
                    this.updateResultsSummary(status.results);
                    this.showAlert('Batch check completed!', 'success');
                } else {
                    // Continue polling
                    setTimeout(() => this.pollBatchStatus(), 1000);
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
            setTimeout(() => this.pollBatchStatus(), 2000);
        }
    }

    updateBatchProgress(status) {
        const progress = status.progress;
        const results = status.results || [];
        
        // Update progress bar
        const percentage = progress.total > 0 ? (progress.current / progress.total) * 100 : 0;
        document.getElementById('progressBar').style.width = `${percentage}%`;
        document.getElementById('progressText').textContent = `${progress.current}/${progress.total}`;
        
        // Update counters
        const validCount = results.filter(r => r.status === 'valid').length;
        const invalidCount = results.filter(r => r.status === 'invalid').length;
        const errorCount = results.length - validCount - invalidCount;
        
        document.getElementById('validCount').textContent = validCount;
        document.getElementById('invalidCount').textContent = invalidCount;
        document.getElementById('errorCount').textContent = errorCount;
        
        // Calculate and display checking rate per minute
        if (this.startTime && progress.current > 0) {
            const elapsedMinutes = (Date.now() - this.startTime) / 60000;
            const checksPerMinute = elapsedMinutes > 0 ? Math.round(progress.current / elapsedMinutes) : 0;
            document.getElementById('checkRate').textContent = checksPerMinute;
            
            // Show progress notifications at milestones
            const progressPercent = Math.round((progress.current / progress.total) * 100);
            if (progressPercent > 0 && progressPercent % 25 === 0 && !this.lastNotifiedProgress || this.lastNotifiedProgress !== progressPercent) {
                this.showNotification(`Progress: ${progressPercent}% complete (${progress.current}/${progress.total})`, 'info', 2000);
                this.lastNotifiedProgress = progressPercent;
            }
        }
        
        // Update live results
        this.updateLiveResults(results);
    }

    updateLiveResults(results) {
        const liveResults = document.getElementById('liveResults');
        
        // Only show last 10 results to avoid performance issues
        const recentResults = results.slice(-10);
        
        liveResults.innerHTML = recentResults.map(result => {
            const timestamp = new Date(result.timestamp * 1000).toLocaleTimeString();
            let statusClass = 'result-error';
            let statusIcon = 'fas fa-exclamation-triangle';
            
            if (result.status === 'valid') {
                statusClass = 'result-valid';
                statusIcon = 'fas fa-check-circle';
            } else if (result.status === 'invalid') {
                statusClass = 'result-invalid';
                statusIcon = 'fas fa-times-circle';
            }
            
            return `
                <div class="result-item ${statusClass} fade-in">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${result.username}</strong>
                            <span class="ms-2 text-muted">${result.message}</span>
                        </div>
                        <div class="text-end">
                            <i class="${statusIcon} me-2"></i>
                            <small class="text-muted">${timestamp}</small>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Auto-scroll to bottom
        liveResults.scrollTop = liveResults.scrollHeight;
    }

    updateBatchUI(isRunning) {
        const startBtn = document.getElementById('startBatchBtn');
        const stopBtn = document.getElementById('stopBatchBtn');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (isRunning) {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            uploadBtn.disabled = true;
        } else {
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            uploadBtn.disabled = false;
        }
    }

    updateResultsSummary(results) {
        if (!results || results.length === 0) return;
        
        const validResults = results.filter(r => r.status === 'valid');
        const invalidResults = results.filter(r => r.status === 'invalid');
        const errorResults = results.filter(r => r.status !== 'valid' && r.status !== 'invalid');
        
        // Update summary stats
        document.getElementById('totalChecked').textContent = results.length;
        document.getElementById('totalValid').textContent = validResults.length;
        document.getElementById('totalInvalid').textContent = invalidResults.length;
        document.getElementById('totalErrors').textContent = errorResults.length;
        
        // Show/hide sections
        document.getElementById('summaryStats').style.display = 'block';
        document.getElementById('noResults').style.display = 'none';
        document.getElementById('exportBtn').style.display = 'block';
        
        // Show valid accounts if any
        if (validResults.length > 0) {
            const validAccountsList = document.getElementById('validAccountsList');
            validAccountsList.innerHTML = validResults.map(result => 
                `<div class="result-item result-valid">
                    <strong>${result.username}:${result.password}</strong>
                    <span class="ms-2 text-muted">${result.message}</span>
                </div>`
            ).join('');
            document.getElementById('validAccounts').style.display = 'block';
        }
    }

    async exportResults() {
        if (!this.currentSessionId) {
            this.showNotification('No results to export', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/export_results/${this.currentSessionId}`);
            const data = await response.json();

            if (response.ok) {
                // Create and download file
                const content = this.formatExportData(data);
                const blob = new Blob([content], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = `valorant_results_${new Date().toISOString().split('T')[0]}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                window.URL.revokeObjectURL(url);
                this.showAlert('Results exported successfully!', 'success');
            } else {
                this.showAlert(data.error || 'Export failed', 'danger');
            }
        } catch (error) {
            this.showAlert('Export failed', 'danger');
        }
    }

    formatExportData(data) {
        const { summary, results } = data;
        let content = `Valorant Account Combo Check Results\n`;
        content += `${'='.repeat(50)}\n\n`;
        
        content += `Summary:\n`;
        content += `Total checked: ${summary.total}\n`;
        content += `Valid accounts: ${summary.valid}\n`;
        content += `Invalid accounts: ${summary.invalid}\n`;
        content += `Errors: ${summary.errors}\n\n`;
        
        if (summary.valid > 0) {
            content += `Valid Accounts:\n`;
            content += `${'-'.repeat(20)}\n`;
            results.filter(r => r.status === 'valid').forEach(result => {
                content += `${result.username}:${result.password}\n`;
            });
            content += `\n`;
        }
        
        content += `Detailed Results:\n`;
        content += `${'-'.repeat(30)}\n`;
        results.forEach(result => {
            const timestamp = new Date(result.timestamp * 1000).toLocaleString();
            content += `Username: ${result.username}\n`;
            content += `Status: ${result.status}\n`;
            content += `Message: ${result.message}\n`;
            content += `Time: ${timestamp}\n`;
            content += `${'-'.repeat(30)}\n`;
        });
        
        return content;
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ValorantComboChecker();
});