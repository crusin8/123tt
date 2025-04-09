import os
import sys
import argparse
from dotenv import load_dotenv

# tiktok_reverse_api.py modülünü import edelim
sys.path.append('.')
from tiktok_reverse_api import TikTokReverseAPI

def main():
    parser = argparse.ArgumentParser(description='Test TikTok API with tokens')
    parser.add_argument('--env_file', default='.env.new', help='Path to .env file with tokens')
    parser.add_argument('--action', choices=['login', 'video_info', 'comment'], default='login', 
                        help='Action to test (default: login)')
    parser.add_argument('--video_id', help='Video ID to use for video_info or comment actions')
    parser.add_argument('--comment', help='Comment text to post')
    
    args = parser.parse_args()
    
    # Load tokens from .env file
    if not os.path.exists(args.env_file):
        print(f"Error: Env file {args.env_file} not found")
        return 1
        
    load_dotenv(args.env_file)
    
    # Get tokens
    session_id = os.getenv('TIKTOK_SESSION_ID')
    ms_token = os.getenv('TIKTOK_MS_TOKEN')
    csrf_token = os.getenv('TIKTOK_CSRF_TOKEN')
    device_id = os.getenv('TIKTOK_DEVICE_ID')
    
    if not session_id:
        print("Error: session_id not found in .env file")
        return 1
        
    # Print what we're working with
    print("\nWorking with the following tokens:")
    print(f"session_id: {session_id[:4]}...{session_id[-4:]}")
    if ms_token:
        print(f"ms_token: {ms_token[:4]}...{ms_token[-4:]}")
    if csrf_token:
        print(f"csrf_token: {csrf_token[:4]}...{csrf_token[-4:]}")
    if device_id:
        print(f"device_id: {device_id[:4]}...{device_id[-4:] if device_id else ''}")
    
    # Initialize API
    api = TikTokReverseAPI(
        session_id=session_id,
        ms_token=ms_token,
        device_id=device_id,
        csrf_token=csrf_token
    )
    
    # Perform the requested action
    if args.action == 'login':
        print("\nTesting login status...")
        success = api.login_status()
        if success:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    elif args.action == 'video_info':
        if not args.video_id:
            print("Error: video_id is required for video_info action")
            return 1
            
        print(f"\nGetting info for video {args.video_id}...")
        video_info = api.get_video_info(args.video_id)
        
        if video_info:
            # Extract some basic info
            try:
                author = video_info["itemInfo"]["itemStruct"]["author"]["uniqueId"]
                desc = video_info["itemInfo"]["itemStruct"]["desc"]
                likes = video_info["itemInfo"]["itemStruct"]["stats"]["diggCount"]
                comments = video_info["itemInfo"]["itemStruct"]["stats"]["commentCount"]
                
                print("\n✅ Successfully retrieved video info:")
                print(f"Author: @{author}")
                print(f"Description: {desc}")
                print(f"Likes: {likes}")
                print(f"Comments: {comments}")
            except KeyError:
                print("\n❓ Video info retrieved but structure is different than expected.")
                print("Here's a sample of retrieved data:")
                print(str(video_info)[:500] + "...")
        else:
            print("\n❌ Failed to get video info!")
            
    elif args.action == 'comment':
        if not args.video_id:
            print("Error: video_id is required for comment action")
            return 1
            
        if not args.comment:
            print("Error: comment text is required for comment action")
            return 1
            
        print(f"\nPosting comment '{args.comment}' on video {args.video_id}...")
        result = api.post_comment(args.video_id, args.comment)
        
        if result:
            print("\n✅ Comment posted successfully!")
        else:
            print("\n❌ Failed to post comment!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 