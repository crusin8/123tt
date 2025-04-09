import os
import json
import time
import asyncio
import argparse
from dotenv import load_dotenv
from TikTokApi import TikTokApi
from TikTokApi.tiktok import TikTokapi

class TikTokBot:
    def __init__(self, ms_token=None, session_id=None, device_id=None):
        self.ms_token = ms_token
        self.session_id = session_id
        self.device_id = device_id
        self.api = None
        
    async def initialize(self):
        """Initialize the TikTok API with session tokens."""
        try:
            if not self.ms_token or not self.session_id:
                raise ValueError("ms_token and session_id are required")
            
            # Create API instance with the provided tokens
            self.api = TikTokApi(custom_verify_fp=self.session_id, 
                                use_test_endpoints=False,
                                ms_token=self.ms_token)
            
            # Set device ID if provided
            if self.device_id:
                self.api.set_device_id(self.device_id)
                
            print("API initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing API: {str(e)}")
            return False
            
    async def get_user_info(self, username):
        """Get a user's profile information."""
        try:
            user_data = await self.api.user(username=username).info()
            return user_data
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None
            
    async def get_video_info(self, video_id):
        """Get video information by ID."""
        try:
            video = await self.api.video(id=video_id)
            video_info = await video.info()
            return video_info
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
            
    async def post_comment(self, video_id, comment_text):
        """Post a comment on a video."""
        try:
            # Get video object
            video = await self.api.video(id=video_id)
            
            # Post comment
            comment_response = await video.comment(comment_text)
            
            # Print success message
            if 'comment_id' in comment_response:
                print(f"Comment posted successfully with ID: {comment_response['comment_id']}")
                return comment_response
            else:
                print("Comment posted, but no comment ID returned")
                return comment_response
                
        except Exception as e:
            print(f"Error posting comment: {str(e)}")
            return None
            
    async def close(self):
        """Close the API session."""
        if self.api:
            await self.api.close_sessions()
            print("API session closed")


async def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='TikTok API Bot for Login and Comments')
    parser.add_argument('--session_id', help='TikTok session ID (ss_id)')
    parser.add_argument('--ms_token', help='TikTok ms_token')
    parser.add_argument('--device_id', help='TikTok device ID')
    parser.add_argument('--env_file', help='Path to .env file with credentials')
    parser.add_argument('--video_id', required=True, help='TikTok video ID to comment on')
    parser.add_argument('--comment', required=True, help='Comment text to post')
    
    args = parser.parse_args()
    
    # Load from .env file if specified
    if args.env_file:
        load_dotenv(args.env_file)
        
    # Get credentials (prioritize command line args over .env)
    session_id = args.session_id or os.getenv('TIKTOK_SESSION_ID')
    ms_token = args.ms_token or os.getenv('TIKTOK_MS_TOKEN')
    device_id = args.device_id or os.getenv('TIKTOK_DEVICE_ID')
    
    if not session_id or not ms_token:
        print("Error: session_id and ms_token are required")
        print("Provide them either as command line arguments or in a .env file")
        return
    
    # Initialize the bot
    bot = TikTokBot(
        session_id=session_id,
        ms_token=ms_token,
        device_id=device_id
    )
    
    try:
        # Initialize API
        init_success = await bot.initialize()
        if not init_success:
            return
        
        # Post comment
        comment_result = await bot.post_comment(args.video_id, args.comment)
        
        if comment_result:
            print(f"Successfully commented: '{args.comment}' on video {args.video_id}")
        else:
            print(f"Failed to comment on video {args.video_id}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the session
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 