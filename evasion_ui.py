"""
Evasion UI Components
Advanced user interface for monitoring and controlling evasion features
"""

def get_evasion_dashboard_html():
    """Return HTML for evasion monitoring dashboard"""
    return '''
    <div class="card mb-4" id="evasionDashboard" style="display: none;">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
                <i class="fas fa-shield-alt me-2"></i>Advanced Evasion Status
            </h5>
            <button class="btn btn-sm btn-outline-light" onclick="toggleEvasionDetails()">
                <i class="fas fa-eye" id="evasionToggleIcon"></i>
            </button>
        </div>
        <div class="card-body" id="evasionDetails" style="display: none;">
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-muted">Current Fingerprint</h6>
                    <div id="currentFingerprint" class="mb-3">
                        <div class="small">
                            <strong>User Agent:</strong> <span id="fpUserAgent">Not initialized</span><br>
                            <strong>Platform:</strong> <span id="fpPlatform">Unknown</span><br>
                            <strong>Resolution:</strong> <span id="fpResolution">Unknown</span>
                        </div>
                    </div>
                    
                    <h6 class="text-muted">Request Statistics</h6>
                    <div class="small">
                        <strong>Total Requests:</strong> <span id="totalRequests">0</span><br>
                        <strong>Fingerprint Rotations:</strong> <span id="fpRotations">0</span><br>
                        <strong>Success Rate:</strong> <span id="evasionSuccessRate">0%</span>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <h6 class="text-muted">Evasion Metrics</h6>
                    <div id="evasionMetrics">
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" role="progressbar" id="httpSuccessBar" style="width: 0%"></div>
                        </div>
                        <div class="small text-muted">HTTP Success Rate</div>
                    </div>
                    
                    <div class="mt-3">
                        <h6 class="text-muted">Status Codes</h6>
                        <div id="statusCodes" class="small">
                            <span class="badge bg-success me-1">200: <span id="status200">0</span></span>
                            <span class="badge bg-warning me-1">429: <span id="status429">0</span></span>
                            <span class="badge bg-danger me-1">Error: <span id="statusError">0</span></span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <h6 class="text-muted">Evasion Timeline</h6>
                    <div id="evasionTimeline" style="height: 100px; background: #1a1a1a; border-radius: 5px; position: relative; overflow: hidden;">
                        <!-- Timeline visualization will be rendered here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''

def get_evasion_controls_html():
    """Return HTML for evasion control panel"""
    return '''
    <div class="card mb-3" id="evasionControls">
        <div class="card-header">
            <h6 class="mb-0">
                <i class="fas fa-cogs me-2"></i>Evasion Controls
            </h6>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">Fingerprint Rotation</label>
                    <select class="form-select form-select-sm" id="fpRotationMode">
                        <option value="auto">Auto (every 25 requests)</option>
                        <option value="aggressive">Aggressive (every 10 requests)</option>
                        <option value="conservative">Conservative (every 50 requests)</option>
                        <option value="manual">Manual only</option>
                    </select>
                </div>
                
                <div class="col-md-4">
                    <label class="form-label">Behavior Simulation</label>
                    <select class="form-select form-select-sm" id="behaviorMode">
                        <option value="human">Human-like patterns</option>
                        <option value="fast">Fast but safe</option>
                        <option value="stealth">Maximum stealth</option>
                    </select>
                </div>
                
                <div class="col-md-4">
                    <label class="form-label">Manual Controls</label>
                    <div>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="rotateFingerprint()">
                            <i class="fas fa-sync-alt"></i> Rotate Now
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="resetEvasionStats()">
                            <i class="fas fa-chart-line"></i> Reset Stats
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''

def get_evasion_js():
    """Return JavaScript for evasion UI functionality"""
    return '''
    // Evasion UI Management
    let evasionTimelineData = [];
    let evasionChart = null;
    
    function toggleEvasionDetails() {
        const details = document.getElementById('evasionDetails');
        const icon = document.getElementById('evasionToggleIcon');
        
        if (details.style.display === 'none') {
            details.style.display = 'block';
            icon.className = 'fas fa-eye-slash';
        } else {
            details.style.display = 'none';
            icon.className = 'fas fa-eye';
        }
    }
    
    function updateEvasionDashboard(evasionData) {
        if (!evasionData) return;
        
        // Update fingerprint info
        if (evasionData.current_fingerprint) {
            const fp = evasionData.current_fingerprint;
            document.getElementById('fpUserAgent').textContent = 
                fp.user_agent ? fp.user_agent.substring(0, 60) + '...' : 'Not set';
            document.getElementById('fpPlatform').textContent = fp.platform || 'Unknown';
            document.getElementById('fpResolution').textContent = 
                fp.resolution ? `${fp.resolution[0]}x${fp.resolution[1]}` : 'Unknown';
        }
        
        // Update request statistics
        document.getElementById('totalRequests').textContent = evasionData.request_count || 0;
        document.getElementById('fpRotations').textContent = evasionData.fingerprint_rotations || 0;
        
        // Update metrics
        if (evasionData.evasion_metrics && evasionData.evasion_metrics.status_codes) {
            const codes = evasionData.evasion_metrics.status_codes;
            const total = Object.values(codes).reduce((a, b) => a + b, 0);
            
            document.getElementById('status200').textContent = codes['200'] || 0;
            document.getElementById('status429').textContent = codes['429'] || 0;
            document.getElementById('statusError').textContent = 
                (codes['0'] || 0) + (codes['500'] || 0) + (codes['503'] || 0);
            
            // Calculate success rate
            const successRate = total > 0 ? ((codes['200'] || 0) / total * 100).toFixed(1) : 0;
            document.getElementById('evasionSuccessRate').textContent = successRate + '%';
            document.getElementById('httpSuccessBar').style.width = successRate + '%';
        }
        
        // Update timeline
        updateEvasionTimeline(evasionData);
    }
    
    function updateEvasionTimeline(evasionData) {
        const timeline = document.getElementById('evasionTimeline');
        const now = Date.now();
        
        // Add new data point
        evasionTimelineData.push({
            timestamp: now,
            requests: evasionData.request_count || 0,
            rotations: evasionData.fingerprint_rotations || 0,
            status: evasionData.evasion_metrics ? 'active' : 'inactive'
        });
        
        // Keep only last 50 data points
        if (evasionTimelineData.length > 50) {
            evasionTimelineData.shift();
        }
        
        // Simple visualization
        renderEvasionTimeline();
    }
    
    function renderEvasionTimeline() {
        const timeline = document.getElementById('evasionTimeline');
        timeline.innerHTML = '';
        
        if (evasionTimelineData.length < 2) return;
        
        const width = timeline.offsetWidth;
        const height = timeline.offsetHeight;
        const maxRequests = Math.max(...evasionTimelineData.map(d => d.requests), 1);
        
        // Create SVG
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.position = 'absolute';
        
        // Draw request count line
        let path = 'M ';
        evasionTimelineData.forEach((point, index) => {
            const x = (index / (evasionTimelineData.length - 1)) * width;
            const y = height - (point.requests / maxRequests) * height;
            path += `${x},${y} `;
        });
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        line.setAttribute('d', path);
        line.setAttribute('stroke', '#00ff88');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('fill', 'none');
        
        svg.appendChild(line);
        
        // Mark fingerprint rotations
        evasionTimelineData.forEach((point, index) => {
            if (point.rotations > (evasionTimelineData[index - 1]?.rotations || 0)) {
                const x = (index / (evasionTimelineData.length - 1)) * width;
                const marker = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                marker.setAttribute('cx', x);
                marker.setAttribute('cy', 10);
                marker.setAttribute('r', 3);
                marker.setAttribute('fill', '#ff6b35');
                svg.appendChild(marker);
            }
        });
        
        timeline.appendChild(svg);
    }
    
    function rotateFingerprint() {
        // This would trigger a fingerprint rotation
        fetch('/api/rotate_fingerprint', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Fingerprint rotated successfully', 'success');
                } else {
                    showNotification('Failed to rotate fingerprint', 'error');
                }
            });
    }
    
    function resetEvasionStats() {
        evasionTimelineData = [];
        document.getElementById('evasionTimeline').innerHTML = '';
        showNotification('Evasion statistics reset', 'info');
    }
    
    // Show evasion dashboard during batch checking
    function showEvasionDashboard() {
        document.getElementById('evasionDashboard').style.display = 'block';
    }
    
    function hideEvasionDashboard() {
        document.getElementById('evasionDashboard').style.display = 'none';
    }
    '''