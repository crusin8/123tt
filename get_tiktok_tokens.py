import json
import sys
import os
import re
import argparse
from datetime import datetime

def extract_cookies_from_file(file_path):
    """Extract cookies from a Netscape cookie file"""
    cookies = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    fields = line.strip().split('\t')
                    if len(fields) >= 7:
                        name = fields[5]
                        value = fields[6]
                        cookies[name] = value
        return cookies
    except Exception as e:
        print(f"Error reading cookie file: {str(e)}")
        return {}

def extract_cookies_from_json(file_path):
    """Extract cookies from a JSON file exported from browser"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        cookies = {}
        if isinstance(data, list):
            # Chrome/Edge format
            for cookie in data:
                if 'name' in cookie and 'value' in cookie and cookie.get('domain', '').endswith('tiktok.com'):
                    cookies[cookie['name']] = cookie['value']
        elif isinstance(data, dict) and 'cookies' in data:
            # Firefox format
            for cookie in data['cookies']:
                if 'name' in cookie and 'value' in cookie and cookie.get('domain', '').endswith('tiktok.com'):
                    cookies[cookie['name']] = cookie['value']
                    
        return cookies
    except Exception as e:
        print(f"Error reading JSON cookie file: {str(e)}")
        return {}

def extract_cookies_from_headers(file_path):
    """Extract cookies from Set-Cookie headers"""
    cookies = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('Set-Cookie:'):
                    # Extract cookie name and value
                    cookie_part = line.split('Set-Cookie:', 1)[1].strip()
                    name_value = cookie_part.split(';')[0].strip()
                    if '=' in name_value:
                        name, value = name_value.split('=', 1)
                        cookies[name] = value
        return cookies
    except Exception as e:
        print(f"Error reading headers file: {str(e)}")
        return {}

def extract_session_tokens(cookies):
    """Extract the required TikTok tokens from cookies dictionary"""
    tokens = {
        'session_id': cookies.get('sessionid', ''),
        'ms_token': cookies.get('msToken', ''),
        'device_id': cookies.get('s_v_web_id', '')
    }
    
    # Get CSRF token (could be in different cookie names)
    csrf_token = cookies.get('tt_csrf_token', '') or cookies.get('passport_csrf_token', '')
    if csrf_token:
        tokens['csrf_token'] = csrf_token
    
    # Additional cookies that might be useful
    if 'sid_tt' in cookies:
        tokens['sid_tt'] = cookies['sid_tt']
        
    return tokens

def validate_tokens(tokens):
    """Validate if the essential tokens are present"""
    if not tokens['session_id']:
        print("Warning: sessionid not found in cookies")
        return False
        
    return True

def create_env_file(tokens, output_file='.env'):
    """Create a .env file with the tokens"""
    try:
        with open(output_file, 'w') as f:
            f.write(f"# TikTok API Tokens - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"TIKTOK_SESSION_ID={tokens['session_id']}\n")
            
            if tokens.get('ms_token'):
                f.write(f"TIKTOK_MS_TOKEN={tokens['ms_token']}\n")
            
            if tokens.get('device_id'):
                f.write(f"TIKTOK_DEVICE_ID={tokens['device_id']}\n")
                
            if tokens.get('csrf_token'):
                f.write(f"TIKTOK_CSRF_TOKEN={tokens['csrf_token']}\n")
                
            # Add any additional tokens
            for key, value in tokens.items():
                if key not in ['session_id', 'ms_token', 'device_id', 'csrf_token'] and value:
                    env_key = f"TIKTOK_{key.upper()}"
                    f.write(f"{env_key}={value}\n")
                    
        print(f"Tokens successfully written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing .env file: {str(e)}")
        return False

def detect_file_type(file_path):
    """Detect type of file based on content"""
    try:
        with open(file_path, 'r') as f:
            first_lines = [f.readline() for _ in range(5)]
            
        # Check if it's a Set-Cookie header file
        if any(line.startswith('Set-Cookie:') for line in first_lines):
            return 'headers'
            
        # Check if it's JSON
        with open(file_path, 'r') as f:
            try:
                json.load(f)
                return 'json'
            except json.JSONDecodeError:
                pass
                
        # Assume it's Netscape cookie format if we get here
        return 'netscape'
    except Exception:
        return 'netscape'  # Default to Netscape format

def main():
    parser = argparse.ArgumentParser(description='Extract TikTok tokens from cookies')
    parser.add_argument('--cookie_file', required=True, help='Path to cookie file (Netscape format, JSON or Set-Cookie headers)')
    parser.add_argument('--output', default='.env', help='Output .env file path (default: .env)')
    parser.add_argument('--file_type', choices=['netscape', 'json', 'headers'], help='Force a specific file type (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.cookie_file):
        print(f"Error: Cookie file {args.cookie_file} not found")
        return 1
        
    # Determine file type
    file_type = args.file_type or detect_file_type(args.cookie_file)
    print(f"Processing file as {file_type} format")
    
    # Extract cookies based on file type
    if file_type == 'json':
        cookies = extract_cookies_from_json(args.cookie_file)
    elif file_type == 'headers':
        cookies = extract_cookies_from_headers(args.cookie_file)
    else:  # netscape
        cookies = extract_cookies_from_file(args.cookie_file)
        
    if not cookies:
        print("No cookies found in the file")
        return 1
        
    tokens = extract_session_tokens(cookies)
    
    if not validate_tokens(tokens):
        print("\nWarning: Some essential tokens are missing. TikTok API might not work correctly.")
        proceed = input("Do you want to proceed anyway? (y/n): ")
        if proceed.lower() != 'y':
            return 1
            
    # Print tokens to console
    print("\nExtracted TikTok tokens:")
    for key, value in tokens.items():
        if value:
            # Mask part of the token for security
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
            print(f"{key}: {masked_value}")
            
    # Create .env file
    success = create_env_file(tokens, args.output)
    
    if success:
        print(f"\nTokens have been saved to {args.output}")
        print("You can now use these tokens with tiktok_reverse_api.py script")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 