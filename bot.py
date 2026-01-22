import os
import json
import random
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# ========= ENV =========
api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
channel = os.environ["TG_CHANNEL"]  # @username или ссылка
session_str = os.environ["TG_SESSION"]
yt_token = os.environ["YT_TOKEN"]

# ========= Telegram =========
client = TelegramClient(StringSession(session_str), api_id, api_hash)

# ========= YouTube =========
creds = Credentials.from_authorized_user_info(json.loads(yt_token))
youtube = build("youtube", "v3", credentials=creds)

# ========= STATE =========
if os.path.exists("state.json"):
    state = json.load(open("state.json"))
else:
    state = {"last_message_id": 0}

if os.path.exists("counter.json"):
    counter = json.load(open("counter.json"))
else:
    counter = {"count": 1}

last_id = state["last_message_id"]
count = counter["count"]

# ========= TEXT =========
TITLES = [
    "Epic Anime Edit #{n}",
    "Anime Fight Scene #{n}",
    "Emotional Anime Edit #{n}",
    "Best Anime Moments #{n}",
    "Legendary Anime AMV #{n}",
]

DESCRIPTIONS = [
    "Лучшие аниме эдиты 🔥",
    "Anime edits every hour 🎬",
    "Подпишись если любишь аниме ❤️",
    "Top anime scenes 💯",
]

# ========= MAIN =========
async def main():
    global last_id, count

    entity = await client.get_entity(channel)

    async for msg in client.iter_messages(entity, min_id=last_id, reverse=True):
        if msg.video or (msg.document and msg.document.mime_type.startswith("video")):
            print(f"🎬 Найдено видео ID {msg.id}")

            path = await msg.download_media("video.mp4")

            title = random.choice(TITLES).format(n=count)
            desc = random.choice(DESCRIPTIONS)

            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": desc,
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

            last_id = msg.id
            count += 1
            break
    else:
        print("ℹ️ Новых видео нет")

    json.dump({"last_message_id": last_id}, open("state.json", "w"))
    json.dump({"count": count}, open("counter.json", "w"))

# ========= RUN =========
with client:
    client.loop.run_until_complete(main())


with client:
    client.loop.run_until_complete(main())
