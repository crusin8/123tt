import os
import json
import time
import random
import string
import hashlib
import requests
import argparse
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv

# Import the TikTokLogin class
from tiktok_login import TikTokLogin

class TikTokReverseAPI:
    def __init__(self, session_id=None, ms_token=None, device_id=None, csrf_token=None):
        self.session_id = session_id
        self.ms_token = ms_token
        self.device_id = device_id
        self.csrf_token = csrf_token
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.api_base = "https://www.tiktok.com/api"
        
    @classmethod
    def login(cls, username, password):
        """Login to TikTok with username and password and return API instance"""
        login_client = TikTokLogin()
        tokens = login_client.get_tokens(username, password)
        
        if not tokens or 'session_id' not in tokens:
            logging.error("Login failed: Could not obtain tokens")
            return None
            
        return cls(
            session_id=tokens.get('session_id'),
            ms_token=tokens.get('ms_token'),
            device_id=tokens.get('device_id'),
            csrf_token=tokens.get('csrf_token')
        )
        
    def _setup_session(self):
        """Setup session with cookies and headers"""
        # Set base cookies
        cookies = {
            "sessionid": self.session_id,
            "msToken": self.ms_token,
        }
        
        if self.device_id:
            cookies["s_v_web_id"] = self.device_id
            
        if self.csrf_token:
            cookies["tt_csrf_token"] = self.csrf_token
            cookies["passport_csrf_token"] = self.csrf_token
            
        # Set common headers
        headers = {
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
        }
        
        # Update session
        self.session.headers.update(headers)
        for key, value in cookies.items():
            self.session.cookies.set(key, value, domain=".tiktok.com")
        
        return True
        
    def _generate_signature(self, url, data=None):
        """Generate TikTok's X-Bogus signature (simplified implementation)"""
        # This is a placeholder. Real X-Bogus implementation is more complex
        # and requires reverse engineering the TikTok web app.
        bogus = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        return bogus
    
    def _generate_device_id(self):
        """Generate a random device ID in TikTok format"""
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        return hashlib.md5(random_str.encode()).hexdigest()
        
    def _add_common_params(self, params):
        """Add common parameters needed for most TikTok API requests"""
        common_params = {
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": True,
            "browser_platform": "MacIntel",
            "browser_version": "5.0 (Macintosh)",
            "channel": "tiktok_web",
            "cookie_enabled": True,
            "device_id": self.device_id or self._generate_device_id(),
            "device_platform": "web_pc",
            "focus_state": True,
            "from_page": "fyp",
            "history_len": 3,
            "is_fullscreen": False,
            "is_page_visible": True,
            "language": "en",
            "os": "mac",
            "priority_region": "",
            "referer": "",
            "region": "TR",
            "screen_height": 1080,
            "screen_width": 1920,
            "tz_name": "Europe/Istanbul",
            "webcast_language": "en",
            "msToken": self.ms_token,
        }
        
        # Add timestamp
        common_params["timestamp"] = int(time.time() * 1000)
        
        # Merge with provided params
        return {**common_params, **params}
    
    def login_status(self):
        """Check if the user is logged in"""
        try:
            self._setup_session()
            
            url = f"{self.api_base}/user/info/"
            params = self._add_common_params({})
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("data", {}).get("user", {}).get("uid"):
                print(f"Successfully logged in. User ID: {data['data']['user']['uid']}")
                # Extract CSRF token if not provided initially
                if not self.csrf_token and "tt_csrf_token" in self.session.cookies:
                    self.csrf_token = self.session.cookies.get("tt_csrf_token")
                return True
            else:
                print("Login failed. Check your credentials.")
                return False
                
        except Exception as e:
            print(f"Error checking login status: {str(e)}")
            return False
            
    def get_video_info(self, video_id):
        """Get detailed information about a video"""
        try:
            self._setup_session()
            
            url = f"{self.api_base}/item/detail/"
            params = self._add_common_params({
                "itemId": video_id
            })
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get video info. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
            
    def post_comment(self, video_id, comment_text):
        """Post a comment on a video using the raw API"""
        try:
            if not self.login_status():
                print("You must be logged in to post a comment")
                return None
                
            if not self.csrf_token:
                print("CSRF token not available")
                return None
                
            # First, get the video information
            video_info = self.get_video_info(video_id)
            if not video_info:
                print("Could not get video information")
                return None
                
            # Get the author ID from the video info
            try:
                author_id = video_info["itemInfo"]["itemStruct"]["author"]["id"]
            except KeyError:
                print("Could not get author ID from video info")
                return None
                
            # Prepare the comment request
            url = f"{self.api_base}/comment/publish/"
            
            data = {
                "text": comment_text,
                "aweme_id": video_id,
                "text_extra": "[]",
                "is_self_see": 0,
                "channel_id": 1,
                "reply_to_reply_id": 0,
                "sticker_id": "",
                "sticker_source": 0
            }
            
            # Add common parameters 
            params = self._add_common_params({})
            
            # Set required headers
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": self.csrf_token,
                "X-Secsdk-Csrf-Token": f"{self.csrf_token}",
            }
            
            # Send the request
            response = self.session.post(
                url, 
                params=params,
                data=urlencode(data),
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("statusCode") == 0 and result.get("statusMsg") == "":
                    comment_id = result.get("comment", {}).get("cid", "unknown")
                    print(f"Comment posted successfully with ID: {comment_id}")
                    return result
                else:
                    print(f"Comment not posted. Status: {result.get('statusMsg', 'Unknown error')}")
                    return None
            else:
                print(f"Failed to post comment. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error posting comment: {str(e)}")
            return None
        
    def like_video(self, video_id):
        """Like a video"""
        try:
            if not self.login_status():
                print("You must be logged in to like a video")
                return None
                
            url = f"{self.api_base}/item/digg/"
            params = self._add_common_params({
                "aweme_id": video_id,
                "type": 1  # 1 for like, 0 for unlike
            })
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": self.csrf_token,
            }
            
            response = self.session.post(url, params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to like video. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error liking video: {str(e)}")
            return None
            
    def follow_user(self, user_id):
        """Follow a user"""
        try:
            if not self.login_status():
                print("You must be logged in to follow a user")
                return None
                
            url = f"{self.api_base}/commit/follow/user/"
            params = self._add_common_params({
                "user_id": user_id,
                "type": 1  # 1 for follow, 0 for unfollow
            })
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": self.csrf_token,
            }
            
            response = self.session.post(url, params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to follow user. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error following user: {str(e)}")
            return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='TikTok Reverse Engineered API Tool')
    
    # Token-based authentication options
    token_group = parser.add_argument_group('Token-based authentication')
    token_group.add_argument('--session_id', help='TikTok session ID (sessionid cookie)')
    token_group.add_argument('--ms_token', help='TikTok ms_token cookie value')
    token_group.add_argument('--device_id', help='TikTok device ID (s_v_web_id cookie)')
    token_group.add_argument('--csrf_token', help='TikTok CSRF token (tt_csrf_token or passport_csrf_token cookie)')
    token_group.add_argument('--env_file', help='Path to .env file with credentials')
    
    # Direct login options
    login_group = parser.add_argument_group('Direct login')
    login_group.add_argument('--username', help='TikTok username or email')
    login_group.add_argument('--password', help='TikTok password')
    
    # Action options
    parser.add_argument('--video_id', help='TikTok video ID to interact with')
    parser.add_argument('--comment', help='Comment text to post')
    parser.add_argument('--like', action='store_true', help='Like the video')
    parser.add_argument('--follow', action='store_true', help='Follow the video author')
    
    args = parser.parse_args()
    
    # Initialize API with either direct login or tokens
    api = None
    
    # Try direct login if username and password provided
    if args.username and args.password:
        print(f"Attempting to login with username: {args.username}")
        api = TikTokReverseAPI.login(args.username, args.password)
        if not api:
            print("Login failed with username and password. Please check your credentials.")
            return
        print("Login successful with username and password!")
    else:
        # Load from .env file if specified
        if args.env_file:
            load_dotenv(args.env_file)
            
        # Get credentials (prioritize command line args over .env)
        session_id = args.session_id or os.getenv('TIKTOK_SESSION_ID')
        ms_token = args.ms_token or os.getenv('TIKTOK_MS_TOKEN')
        device_id = args.device_id or os.getenv('TIKTOK_DEVICE_ID')
        csrf_token = args.csrf_token or os.getenv('TIKTOK_CSRF_TOKEN')
        
        if not session_id:
            print("Error: Either username/password or session_id is required")
            print("Provide credentials either as command line arguments or in a .env file")
            return
        
        # Initialize the API with tokens
        api = TikTokReverseAPI(
            session_id=session_id,
            ms_token=ms_token,
            device_id=device_id,
            csrf_token=csrf_token
        )
    
    # Check if login is valid
    if not api.login_status():
        print("Login failed. Please check your credentials.")
        return
        
    # Process actions based on arguments
    if args.video_id:
        # Get video info
        video_info = api.get_video_info(args.video_id)
        if video_info:
            print(f"Successfully fetched info for video {args.video_id}")
        
        # Post comment if provided
        if args.comment:
            comment_result = api.post_comment(args.video_id, args.comment)
            if comment_result:
                print(f"Successfully commented: '{args.comment}' on video {args.video_id}")
            
        # Like video if requested
        if args.like:
            like_result = api.like_video(args.video_id)
            if like_result:
                print(f"Successfully liked video {args.video_id}")
            
        # Follow user if requested
        if args.follow and video_info:
            try:
                author_id = video_info["itemInfo"]["itemStruct"]["author"]["id"]
                follow_result = api.follow_user(author_id)
                if follow_result:
                    print(f"Successfully followed user {author_id}")
            except (KeyError, TypeError):
                print("Could not extract author ID from video info")
    else:
        print("No video ID provided. Please specify a video ID to interact with.")

if __name__ == "__main__":
    main() 