import os
import pickle
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FOLDER_ID = "ISI_ID_FOLDER_DRIVE_KAMU_DI_SINI"

# ===== LOGIN =====
gauth = GoogleAuth()

if os.path.exists("token.pickle"):
    gauth.LoadCredentialsFile("token.pickle")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("token.pickle")

drive = GoogleDrive(gauth)

# ===== AMBIL VIDEO =====
file_list = drive.ListFile({
    'q': f"'{FOLDER_ID}' in parents and trashed=false"
}).GetList()

if not file_list:
    print("Tidak ada video")
    exit()

video = file_list[0]
print("Download:", video['title'])
video.GetContentFile("video.mp4")

# ===== UPLOAD KE YOUTUBE =====
youtube = build("youtube", "v3", credentials=gauth.credentials)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": video['title'],
            "description": "#shorts",
            "tags": ["shorts"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=MediaFileUpload("video.mp4", resumable=True)
)

response = request.execute()
print("Uploaded:", response["id"])

# ===== HAPUS DARI DRIVE =====
video.Delete()
print("Selesai.")
