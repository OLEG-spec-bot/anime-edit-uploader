from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("API_ID: "))
api_hash = input("API_HASH: ")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n✅ Сессия создана. СКОПИРУЙ строку ниже и сохрани как секрет TG_SESSION:")
    print(client.session.save())
