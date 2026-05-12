#!/usr/bin/env python3
"""
Authentication helper for reading credentials from environment variables
"""
import os
import json
import tempfile

def get_credentials_file():
    """
    Get credentials from environment variable or local file.
    If GOOGLE_CREDENTIALS_JSON env var exists, create temp file with its content.
    Otherwise, use local credentials.json file.
    """
    # Try to read from environment variable
    credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')

    if credentials_json:
        # Create temporary file with credentials
        try:
            creds_data = json.loads(credentials_json)
            # Create temp file in current directory
            with open('credentials.json', 'w') as f:
                json.dump(creds_data, f)
            return 'credentials.json'
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in GOOGLE_CREDENTIALS_JSON environment variable")
            pass

    # Fall back to local file
    if os.path.exists('credentials.json'):
        return 'credentials.json'

    # If nothing found, raise error
    raise FileNotFoundError(
        "Credentials not found. Either:\n"
        "1. Set GOOGLE_CREDENTIALS_JSON environment variable with the JSON content\n"
        "2. Place credentials.json in the current directory"
    )

if __name__ == '__main__':
    try:
        creds_file = get_credentials_file()
        print(f"✓ Using credentials from: {creds_file}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        exit(1)
