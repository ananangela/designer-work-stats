#!/usr/bin/env python3
"""
Google Drive uploader for design work statistics charts
"""
import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Authenticate and return Google Drive service"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def create_date_folder(service, parent_folder_id):
    """Create a folder with today's date in parent folder"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if folder already exists
    query = f"name='{today}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', pageSize=1, fields='files(id, name)').execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']

    # Create new folder
    file_metadata = {
        'name': today,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_drive(service, file_path, folder_id):
    """Upload a file to Google Drive folder"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    file_name = os.path.basename(file_path)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='image/png')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return file

def upload_charts_to_drive(parent_folder_id):
    """Upload generated charts to Google Drive"""
    service = get_drive_service()

    # Create date-based folder
    date_folder_id = create_date_folder(service, parent_folder_id)
    print(f"📁 Created/found folder: {datetime.now().strftime('%Y-%m-%d')}")

    # Files to upload
    files_to_upload = [
        'chart_bar.png',
        'chart_pie.png',
        'chart_table.png'
    ]

    uploaded_files = []
    for file_name in files_to_upload:
        if os.path.exists(file_name):
            try:
                result = upload_file_to_drive(service, file_name, date_folder_id)
                if result:
                    uploaded_files.append({
                        'name': file_name,
                        'id': result.get('id'),
                        'link': result.get('webViewLink')
                    })
                    print(f"✅ Uploaded: {file_name}")
            except Exception as e:
                print(f"❌ Failed to upload {file_name}: {str(e)}")
        else:
            print(f"⚠️  File not found: {file_name}")

    return uploaded_files

if __name__ == '__main__':
    # Test: upload to specific folder
    # Replace with actual folder ID
    FOLDER_ID = '16RwtvEIZFYwelmTQunLAk9K5H5O8J4tM'
    upload_charts_to_drive(FOLDER_ID)
