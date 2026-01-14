import os
import pickle
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==============================
# KONFIGURASI
# ==============================
FOLDER_ID = "1nKSO2v_YWZn1EE1HMvEP_rM9EqrHkQV2"  # Folder Drive kamu
MAX_SIZE_MB = 500  # batas aman size video

# ==============================
# LOGIN GOOGLE
# ==============================
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

# ==============================
# AMBIL 1 VIDEO TERLAMA (FIFO)
# ==============================
print("🔍 Mengecek folder Drive...")

file_list = drive.ListFile({
    'q': f"'{FOLDER_ID}' in parents and trashed=false",
    'orderBy': 'createdDate asc'
}).GetList()

if not file_list:
    print("❌ Tidak ada video di folder. Skip waktu ini.")
    exit(0)

video = file_list[0]  # VIDEO TERLAMA

print("📥 Mengambil:", video['title'])

# ==============================
# DOWNLOAD VIDEO
# ==============================
LOCAL_FILE = "video.mp4"
video.GetContentFile(LOCAL_FILE)

# ==============================
# CEK UKURAN FILE
# ==============================
size_mb = os.path.getsize(LOCAL_FILE) / (1024 * 1024)

if size_mb > MAX_SIZE_MB:
    print("❌ File terlalu besar:", round(size_mb, 2), "MB")
    os.remove(LOCAL_FILE)
    exit(0)

# ==============================
# UPLOAD KE YOUTUBE
# ==============================
print("🚀 Upload ke YouTube...")

youtube = build("youtube", "v3", credentials=gauth.credentials)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": video['title'],  # JUDUL = NAMA FILE
            "description": "#shorts",
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"  # LANGSUNG PUBLIC
        }
    },
    media_body=MediaFileUpload(LOCAL_FILE, resumable=True)
)

response = request.execute()

print("✅ Upload sukses! Video ID:", response.get("id"))

# ==============================
# HAPUS VIDEO DARI DRIVE (ANTRIAN LANJUT)
# ==============================
video.Delete()
print("🗑️ Video dihapus dari Drive (antrian lanjut).")

# ==============================
# BERSIHKAN FILE LOKAL
# ==============================
if os.path.exists(LOCAL_FILE):
    os.remove(LOCAL_FILE)

print("🎉 Selesai 1 video.")
