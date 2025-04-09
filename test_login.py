import argparse
import logging
import json
from tiktok_login import TikTokLogin
from tiktok_reverse_api import TikTokReverseAPI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Test TikTok direct login')
    parser.add_argument('--username', required=True, help='TikTok username or email')
    parser.add_argument('--password', required=True, help='TikTok password')
    parser.add_argument('--save_tokens', action='store_true', help='Save obtained tokens to .env.login file')
    parser.add_argument('--test_api', action='store_true', help='Test API functions after login')
    parser.add_argument('--video_id', help='Video ID to test with (if test_api is enabled)')
    
    args = parser.parse_args()
    
    # First try the direct TikTokLogin class
    logging.info(f"Attempting to login with username: {args.username}")
    login_client = TikTokLogin()
    tokens = login_client.get_tokens(args.username, args.password)
    
    if not tokens or 'session_id' not in tokens:
        logging.error("Direct login failed with TikTokLogin class")
        return 1
    
    # Print tokens (masked for security)
    logging.info("Login successful! Obtained tokens:")
    for key, value in tokens.items():
        if value and len(value) > 8:
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            logging.info(f"  {key}: {masked_value}")
        elif value:
            logging.info(f"  {key}: {'*' * len(value)}")
    
    # Save tokens to .env file if requested
    if args.save_tokens:
        with open('.env.login', 'w') as f:
            f.write(f"# TikTok tokens obtained through direct login\n")
            f.write(f"TIKTOK_SESSION_ID={tokens.get('session_id', '')}\n")
            f.write(f"TIKTOK_MS_TOKEN={tokens.get('ms_token', '')}\n")
            f.write(f"TIKTOK_DEVICE_ID={tokens.get('device_id', '')}\n")
            f.write(f"TIKTOK_CSRF_TOKEN={tokens.get('csrf_token', '')}\n")
        logging.info("Tokens saved to .env.login file")
    
    # Test the TikTokReverseAPI login class method
    logging.info("\nTesting TikTokReverseAPI.login() class method...")
    api = TikTokReverseAPI.login(args.username, args.password)
    
    if not api:
        logging.error("Login failed with TikTokReverseAPI.login() method")
        return 1
    
    logging.info("Login successful with TikTokReverseAPI.login() method!")
    
    # Test API functions if requested
    if args.test_api:
        if not args.video_id:
            logging.error("Video ID is required for API testing")
            return 1
        
        # Test getting video info
        logging.info(f"\nTesting video info retrieval for video ID: {args.video_id}")
        video_info = api.get_video_info(args.video_id)
        
        if video_info:
            try:
                author = video_info["itemInfo"]["itemStruct"]["author"]["uniqueId"]
                desc = video_info["itemInfo"]["itemStruct"]["desc"]
                likes = video_info["itemInfo"]["itemStruct"]["stats"]["diggCount"]
                comments = video_info["itemInfo"]["itemStruct"]["stats"]["commentCount"]
                
                logging.info("✅ Successfully retrieved video info:")
                logging.info(f"  Author: @{author}")
                logging.info(f"  Description: {desc}")
                logging.info(f"  Likes: {likes}")
                logging.info(f"  Comments: {comments}")
            except KeyError:
                logging.warning("Video info retrieved but structure is different than expected")
                sample = json.dumps(video_info)[:200] + "..."
                logging.info(f"Sample of retrieved data: {sample}")
        else:
            logging.error("Failed to get video info")
    
    logging.info("\nAll tests completed!")
    return 0

if __name__ == "__main__":
    exit(main()) 