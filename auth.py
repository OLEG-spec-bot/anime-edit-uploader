import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# права доступа (обязательно с youtube.upload)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    # сохраняем token.json
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    print("✅ Авторизация прошла успешно. Файл token.json сохранён.")

if __name__ == "__main__":
    main()
