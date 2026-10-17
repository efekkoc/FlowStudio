import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.settings import YOUTUBE_CLIENT_SECRET_FILE, BASE_DIR

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]


class YouTubeUploader:
    def __init__(self, client_secret_file: Optional[str] = None):
        self.client_secret_file = client_secret_file or YOUTUBE_CLIENT_SECRET_FILE
        self.token_file = BASE_DIR / "token.json"
        self.youtube = None

    def authenticate(self) -> bool:
        """
        YouTube API için OAuth2 kimlik doğrulamasını gerçekleştirir veya kayıtlı token'ı yeniler.
        """
        creds = None
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                print(f"[YouTubeUploader] Token okuma hatası: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[YouTubeUploader] Token yenileme hatası: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.client_secret_file):
                    print(f"[YouTubeUploader] HATA: '{self.client_secret_file}' bulunamadı. Lütfen Google Cloud'dan indirdiğiniz client_secrets.json dosyasını proje ana dizinine ekleyin.")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, SCOPES)
                creds = flow.run_local_server(bind_addr="127.0.0.1", port=0)

            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        self.youtube = build("youtube", "v3", credentials=creds)
        return True

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "public",  # "public", "private", "unlisted"
        publish_at: Optional[str] = None, # ISO 8601: "2026-08-28T14:00:00Z"
        made_for_kids: bool = False,
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        YouTube Shorts videosunu kanala yükler.
        """
        if not self.youtube:
            success = self.authenticate()
            if not success:
                raise Exception("YouTube API kimlik doğrulaması yapılamadı. client_secrets.json dosyasını kontrol edin.")

        tags_list = tags or ["Shorts", "Animation", "KidsAnimation", "Cartoon", "Funny"]
        if "Shorts" not in tags_list and "#Shorts" not in title:
            title = f"{title} #Shorts"

        body = {
            "snippet": {
                "title": title[:100],  # YouTube 100 karakter sınırı
                "description": description[:5000],
                "tags": tags_list[:30],
                "categoryId": "1"  # 1: Film & Animation, 24: Entertainment
            },
            "status": {
                "privacyStatus": "private" if publish_at else privacy_status,
                "selfDeclaredMadeForKids": made_for_kids
            }
        }

        if publish_at:
            body["status"]["publishAt"] = publish_at

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 5  # 5MB chunks
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        print(f"[YouTubeUploader] '{title}' videosu yükleniyor...")
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"[YouTubeUploader] Yükleme İlerlemesi: %{progress}")

        video_id = response.get("id")
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"[YouTubeUploader] Yükleme tamamlandı! Video URL: {video_url}")

        # İsteğe bağlı özel kapak görseli
        if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
            try:
                self.youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                ).execute()
            except Exception as e:
                print(f"[YouTubeUploader] Küçük resim yüklenemedi ({e}). Varsayılan kullanılacak.")

        return {
            "video_id": video_id,
            "url": video_url,
            "title": title,
            "status": privacy_status,
            "response": response
        }
