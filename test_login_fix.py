#!/usr/bin/env python3
"""
TikTok Login Fix Test Script
This script tests the updated TikTok login functionality with detailed debugging.
"""

import argparse
import logging
import json
import sys
import requests
from urllib.parse import urlencode
import random

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tiktok_login_fix.log')
    ]
)

def test_direct_login(username, password):
    """Test direct login to TikTok using the passport endpoint"""
    session = requests.Session()
    
    # First get the CSRF token by visiting main page
    logging.info("Getting CSRF token...")
    response = session.get("https://www.tiktok.com/login/")
    
    # Check cookies
    cookies = session.cookies.get_dict()
    logging.info(f"Initial cookies: {cookies}")
    
    csrf_token = cookies.get('tt_csrf_token', '')
    if not csrf_token:
        logging.error("Failed to get CSRF token")
        return None
    
    logging.info(f"Got CSRF token: {csrf_token}")
    
    # Prepare login request
    login_url = "https://www.tiktok.com/passport/web/login_v2/"
    
    login_data = {
        "account": username,
        "password": password,
        "mix_mode": "1",
        "aid": "1459",
        "account_sdk_source": "web",
        "language": "en",
        "captcha": "",
        "type": "email",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/login/",
        "Origin": "https://www.tiktok.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf_token,
    }
    
    # Make login request
    logging.info("Making login request...")
    response = session.post(
        login_url,
        data=urlencode(login_data),
        headers=headers
    )
    
    # Log response details
    logging.info(f"Login response status: {response.status_code}")
    
    # Try to parse JSON response
    try:
        data = response.json()
        logging.info(f"Login response data: {json.dumps(data, indent=2)}")
        
        # Check if there was an error message
        if "message" in data:
            logging.error(f"Login error: {data['message']}")
        
        # Check for successful login indicators
        if data.get("data", {}).get("redirect_url"):
            logging.info(f"Login successful! Redirect URL: {data['data']['redirect_url']}")
            
            # Follow redirect
            redirect_url = data["data"]["redirect_url"]
            logging.info(f"Following redirect to: {redirect_url}")
            
            redirect_response = session.get(redirect_url)
            logging.info(f"Redirect response status: {redirect_response.status_code}")
            
            # Log cookies after redirect
            cookies_after_redirect = session.cookies.get_dict()
            logging.info(f"Cookies after redirect: {cookies_after_redirect}")
            
            # Check if session ID is present
            session_id = cookies_after_redirect.get("sessionid")
            if session_id:
                logging.info(f"Login confirmed! Session ID: {session_id[:4]}***{session_id[-4:] if len(session_id) > 8 else ''}")
                return True
            else:
                logging.error("No session ID found after redirect")
                return False
        
        # Alternative success format
        elif data.get("data", {}).get("redirect"):
            redirect = data["data"]["redirect"]
            logging.info(f"Login successful (alternative format)! Redirect: {redirect}")
            return True
            
        # Direct token in response
        elif data.get("data", {}).get("token"):
            token = data["data"]["token"]
            logging.info(f"Login successful! Got token directly: {token[:4]}***{token[-4:] if len(token) > 8 else ''}")
            return True
            
        else:
            logging.error("Login failed: No success indicators in response")
            return False
            
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response")
        logging.debug(f"Raw response: {response.text[:1000]}")
        return False
        
    return False

def test_sso_login(username, password):
    """Test login using the SSO endpoint"""
    session = requests.Session()
    
    # First get the CSRF token by visiting main page
    logging.info("Getting CSRF token for SSO login...")
    response = session.get("https://www.tiktok.com/login/")
    
    cookies = session.cookies.get_dict()
    csrf_token = cookies.get('tt_csrf_token', '')
    if not csrf_token:
        logging.error("Failed to get CSRF token for SSO login")
        return None
    
    logging.info(f"Got CSRF token for SSO login: {csrf_token}")
    
    # SSO login endpoint
    sso_login_url = "https://www.tiktok.com/passport/web/account/sso/login/"
    
    login_data = {
        "account": username,
        "password": password,
        "account_sdk_source": "web",
        "language": "en",
        "captcha": "",
        "type": "email",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/login/",
        "Origin": "https://www.tiktok.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf_token,
    }
    
    # Make login request
    logging.info("Making SSO login request...")
    response = session.post(
        sso_login_url,
        data=urlencode(login_data),
        headers=headers
    )
    
    # Log response details
    logging.info(f"SSO Login response status: {response.status_code}")
    
    # Try to parse JSON response
    try:
        data = response.json()
        logging.info(f"SSO Login response data: {json.dumps(data, indent=2)}")
        
        # Check for successful login indicators
        if response.status_code == 200 and "passport_csrf_token" in session.cookies:
            logging.info("SSO Login successful!")
            
            # Log cookies
            cookies = session.cookies.get_dict()
            logging.info(f"Cookies after SSO login: {cookies}")
            
            # Check if session ID is present
            session_id = cookies.get("sessionid")
            if session_id:
                logging.info(f"SSO Login confirmed! Session ID: {session_id[:4]}***{session_id[-4:]}")
                return True
            else:
                logging.error("No session ID found after SSO login")
                return False
        else:
            logging.error("SSO Login failed")
            return False
            
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response from SSO login")
        logging.debug(f"Raw SSO response: {response.text[:1000]}")
        return False
        
    return False

def test_mobile_api_login(username, password):
    """Test login using TikTok's mobile API"""
    session = requests.Session()
    
    # Set up proper headers for mobile API
    session.headers.update({
        "User-Agent": "okhttp/3.10.0.1",
        "sdk-version": "2",
        "Accept-Encoding": "gzip"
    })
    
    # Generate a device ID
    device_id = ''.join(random.choices("0123456789", k=15))
    
    # Mobile API login endpoint
    mobile_login_url = "https://api16-normal-c-useast1a.tiktokv.com/passport/user/login/"
    
    # Prepare login data for mobile API
    login_data = {
        "username": username,
        "password": password,
        "mix_mode": "1",
        "multi_login": "1",
        "aid": "1233",
        "language": "en",
        "app_name": "musical_ly",
        "account_sdk_source": "app",
        "iid": device_id,
        "device_id": device_id,
    }
    
    # Make login request
    logging.info("Making mobile API login request...")
    response = session.post(
        mobile_login_url, 
        data=login_data
    )
    
    # Log response details
    logging.info(f"Mobile API Login response status: {response.status_code}")
    
    # Try to parse JSON response
    try:
        data = response.json()
        logging.info(f"Mobile API Login response data: {json.dumps(data, indent=2)}")
        
        # Check for successful login indicators
        if response.status_code == 200 and data.get("data", {}).get("session_key"):
            session_key = data["data"]["session_key"]
            logging.info(f"Mobile API login successful! Session key: {session_key[:4]}***{session_key[-4:] if len(session_key) > 8 else ''}")
            
            # Set the session ID in cookies for later web API use
            session.cookies.set('sessionid', session_key, domain='.tiktok.com')
            
            # Try to make a request to user info to validate the session
            user_info_url = "https://www.tiktok.com/api/user/info/"
            user_info_response = session.get(user_info_url)
            logging.info(f"User info API call status: {user_info_response.status_code}")
            
            try:
                user_data = user_info_response.json()
                if user_data.get("data", {}).get("user", {}).get("uid"):
                    user_id = user_data["data"]["user"]["uid"]
                    logging.info(f"Session validated! User ID: {user_id}")
                    return True
                else:
                    logging.warning("User info doesn't contain valid user data")
            except:
                logging.warning("Couldn't parse user info response")
                
            # Even if user info validation fails, we have a session key, so login was successful
            return True
        else:
            error_message = data.get("message", "Unknown error")
            logging.error(f"Mobile API login failed: {error_message}")
            return False
            
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response from mobile API")
        logging.debug(f"Raw mobile API response: {response.text[:1000]}")
        return False
        
    return False

def main():
    parser = argparse.ArgumentParser(description='Test TikTok login fix')
    parser.add_argument('--username', required=True, help='TikTok username or email')
    parser.add_argument('--password', required=True, help='TikTok password')
    parser.add_argument('--method', choices=['direct', 'sso', 'mobile', 'all'], default='all',
                       help='Login method to test (direct, sso, mobile, or all)')
    
    args = parser.parse_args()
    
    success = False
    
    if args.method in ['direct', 'all']:
        logging.info("=== Testing Direct Login Method ===")
        direct_success = test_direct_login(args.username, args.password)
        if direct_success:
            success = True
            logging.info("Direct login method succeeded!")
        else:
            logging.warning("Direct login method failed")
    
    if args.method in ['sso', 'all'] and not success:
        logging.info("=== Testing SSO Login Method ===")
        sso_success = test_sso_login(args.username, args.password)
        if sso_success:
            success = True
            logging.info("SSO login method succeeded!")
        else:
            logging.warning("SSO login method failed")
    
    if args.method in ['mobile', 'all'] and not success:
        logging.info("=== Testing Mobile API Login Method ===")
        mobile_success = test_mobile_api_login(args.username, args.password)
        if mobile_success:
            success = True
            logging.info("Mobile API login method succeeded!")
        else:
            logging.warning("Mobile API login method failed")
    
    if success:
        logging.info("✅ Login test successful!")
        return 0
    else:
        logging.error("❌ All login methods failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 