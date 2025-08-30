import os
import json
import asyncio
from telethon import TelegramClient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ------------------ НАСТРОЙКИ ------------------
API_ID = int(os.environ["TG_API_ID"])  # Telegram api_id (из GitHub Secrets)
API_HASH = os.environ["TG_API_HASH"]   # Telegram api_hash (из GitHub Secrets)
CHANNEL_USERNAME = os.environ["TG_CHANNEL"]  # Канал (username или ID)

# YouTube token.json будет храниться в секретах
TOKEN_FILE = "token.json"

COUNTER_FILE = "counter.json"
DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ------------------ СЧЁТЧИК ------------------
def get_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            json.dump({"count": 1}, f)
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)["count"]

def update_counter(new_value):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": new_value}, f)

# ------------------ TELEGRAM ------------------
async def download_last_video():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()
    messages = await client.get_messages(CHANNEL_USERNAME, limit=1)

    for msg in messages:
        if msg.video:
            path = await msg.download_media(file=DOWNLOAD_FOLDER)
            print(f"✅ Скачано: {path}")
            return path
    return None

# ------------------ YOUTUBE ------------------
def get_youtube_service():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE, ["https://www.googleapis.com/auth/youtube.upload"]
    )
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path):
    youtube = get_youtube_service()
    count = get_counter()
    title = f"Anime edit #{count}"

    request_body = {
        "snippet": {
            "title": title,
            "description": "Anime edit",
            "tags": ["anime", "edit", "shorts"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print(f"🎬 Загружено: {title}")

    update_counter(count + 1)
    os.remove(video_path)

# ------------------ MAIN ------------------
def main():
    video_path = asyncio.run(download_last_video())
    if video_path:
        upload_to_youtube(video_path)
    else:
        print("⚠️ Видео не найдено.")

if __name__ == "__main__":
    main()
