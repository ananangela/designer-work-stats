#!/usr/bin/env python3
"""
Create Google Slides presentation with combined charts on single page
Directly uses Google Slides API to create and format slides
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
    """Authenticate and return Google Slides and Drive services"""
    creds = None
    combined_token_file = 'token_combined.pickle'

    if os.path.exists(combined_token_file):
        with open(combined_token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(combined_token_file, 'wb') as token:
            pickle.dump(creds, token)

    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return slides_service, drive_service

def upload_image_to_drive(drive_service, image_path):
    """Upload image to Google Drive and return file ID"""
    if not os.path.exists(image_path):
        print(f"❌ 檔案不存在: {image_path}")
        return None

    file_name = os.path.basename(image_path)
    file_metadata = {'name': file_name}

    media = MediaFileUpload(image_path, mimetype='image/png')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')

def create_presentation():
    """Create Google Slides presentation with combined charts"""
    slides_service, drive_service = get_services()

    # Create presentation
    presentation_body = {
        'title': '設計工作統計報告 - 2026/04/28-05/12'
    }

    try:
        presentation = slides_service.presentations().create(
            body=presentation_body).execute()
    except Exception as e:
        print(f"❌ 建立簡報時出現錯誤: {str(e)}")
        return None, None

    presentation_id = presentation.get('presentationId')

    if not presentation_id:
        print(f"❌ 無法取得簡報 ID")
        print(f"   響應: {presentation}")
        return None, None

    print(f"✓ 簡報已建立")
    print(f"  ID: {presentation_id}\n")

    # Upload images to Drive
    print("📤 上傳圖表到 Google Drive...")
    slide1_id = upload_image_to_drive(drive_service, 'presentation_slide_1.png')
    slide2_id = upload_image_to_drive(drive_service, 'presentation_slide_2.png')
    summary_id = upload_image_to_drive(drive_service, 'presentation_summary.png')

    if slide1_id:
        print(f"  ✓ presentation_slide_1.png")
    if slide2_id:
        print(f"  ✓ presentation_slide_2.png")
    if summary_id:
        print(f"  ✓ presentation_summary.png\n")

    # Add slides
    print("📝 添加幻燈片...")
    try:
        add_title_slide(slides_service, presentation_id)
        add_combined_chart_slide(slides_service, presentation_id, slide1_id, slide2_id)
        add_summary_slide(slides_service, presentation_id, summary_id)
    except Exception as e:
        print(f"❌ 添加幻燈片時出現錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

    # Get presentation link
    try:
        file = drive_service.files().get(
            fileId=presentation_id,
            fields='webViewLink'
        ).execute()
        presentation_link = file.get('webViewLink')
    except Exception as e:
        print(f"❌ 取得簡報連結時出現錯誤: {str(e)}")
        presentation_link = f"https://docs.google.com/presentation/d/{presentation_id}"

    return presentation_id, presentation_link

def add_title_slide(slides_service, presentation_id):
    """Add title slide"""
    # Get blank layout
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()

    slide_layouts = presentation['slides'][0]['slideLayout']['layoutProperties']

    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_SLIDE'
                }
            }
        }
    ]

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("  ✓ 標題幻燈片已添加")

def add_combined_chart_slide(slides_service, presentation_id, image1_id, image2_id):
    """Add slide with both charts side by side"""
    # Add blank slide
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        }
    ]

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    # Get the new slide ID
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()

    slide_id = presentation['slides'][-1]['objectId']

    # Add title
    requests = [
        {
            'insertText': {
                'objectId': slide_id,
                'text': '設計工作統計分析',
                'insertionIndex': 0
            }
        }
    ]

    # Add left image (product categories)
    if image1_id:
        requests.extend([
            {
                'insertImage': {
                    'url': f'https://drive.google.com/uc?id={image1_id}',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'height': {'magnitude': 3.5, 'unit': 'INCHES'},
                            'width': {'magnitude': 5.5, 'unit': 'INCHES'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 0.3,
                            'translateY': 0.8,
                            'unit': 'INCHES'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': slide_id,
                    'text': '按產品類別分類',
                    'insertionIndex': 0
                }
            }
        ])

    # Add right image (work types)
    if image2_id:
        requests.extend([
            {
                'insertImage': {
                    'url': f'https://drive.google.com/uc?id={image2_id}',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'height': {'magnitude': 3.5, 'unit': 'INCHES'},
                            'width': {'magnitude': 5.5, 'unit': 'INCHES'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 6.3,
                            'translateY': 0.8,
                            'unit': 'INCHES'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': slide_id,
                    'text': '按工作類型分類',
                    'insertionIndex': 0
                }
            }
        ])

    # Add timestamp and summary
    requests.extend([
        {
            'insertText': {
                'objectId': slide_id,
                'text': '時間範圍：2026/04/28 - 2026/05/12 | 總項目：32個',
                'insertionIndex': 0
            }
        }
    ])

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("  ✓ 組合圖表幻燈片已添加")

def add_summary_slide(slides_service, presentation_id, summary_id):
    """Add summary slide"""
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        }
    ]

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    # Get the new slide ID
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()

    slide_id = presentation['slides'][-1]['objectId']

    # Add title
    requests = [
        {
            'insertText': {
                'objectId': slide_id,
                'text': '關鍵指標摘要',
                'insertionIndex': 0
            }
        }
    ]

    # Add summary image
    if summary_id:
        requests.append({
            'insertImage': {
                'url': f'https://drive.google.com/uc?id={summary_id}',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': 5, 'unit': 'INCHES'},
                        'width': {'magnitude': 8, 'unit': 'INCHES'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': 1,
                        'translateY': 1,
                        'unit': 'INCHES'
                    }
                }
            }
        })

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print("  ✓ 摘要幻燈片已添加")

if __name__ == '__main__':
    print("📊 正在建立 Google Slides 簡報...\n")

    try:
        presentation_id, presentation_link = create_presentation()

        print("\n" + "="*70)
        print("✅ Google Slides 簡報已建立完成！")
        print("="*70)
        print(f"\n🔗 簡報連結: {presentation_link}")
        print(f"\n💡 提示：")
        print("  • 簡報已自動建立並包含所有圖表")
        print("  • 點擊上方連結即可打開編輯")
        print("  • 所有圖表已格式化在各自的幻燈片上")
        print("  • 可以直接分享此連結給團隊")

    except Exception as e:
        print(f"❌ 建立簡報失敗: {str(e)}")
        import traceback
        traceback.print_exc()
