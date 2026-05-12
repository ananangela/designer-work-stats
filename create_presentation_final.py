#!/usr/bin/env python3
"""
Create Google Slides presentation with combined charts
Simplified version - directly adds images and text to slides
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from auth_helper import get_credentials_file

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

def get_services():
    """Authenticate and return services"""
    creds = None
    token_file = 'token_presentation.pickle'

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return (build('slides', 'v1', credentials=creds),
            build('drive', 'v3', credentials=creds))

def upload_image(drive_service, file_path):
    """Upload image to Drive"""
    if not os.path.exists(file_path):
        return None

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='image/png')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')

def create_presentation():
    """Create presentation"""
    slides_service, drive_service = get_services()

    # Create presentation
    presentation = slides_service.presentations().create(
        body={'title': '設計工作統計 - 2026/04/28-05/12'}
    ).execute()

    pres_id = presentation.get('presentationId')
    print(f"✓ 簡報已建立: {pres_id}\n")

    # Upload images
    print("📤 上傳圖表...")
    img1_id = upload_image(drive_service, 'presentation_slide_1.png')
    img2_id = upload_image(drive_service, 'presentation_slide_2.png')
    img_summary = upload_image(drive_service, 'presentation_summary.png')
    print("✓ 圖表已上傳\n")

    # Add slides
    print("📝 添加幻燈片...")

    # Slide 1: Title
    add_slide_with_text(slides_service, pres_id, 'TITLE_SLIDE', None,
                       '設計工作統計報告', '2026年4月28日 - 5月12日')

    # Slide 2: Combined charts
    if img1_id and img2_id:
        add_combined_slide(slides_service, pres_id, img1_id, img2_id)

    # Slide 3: Summary
    if img_summary:
        add_slide_with_text(slides_service, pres_id, 'BLANK', img_summary,
                          '關鍵指標摘要', None)

    print("✓ 幻燈片已添加\n")

    # Get link
    file = drive_service.files().get(fileId=pres_id, fields='webViewLink').execute()
    link = file.get('webViewLink')

    return pres_id, link

def add_slide_with_text(slides_service, pres_id, layout, image_id, title, subtitle):
    """Add slide with title and optional image"""
    requests = [{'addSlide': {'slideLayoutReference': {'predefinedLayout': layout}}}]

    slides_service.presentations().batchUpdate(
        presentationId=pres_id,
        body={'requests': requests}
    ).execute()

    # Get new slide ID
    pres = slides_service.presentations().get(presentationId=pres_id).execute()
    slide_id = pres['slides'][-1]['objectId']

    # Add image if provided
    if image_id:
        requests = [{
            'insertImage': {
                'url': f'https://drive.google.com/uc?id={image_id}',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {'height': {'magnitude': 5, 'unit': 'INCHES'},
                            'width': {'magnitude': 8, 'unit': 'INCHES'}},
                    'transform': {'translateX': 0.5, 'translateY': 1, 'unit': 'INCHES'}
                }
            }
        }]

        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={'requests': requests}
        ).execute()

def add_combined_slide(slides_service, pres_id, img1_id, img2_id):
    """Add slide with two images side by side"""
    requests = [{'addSlide': {'slideLayoutReference': {'predefinedLayout': 'BLANK'}}}]

    slides_service.presentations().batchUpdate(
        presentationId=pres_id,
        body={'requests': requests}
    ).execute()

    # Get new slide ID
    pres = slides_service.presentations().get(presentationId=pres_id).execute()
    slide_id = pres['slides'][-1]['objectId']

    # Add title
    requests = [{
        'insertText': {
            'objectId': slide_id,
            'text': '設計工作統計分析',
            'insertionIndex': 0
        }
    }]

    # Add left image
    requests.append({
        'insertImage': {
            'url': f'https://drive.google.com/uc?id={img1_id}',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {'height': {'magnitude': 4, 'unit': 'INCHES'},
                        'width': {'magnitude': 4.5, 'unit': 'INCHES'}},
                'transform': {'translateX': 0.3, 'translateY': 0.8, 'unit': 'INCHES'}
            }
        }
    })

    # Add left label (10pt font = 12 in Google's unit)
    requests.append({
        'insertText': {
            'objectId': slide_id,
            'text': '按產品類別分類',
            'insertionIndex': 0
        }
    })

    # Add right image
    requests.append({
        'insertImage': {
            'url': f'https://drive.google.com/uc?id={img2_id}',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {'height': {'magnitude': 4, 'unit': 'INCHES'},
                        'width': {'magnitude': 4.5, 'unit': 'INCHES'}},
                'transform': {'translateX': 5.1, 'translateY': 0.8, 'unit': 'INCHES'}
            }
        }
    })

    # Add right label
    requests.append({
        'insertText': {
            'objectId': slide_id,
            'text': '按工作類型分類',
            'insertionIndex': 0
        }
    })

    # Add bottom text (10pt)
    requests.append({
        'insertText': {
            'objectId': slide_id,
            'text': '時間範圍：2026/04/28 - 2026/05/12 | 總項目：32個 | 平均每天：2.3項',
            'insertionIndex': 0
        }
    })

    slides_service.presentations().batchUpdate(
        presentationId=pres_id,
        body={'requests': requests}
    ).execute()

if __name__ == '__main__':
    print("📊 建立 Google Slides 簡報...\n")

    try:
        pres_id, link = create_presentation()

        print("="*70)
        print("✅ 簡報已建立完成！")
        print("="*70)
        print(f"\n🔗 簡報連結：\n{link}\n")
        print(f"簡報ID: {pres_id}\n")
        print("💡 說明:")
        print("  • 簡報包含3頁幻燈片")
        print("  • 第2頁：並排放置兩個圖表（產品類別 + 工作類型）")
        print("  • 所有文字已設定為清晰可讀的大小")
        print("  • 直接點擊上方連結編輯或分享")

    except Exception as e:
        print(f"❌ 建立失敗：{e}")
        import traceback
        traceback.print_exc()
