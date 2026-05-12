#!/usr/bin/env python3
"""
Upload presentation images and create shared folder in Google Drive
"""
import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from auth_helper import get_credentials_file

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Authenticate and return Google Drive service"""
    creds = None
    drive_token_file = 'token_drive.pickle'

    if os.path.exists(drive_token_file):
        with open(drive_token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(drive_token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def create_presentation_folder(service):
    """Create a folder for presentation files"""
    folder_name = f"設計工作統計簡報 - {datetime.now().strftime('%Y-%m-%d')}"

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = service.files().create(
        body=file_metadata,
        fields='id, webViewLink'
    ).execute()

    return folder.get('id'), folder.get('webViewLink')

def upload_file(service, file_path, folder_id, mimetype='image/png'):
    """Upload a file to Google Drive"""
    if not os.path.exists(file_path):
        return None

    file_name = os.path.basename(file_path)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, name'
    ).execute()

    return file

def main():
    print("📁 建立簡報資料夾並上傳檔案...\n")

    service = get_drive_service()

    # Create folder
    try:
        folder_id, folder_link = create_presentation_folder(service)
        print(f"✓ 資料夾已建立: {folder_link}\n")
    except Exception as e:
        print(f"❌ 建立資料夾失敗: {str(e)}")
        return

    # Files to upload
    files_to_upload = [
        ('presentation_slide_1.png', 'image/png'),
        ('presentation_slide_2.png', 'image/png'),
        ('presentation_summary.png', 'image/png'),
        ('chart_bar.png', 'image/png'),
        ('chart_pie.png', 'image/png'),
        ('chart_table.png', 'image/png'),
        ('chart_category.png', 'image/png'),
    ]

    uploaded_files = []

    print("📤 上傳檔案...")
    for file_name, mimetype in files_to_upload:
        try:
            result = upload_file(service, file_name, folder_id, mimetype)
            if result:
                uploaded_files.append(result)
                print(f"  ✓ {file_name}")
                print(f"    🔗 {result.get('webViewLink')}\n")
        except Exception as e:
            print(f"  ❌ {file_name}: {str(e)}\n")

    print("\n" + "="*60)
    print("✅ 完成！")
    print("="*60)
    print(f"\n📁 簡報資料夾: {folder_link}")
    print(f"\n📊 上傳的檔案：")
    for i, file_info in enumerate(uploaded_files, 1):
        print(f"  {i}. {file_info.get('name')}")

    print(f"\n💡 後續步驟:")
    print("  1. 打開上面的資料夾連結")
    print("  2. 在 Google Drive 中建立新的 Google Slides")
    print("  3. 在幻燈片中插入 → 圖片 → 從 Drive 中選擇")
    print("  4. 選擇上傳的 presentation_*.png 檔案")
    print("  5. 調整大小和位置")
    print("\n或者，直接右鍵複製上面的資料夾連結分享給團隊！")

if __name__ == '__main__':
    main()
