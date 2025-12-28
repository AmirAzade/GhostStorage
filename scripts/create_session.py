import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv

# Try to load from .env file in the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_input(prompt, env_key):
    """Get value from env or ask user input"""
    val = os.getenv(env_key)
    if val:
        print(f"Loaded {env_key} from .env")
        return val
    return input(prompt)

print("--- Telegram Session Generator ---")

# Get credentials
api_id = get_input("Enter API ID: ", 'TG_API_ID')
api_hash = get_input("Enter API Hash: ", 'TG_API_HASH')
session_name = get_input("Enter Session Name (e.g., mysession): ", 'TG_SESSION_NAME')

if not api_id or not api_hash or not session_name:
    print("Error: Missing credentials.")
    exit(1)

# Ensure session is saved in the root directory (where manage.py is)
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_path = os.path.join(base_path, session_name)

print(f"Connecting to Telegram... (Check your phone for the code)")

with TelegramClient(session_path, int(api_id), api_hash) as client:
    print(f"\n✅ Session file created successfully at: {session_path}.session")
    
    # Send a test message
    client.send_message('me', '🤖 Hello! Your Telegram Drive session is active.')
    print("Test message sent to 'Saved Messages'.")