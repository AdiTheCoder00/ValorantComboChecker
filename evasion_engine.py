"""
Advanced Evasion Engine for Valorant Combo Checker
Comprehensive anti-detection and stealth capabilities
"""

import random
import time
import json
import base64
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

@dataclass
class BrowserFingerprint:
    """Comprehensive browser fingerprint data"""
    user_agent: str
    viewport: Tuple[int, int]
    screen_resolution: Tuple[int, int]
    timezone: str
    language: str
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    audio_fingerprint: str
    fonts: List[str]
    plugins: List[str]
    webrtc_ip: str
    
class AdvancedEvasionEngine:
    """Advanced evasion and anti-detection system"""
    
    def __init__(self):
        self.current_fingerprint = None
        self.session_history = []
        self.behavior_patterns = self._load_behavior_patterns()
        self.proxy_pool = []
        self.user_agent_pool = self._load_user_agents()
        
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent pool"""
        return [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Firefox macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # Edge Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            
            # Safari macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
    
    def _load_behavior_patterns(self) -> Dict:
        """Load realistic human behavior patterns"""
        return {
            'typing_speeds': {
                'slow': (0.15, 0.25),      # 150-250ms between keystrokes
                'medium': (0.08, 0.15),    # 80-150ms
                'fast': (0.05, 0.08),      # 50-80ms
                'variable': True           # Vary speed within session
            },
            'mouse_movements': {
                'jitter_range': (1, 3),    # Pixel jitter range
                'pause_probability': 0.15,  # 15% chance to pause
                'pause_duration': (0.5, 1.5)  # 0.5-1.5 second pauses
            },
            'request_timing': {
                'base_delay': (1.0, 3.0),      # Base delay between requests
                'human_variation': (0.5, 2.0),  # Random human-like variation
                'think_time': (2.0, 8.0),      # Time to "think" between actions
                'break_probability': 0.05,      # 5% chance for longer break
                'break_duration': (30, 120)     # 30s-2min breaks
            }
        }
    
    def generate_fingerprint(self) -> BrowserFingerprint:
        """Generate a realistic browser fingerprint"""
        
        # Select base platform and derive consistent data
        platforms = [
            {
                'platform': 'Win32',
                'os': 'Windows NT 10.0; Win64; x64',
                'resolutions': [(1920, 1080), (2560, 1440), (1366, 768), (1536, 864)],
                'timezones': ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']
            },
            {
                'platform': 'MacIntel', 
                'os': 'Macintosh; Intel Mac OS X 10_15_7',
                'resolutions': [(2560, 1600), (1440, 900), (1920, 1080)],
                'timezones': ['America/New_York', 'America/Los_Angeles', 'America/Chicago']
            }
        ]
        
        platform_data = random.choice(platforms)
        resolution = random.choice(platform_data['resolutions'])
        
        # Generate consistent viewport (slightly smaller than screen)
        viewport = (
            resolution[0] - random.randint(0, 100),
            resolution[1] - random.randint(100, 200)
        )
        
        # WebGL data based on platform
        webgl_vendors = ["Google Inc.", "Mozilla", "WebKit"]
        webgl_renderers = [
            "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            "Apple GPU"
        ]
        
        # Generate canvas fingerprint (simplified)
        canvas_data = f"{resolution[0]}x{resolution[1]}_{random.randint(1000, 9999)}"
        canvas_fingerprint = hashlib.md5(canvas_data.encode()).hexdigest()[:16]
        
        # Audio context fingerprint
        audio_data = f"audio_{random.randint(100, 999)}_{platform_data['platform']}"
        audio_fingerprint = hashlib.md5(audio_data.encode()).hexdigest()[:12]
        
        # Common fonts based on platform
        windows_fonts = [
            "Arial", "Calibri", "Cambria", "Consolas", "Georgia", "Impact", 
            "Lucida Console", "Palatino Linotype", "Segoe UI", "Tahoma", 
            "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        
        mac_fonts = [
            "Arial", "Helvetica", "Times", "Courier", "Verdana", "Georgia",
            "Palatino", "Times New Roman", "Courier New", "Arial Black",
            "Comic Sans MS", "Impact", "Lucida Grande", "Tahoma"
        ]
        
        fonts = mac_fonts if 'Mac' in platform_data['os'] else windows_fonts
        available_fonts = random.sample(fonts, random.randint(8, len(fonts)))
        
        # Browser plugins
        plugins = [
            "Chrome PDF Plugin",
            "Chrome PDF Viewer", 
            "Native Client"
        ]
        
        fingerprint = BrowserFingerprint(
            user_agent=random.choice(self.user_agent_pool),
            viewport=viewport,
            screen_resolution=resolution,
            timezone=random.choice(platform_data['timezones']),
            language=random.choice(['en-US', 'en-GB', 'en-CA']),
            platform=platform_data['platform'],
            webgl_vendor=random.choice(webgl_vendors),
            webgl_renderer=random.choice(webgl_renderers),
            canvas_fingerprint=canvas_fingerprint,
            audio_fingerprint=audio_fingerprint,
            fonts=available_fonts,
            plugins=plugins,
            webrtc_ip=self._generate_webrtc_ip()
        )
        
        self.current_fingerprint = fingerprint
        return fingerprint
    
    def _generate_webrtc_ip(self) -> str:
        """Generate realistic WebRTC local IP"""
        # Common private IP ranges
        ranges = [
            "192.168.{}.{}",
            "10.0.{}.{}",
            "172.16.{}.{}"
        ]
        
        pattern = random.choice(ranges)
        return pattern.format(
            random.randint(0, 255),
            random.randint(1, 254)
        )
    
    def get_enhanced_headers(self, fingerprint: BrowserFingerprint = None) -> Dict[str, str]:
        """Generate enhanced HTTP headers with fingerprint data"""
        if not fingerprint:
            fingerprint = self.current_fingerprint or self.generate_fingerprint()
        
        headers = {
            'User-Agent': fingerprint.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': f'{fingerprint.language},en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(random.choice([0, 1])),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-CH-UA': self._generate_sec_ch_ua(fingerprint.user_agent),
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': f'"{fingerprint.platform}"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Add realistic client hints
        if 'Chrome' in fingerprint.user_agent:
            headers['sec-ch-ua-platform-version'] = '"15.0.0"' if 'Windows' in fingerprint.user_agent else '"13.0.0"'
        
        return headers
    
    def _generate_sec_ch_ua(self, user_agent: str) -> str:
        """Generate realistic Sec-CH-UA header"""
        if 'Chrome/120' in user_agent:
            return '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        elif 'Chrome/119' in user_agent:
            return '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"'
        elif 'Firefox' in user_agent:
            return '"Firefox";v="121"'
        elif 'Edge' in user_agent:
            return '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"'
        else:
            return '"Google Chrome";v="120", "Chromium";v="120", "Not?A_Brand";v="24"'
    
    def simulate_human_timing(self, action_type: str = 'request') -> float:
        """Calculate human-like timing delays"""
        patterns = self.behavior_patterns['request_timing']
        
        # Base delay
        base_delay = random.uniform(*patterns['base_delay'])
        
        # Add human variation
        variation = random.uniform(*patterns['human_variation'])
        
        # Occasionally add "think time"
        if random.random() < 0.3:  # 30% chance
            think_time = random.uniform(*patterns['think_time'])
            base_delay += think_time
        
        # Very rarely take a break
        if random.random() < patterns['break_probability']:
            break_time = random.uniform(*patterns['break_duration'])
            base_delay += break_time
            logging.info(f"Taking human-like break: {break_time:.1f}s")
        
        return base_delay
    
    def create_evasion_session(self) -> requests.Session:
        """Create a requests session with full evasion capabilities"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set enhanced headers
        fingerprint = self.generate_fingerprint()
        session.headers.update(self.get_enhanced_headers(fingerprint))
        
        # Configure session
        session.timeout = 30
        
        return session
    
    def rotate_fingerprint(self) -> BrowserFingerprint:
        """Rotate to a new browser fingerprint"""
        old_fingerprint = self.current_fingerprint
        new_fingerprint = self.generate_fingerprint()
        
        if old_fingerprint:
            logging.info(f"Rotated fingerprint: {old_fingerprint.user_agent[:50]}... -> {new_fingerprint.user_agent[:50]}...")
        
        return new_fingerprint
    
    def add_proxy(self, proxy_url: str, proxy_type: str = 'http'):
        """Add proxy to rotation pool"""
        self.proxy_pool.append({
            'url': proxy_url,
            'type': proxy_type,
            'last_used': None,
            'success_count': 0,
            'error_count': 0
        })
    
    def get_best_proxy(self) -> Optional[Dict]:
        """Get the best performing proxy from pool"""
        if not self.proxy_pool:
            return None
        
        # Filter healthy proxies
        healthy_proxies = [
            p for p in self.proxy_pool 
            if p['error_count'] < 3 and (p['success_count'] > p['error_count'])
        ]
        
        if not healthy_proxies:
            healthy_proxies = self.proxy_pool  # Fallback to all
        
        # Sort by success rate and last used time
        healthy_proxies.sort(key=lambda x: (
            x['success_count'] / max(1, x['success_count'] + x['error_count']),
            -(x['last_used'] or 0)
        ), reverse=True)
        
        return healthy_proxies[0] if healthy_proxies else None
    
    def apply_jitter(self, base_delay: float) -> float:
        """Apply realistic jitter to timing"""
        jitter_factor = random.uniform(0.8, 1.2)  # ±20% jitter
        micro_jitter = random.uniform(-0.1, 0.1)  # Small random component
        
        return max(0.1, base_delay * jitter_factor + micro_jitter)
    
    def get_evasion_stats(self) -> Dict:
        """Get current evasion statistics"""
        return {
            'current_fingerprint': {
                'user_agent': self.current_fingerprint.user_agent if self.current_fingerprint else None,
                'resolution': self.current_fingerprint.screen_resolution if self.current_fingerprint else None,
                'platform': self.current_fingerprint.platform if self.current_fingerprint else None
            },
            'proxy_pool_size': len(self.proxy_pool),
            'user_agent_pool_size': len(self.user_agent_pool),
            'session_count': len(self.session_history)
        }
    
    def generate_mouse_movement(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int, float]]:
        """Generate realistic mouse movement path with timing"""
        movements = []
        
        # Calculate movement parameters
        distance = ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
        steps = max(3, int(distance / 10))  # More steps for longer movements
        
        current_x, current_y = start
        for i in range(steps):
            # Linear interpolation with small random variations
            progress = (i + 1) / steps
            target_x = start[0] + (end[0] - start[0]) * progress
            target_y = start[1] + (end[1] - start[1]) * progress
            
            # Add small random jitter
            jitter_x = random.randint(-2, 2)
            jitter_y = random.randint(-2, 2)
            
            new_x = int(target_x + jitter_x)
            new_y = int(target_y + jitter_y)
            
            # Calculate timing (faster at start/end, slower in middle)
            timing_factor = 1 - abs(0.5 - progress) * 2
            base_time = 0.01 + timing_factor * 0.02
            jitter_time = random.uniform(-0.005, 0.005)
            
            movements.append((new_x, new_y, base_time + jitter_time))
            current_x, current_y = new_x, new_y
        
        return movements

class CaptchaSolver:
    """CAPTCHA solving capabilities"""
    
    def __init__(self):
        self.solver_services = {
            '2captcha': 'https://2captcha.com',
            'anticaptcha': 'https://anti-captcha.com',
            'deathbycaptcha': 'https://deathbycaptcha.com'
        }
    
    def solve_recaptcha(self, site_key: str, page_url: str, api_key: str = None) -> Optional[str]:
        """Solve reCAPTCHA v2/v3"""
        if not api_key:
            logging.warning("No CAPTCHA solver API key provided")
            return None
        
        # Implementation would integrate with actual CAPTCHA solving service
        # This is a placeholder for the interface
        return self._mock_captcha_solution()
    
    def solve_image_captcha(self, image_data: bytes, api_key: str = None) -> Optional[str]:
        """Solve image-based CAPTCHA"""
        if not api_key:
            return None
        
        # Mock implementation
        return self._mock_captcha_solution()
    
    def _mock_captcha_solution(self) -> str:
        """Mock CAPTCHA solution for testing"""
        return f"captcha_solution_{random.randint(100000, 999999)}"

# Global evasion engine instance
evasion_engine = AdvancedEvasionEngine()
captcha_solver = CaptchaSolver()