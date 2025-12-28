from telethon import TelegramClient
from django.conf import settings

# Initialize the client once
client = TelegramClient(settings.TG_SESSION_NAME, settings.TG_API_ID, settings.TG_API_HASH)

async def get_client():
    """Ensures client is connected before returning it"""
    if not client.is_connected():
        await client.connect()
    
    # Note: On first run, you might need to run a script locally to 
    # generate the session file because you can't enter OTP in a web server.
    return client