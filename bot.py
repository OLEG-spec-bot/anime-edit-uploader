import os
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# --- Telegram auth ---
api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
channel = os.environ["TG_CHANNEL"]
session = os.environ["TG_SESSION"]
yt_token = os.environ["YT_TOKEN"]

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# --- YouTube auth ---
creds = Credentials.from_authorized_user_info(
    json.loads(open("token.json").read())
)

youtube = build("youtube", "v3", credentials=creds)

# --- Counter ---
with open("counter.json", "r") as f:
    counter = json.load(f)

count = counter["count"]

async def main():
    global count
    async for message in client.iter_messages(channel, limit=1):
        if message.video or (message.document and message.document.mime_type.startswith("video")):
            path = await message.download_media(file="video.mp4")

            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": f"Anime edit #{count}",
                        "description": "Best anime edits 🚀",
                        "tags": ["anime", "edit", "shorts"],
                        "categoryId": "22"
                    },
                    "status": {
                        "privacyStatus": "public",
                        "selfDeclaredMadeForKids": False
                    }
                },
                media_body=path
            )
            request.execute()
            print(f"✅ Загружено: Anime edit #{count}")
            count += 1

    # обновляем счётчик
    with open("counter.json", "w") as f:
        json.dump({"count": count}, f)

with client:
    client.loop.run_until_complete(main())
