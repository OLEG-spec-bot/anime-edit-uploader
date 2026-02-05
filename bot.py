import os
import json
import random
import time
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

# ========= FILES =========
STATE_FILE = "state.json"
COUNTER_FILE = "counter.json"
RATE_FILE = "rate_limit.json"

# ========= STATE =========
if os.path.exists(STATE_FILE):
    state = json.load(open(STATE_FILE, "r", encoding="utf-8"))
else:
    state = {"last_message_id": 0}

if os.path.exists(COUNTER_FILE):
    counter = json.load(open(COUNTER_FILE, "r", encoding="utf-8"))
else:
    counter = {"count": 1}

if os.path.exists(RATE_FILE):
    rate = json.load(open(RATE_FILE, "r", encoding="utf-8"))
else:
    rate = {"last_upload_ts": 0}

last_id = int(state.get("last_message_id", 0))
count = int(counter.get("count", 1))
last_upload_ts = int(rate.get("last_upload_ts", 0))

# ========= TEXT =========
TITLES = [
    "Epic Anime Edit #{n}",
    "Anime Fight Scene #{n}",
    "Emotional Anime Short #{n}",
    "Best Anime Moments #{n}",
    "Legendary Anime Edit #{n}",
]

DESCRIPTIONS = [
    "Лучшие аниме эдиты 🔥 #Shorts",
    "Anime edits every hour 🎬 #Shorts",
    "Подпишись если любишь аниме ❤️ #Shorts",
    "Top anime scenes 💯 #Shorts",
]

# ========= MAIN =========
async def main():
    global last_id, count, last_upload_ts

    now = int(time.time())

    # --- железный лимит: не чаще 1 раза в час ---
    if now - last_upload_ts < 3600:
        mins = (3600 - (now - last_upload_ts)) // 60
        print(f"⏳ Ещё рано. До следующей загрузки примерно {mins} минут.")
        return

    print("🔍 Ищу канал...")
    entity = await client.get_entity(channel)
    print("✅ Канал найден")

    print("🔍 Ищу следующее новое видео...")
    async for msg in client.iter_messages(entity, min_id=last_id, reverse=True):

        is_video = (
            msg.video
            or (msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"))
        )

        if not is_video:
            continue

        print(f"🎬 Найдено видео ID {msg.id}")
        path = await msg.download_media("video.mp4")
        print(f"📁 Видео скачано: {path}")

        title = random.choice(TITLES).format(n=count)
        desc = random.choice(DESCRIPTIONS)

        print(f"📤 Загружаю на YouTube: {title}")

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": desc,
                    "tags": ["anime", "edit", "shorts", "amv"],
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

        # обновляем прогресс
        last_id = msg.id
        count += 1
        last_upload_ts = now

        break
    else:
        print("ℹ️ Новых видео нет")

    # --- сохраняем ---
    json.dump({"last_message_id": last_id}, open(STATE_FILE, "w", encoding="utf-8"))
    json.dump({"count": count}, open(COUNTER_FILE, "w", encoding="utf-8"))
    json.dump({"last_upload_ts": last_upload_ts}, open(RATE_FILE, "w", encoding="utf-8"))

# ========= RUN =========
with client:
    client.loop.run_until_complete(main())
