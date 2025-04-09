import requests
import time
import json
import re
import random
import string
import hashlib
import logging
from urllib.parse import urlencode

class TikTokLogin:
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.base_url = "https://www.tiktok.com"
        self.login_url = "https://www.tiktok.com/login/"
        self.api_login_url = "https://www.tiktok.com/api/login/"
        
        # Set up basic headers
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="120"',
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _generate_device_id(self):
        """Generate a random device ID in TikTok format (s_v_web_id)"""
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        device_id = hashlib.md5(random_str.encode()).hexdigest()
        timestamp = int(time.time())
        
        # TikTok format: verify_xxxxx_yyyyy_zzzzzz
        version = "".join(random.choices("0123456789", k=5))
        segment1 = device_id[:8]
        segment2 = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        
        # TikTok device IDs have a specific pattern
        return f"verify_{version}_{segment1}_{segment2}"

    def _generate_ms_token(self):
        """Generate a simplified MS token"""
        timestamp = int(time.time() * 1000)
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=120))
        return f"ms{timestamp}{random_part}"[:150]

    def _extract_tokens_from_response(self, response):
        """Extract tokens from login response and cookies"""
        tokens = {}
        
        # Extract session ID from cookies
        if 'sessionid' in self.session.cookies:
            tokens['session_id'] = self.session.cookies.get('sessionid')
        
        # Extract CSRF token
        if 'tt_csrf_token' in self.session.cookies:
            tokens['csrf_token'] = self.session.cookies.get('tt_csrf_token')
        elif 'passport_csrf_token' in self.session.cookies:
            tokens['csrf_token'] = self.session.cookies.get('passport_csrf_token')
        
        # Extract other tokens from cookies
        if 's_v_web_id' in self.session.cookies:
            tokens['device_id'] = self.session.cookies.get('s_v_web_id')
        
        if 'msToken' in self.session.cookies:
            tokens['ms_token'] = self.session.cookies.get('msToken')
        else:
            # Generate MS token if not available
            tokens['ms_token'] = self._generate_ms_token()
        
        return tokens

    def _get_login_parameters(self):
        """Visit TikTok login page to get required parameters"""
        try:
            # Visit main page first
            response = self.session.get(self.base_url)
            
            # Set device ID if not already set
            if 's_v_web_id' not in self.session.cookies:
                device_id = self._generate_device_id()
                self.session.cookies.set('s_v_web_id', device_id, domain='.tiktok.com')
            
            # Visit login page to get CSRF token
            response = self.session.get(self.login_url)
            
            # Check if CSRF token is in cookies
            if 'tt_csrf_token' not in self.session.cookies:
                # Try to extract CSRF token from page content
                csrf_pattern = r'var\s+CSRF_TOKEN\s*=\s*["\']([^"\']+)["\']'
                match = re.search(csrf_pattern, response.text)
                if match:
                    csrf_token = match.group(1)
                    self.session.cookies.set('tt_csrf_token', csrf_token, domain='.tiktok.com')
                else:
                    # Generate a random CSRF token if not found
                    csrf_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                    self.session.cookies.set('tt_csrf_token', csrf_token, domain='.tiktok.com')
            
            return True
        except Exception as e:
            logging.error(f"Error getting login parameters: {str(e)}")
            return False

    def login_with_email(self, email, password):
        """Login to TikTok with email and password"""
        try:
            # Get necessary login parameters first
            if not self._get_login_parameters():
                return None
            
            # Get CSRF token
            csrf_token = self.session.cookies.get('tt_csrf_token', '')
            if not csrf_token:
                return None
            
            # Prepare login data
            login_data = {
                "email": email,
                "password": password,
                "mix_mode": 1,
                "aid": 1459,
                "account_sdk_source": "web",
                "language": "en",
                "captcha": "",
                "fp": "",  # Fingerprint would go here in a real implementation
            }
            
            # Set necessary headers for login request
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrf_token,
            }
            
            # Make login request
            response = self.session.post(
                self.api_login_url, 
                data=urlencode(login_data), 
                headers=headers
            )
            
            # Check login result
            data = response.json()
            
            if response.status_code == 200 and data.get("data", {}).get("redirect_url"):
                # Login successful, now visit the redirect URL to complete login
                redirect_url = data["data"]["redirect_url"]
                self.session.get(redirect_url)
                
                # Extract tokens from cookies
                tokens = self._extract_tokens_from_response(response)
                return tokens
            else:
                error_message = data.get("message", "Unknown error")
                logging.error(f"Login failed: {error_message}")
                return None
                
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return None

    def login_with_username(self, username, password):
        """Login with username (wrapper for email login)"""
        return self.login_with_email(username, password)

    def get_tokens(self, username, password):
        """Get TikTok tokens using username/password login"""
        tokens = self.login_with_username(username, password)
        
        if tokens and 'session_id' in tokens:
            return tokens
        
        # Try fallback login method if direct API login failed
        logging.info("Direct API login failed, trying alternate method...")
        return None  # In a real implementation, we would try another method here 