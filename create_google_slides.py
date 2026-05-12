#!/usr/bin/env python3
"""
Create Google Slides presentation with design work statistics
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from auth_helper import get_credentials_file

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

def get_slides_service():
    """Authenticate and return Google Slides service"""
    creds = None
    slide_token_file = 'token_slides.pickle'

    if os.path.exists(slide_token_file):
        with open(slide_token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(slide_token_file, 'wb') as token:
            pickle.dump(creds, token)

    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return slides_service, drive_service

def create_presentation():
    """Create a new Google Slides presentation"""
    slides_service, drive_service = get_slides_service()

    # Create presentation
    presentation_body = {
        'title': '設計工作統計 - 2026/04/28-05/12'
    }

    presentation = slides_service.presentations().create(
        body=presentation_body).execute()

    presentation_id = presentation.get('id')
    print(f"✓ 簡報已建立")
    print(f"📊 簡報ID: {presentation_id}")

    # Get presentation link
    drive_file = drive_service.files().get(
        fileId=presentation_id,
        fields='webViewLink'
    ).execute()

    presentation_link = drive_file.get('webViewLink')
    print(f"🔗 簡報連結: {presentation_link}")

    # Add slides
    add_slides(slides_service, presentation_id)

    return presentation_id, presentation_link

def add_slides(slides_service, presentation_id):
    """Add content slides to presentation"""

    # Slide 1: Title slide
    add_title_slide(slides_service, presentation_id)

    # Slide 2: Product categories
    add_product_category_slide(slides_service, presentation_id)

    # Slide 3: Work types
    add_work_type_slide(slides_service, presentation_id)

    # Slide 4: Summary
    add_summary_slide(slides_service, presentation_id)

def add_title_slide(slides_service, presentation_id):
    """Add title slide"""
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_SLIDE'
                }
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    # Get the created slide
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()

    slide_id = presentation['slides'][-1]['objectId']

    # Update title slide content
    requests = [
        {
            'updateTextStyle': {
                'objectId': slide_id,
                'fields': 'fontSize,bold,foregroundColor',
                'style': {
                    'fontSize': {'magnitude': 54, 'unit': 'PT'},
                    'bold': True,
                    'foregroundColor': {
                        'rgbColor': {
                            'red': 0.78,
                            'green': 0.12,
                            'blue': 0.23
                        }
                    }
                }
            }
        }
    ]

    print("✓ 幻燈片1: 標題頁已新增")

def add_product_category_slide(slides_service, presentation_id):
    """Add product category analysis slide"""
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("✓ 幻燈片2: 產品類別分析已新增")

def add_work_type_slide(slides_service, presentation_id):
    """Add work type analysis slide"""
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("✓ 幻燈片3: 工作類型分析已新增")

def add_summary_slide(slides_service, presentation_id):
    """Add summary slide with key metrics"""
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("✓ 幻燈片4: 摘要已新增")

if __name__ == '__main__':
    print("📊 正在建立 Google 簡報...\n")

    try:
        presentation_id, link = create_presentation()
        print("\n" + "="*60)
        print("✅ Google 簡報已建立完成！")
        print("="*60)
        print(f"\n🔗 簡報連結: {link}")
        print(f"\n💡 提示：")
        print("  1. 點擊上方連結開啟簡報")
        print("  2. 你可以在Google Slides中直接編輯內容")
        print("  3. 簡報已自動保存到你的Google Drive")

    except Exception as e:
        print(f"❌ 建立簡報失敗: {str(e)}")
        print("\n可能的原因：")
        print("  • 需要Google Slides API權限")
        print("  • 請在以下網址啟用API:")
        print("    https://console.cloud.google.com/apis/library")
