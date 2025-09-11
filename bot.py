import os
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# --- Telegram auth ---
api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
channel = os.environ["TG_CHANNEL"]
session_str = os.environ["TG_SESSION"]
yt_token = os.environ["YT_TOKEN"]

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# --- YouTube auth ---
creds = Credentials.from_authorized_user_info(
    json.loads(yt_token)  # берем токен из Secrets
)

youtube = build("youtube", "v3", credentials=creds)

# --- Counter ---
if os.path.exists("counter.json"):
    with open("counter.json", "r") as f:
        counter = json.load(f)
else:
    counter = {"count": 1}

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
                media_body=MediaFileUpload(path, resumable=True)  # фикс загрузки
            )
            request.execute()
            print(f"✅ Загружено: Anime edit #{count}")
            count += 1

    # обновляем счётчик
    with open("counter.json", "w") as f:
        json.dump({"count": count}, f)

with client:
    client.loop.run_until_complete(main())
