import os
import json
import random
from telethon import TelegramClient
from telethon.sessions import StringSession
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# --- Telegram auth ---
api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
channel = os.environ["TG_CHANNEL"]  # ID канала, например: -1002193847502
session_str = os.environ["TG_SESSION"]
yt_token = os.environ["YT_TOKEN"]

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# --- YouTube auth ---
creds = Credentials.from_authorized_user_info(json.loads(yt_token))
youtube = build("youtube", "v3", credentials=creds)

# --- Counter ---
if os.path.exists("counter.json"):
    with open("counter.json", "r") as f:
        counter = json.load(f)
else:
    counter = {"count": 1}

count = counter["count"]

TITLES = [
    "Epic Anime Edit #{num}",
    "🔥 Best Anime Moments #{num}",
    "Sad Anime Edit #{num}",
    "Emotional Anime Scene #{num}",
    "AMV Edit #{num}",
    "Legendary Anime Edit #{num}",
    "Anime Fight Scene #{num}",
    "Cool Anime Transitions #{num}",
    "Anime Music Video #{num}",
    "Top Anime Edit #{num}"
]

DESCRIPTIONS = [
    "Лучшие аниме эдиты для тебя 🚀",
    "Подпишись на канал, если любишь аниме ❤️",
    "Самые красивые сцены в аниме 🎬",
    "Эмоции в каждом кадре ✨",
    "Anime edits for true fans 💯"
]

async def main():
    global count
    try:
        entity = await client.get_entity(int(channel))  # теперь берёт по ID
    except Exception as e:
        print(f"❌ Ошибка при получении канала: {e}")
        return

    async for message in client.iter_messages(entity, limit=1):
        if message.video or (message.document and message.document.mime_type.startswith("video")):
            path = await message.download_media(file="video.mp4")

            if not os.path.exists(path):
                print("❌ Видео не скачалось — пропуск.")
                return

            title = random.choice(TITLES).format(num=count)
            description = random.choice(DESCRIPTIONS)

            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": ["anime", "edit", "shorts"],
                        "categoryId": "22"
                    },
                    "status": {
                        "privacyStatus": "public",
                        "selfDeclaredMadeForKids": False
                    }
                },
                media_body=MediaFileUpload(path, resumable=True)
            )
            request.execute()
            print(f"✅ Загружено: {title}")
            count += 1

    with open("counter.json", "w") as f:
        json.dump({"count": count}, f)

with client:
    client.loop.run_until_complete(main())
