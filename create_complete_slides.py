#!/usr/bin/env python3
"""
Create complete Google Slides presentation with combined charts
Directly creates and formats the presentation without manual steps
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from auth_helper import get_credentials_file
import uuid

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

def get_services():
    """Get authenticated services"""
    creds = None
    token_file = 'token_complete.pickle'

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
    """Upload image to Drive and return URL"""
    if not os.path.exists(file_path):
        print(f"❌ 檔案不存在: {file_path}")
        return None

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='image/png')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    return f'https://drive.google.com/uc?id={file_id}'

def pt_to_emu(pt):
    """Convert points to EMU (English Metric Units)"""
    return int(pt * 12700)

def inches_to_emu(inches):
    """Convert inches to EMU"""
    return int(inches * 914400)

def create_presentation():
    """Create complete Google Slides presentation"""
    slides_service, drive_service = get_services()

    # Create presentation
    presentation = slides_service.presentations().create(
        body={'title': '設計工作統計 - 2026/04/28-05/12'}
    ).execute()

    pres_id = presentation.get('presentationId')
    if not pres_id:
        print("❌ 無法建立簡報")
        return None, None

    print(f"✓ 簡報已建立")
    print(f"  ID: {pres_id}\n")

    # Upload images
    print("📤 上傳圖表到 Google Drive...")
    img1_url = upload_image(drive_service, 'presentation_slide_1.png')
    img2_url = upload_image(drive_service, 'presentation_slide_2.png')
    print("✓ 圖表已上傳\n")

    # Build slide with images and text
    print("📝 設計幻燈片布局...")
    requests = []

    # Add blank slide
    blank_slide_id = str(uuid.uuid4())
    requests.append({
        'createSlide': {
            'objectId': blank_slide_id,
            'slideLayoutReference': {
                'predefinedLayout': 'BLANK'
            }
        }
    })

    # Add title
    title_box_id = str(uuid.uuid4())
    requests.append({
        'insertShape': {
            'objectId': title_box_id,
            'elementProperties': {
                'pageObjectId': blank_slide_id,
                'size': {
                    'width': {'magnitude': inches_to_emu(9), 'unit': 'EMU'},
                    'height': {'magnitude': inches_to_emu(0.5), 'unit': 'EMU'}
                },
                'transform': {
                    'translateX': {'magnitude': 0, 'unit': 'EMU'},
                    'translateY': {'magnitude': 0, 'unit': 'EMU'}
                }
            },
            'shapeType': 'TEXT_BOX'
        }
    })

    requests.append({
        'insertText': {
            'objectId': title_box_id,
            'text': '設計工作統計分析'
        }
    })

    # Format title (14pt, bold)
    requests.append({
        'updateTextStyle': {
            'objectId': title_box_id,
            'style': {
                'fontSize': {'magnitude': pt_to_emu(14), 'unit': 'EMU'},
                'bold': True
            },
            'fields': 'fontSize,bold'
        }
    })

    # Left image
    if img1_url:
        left_img_id = str(uuid.uuid4())
        requests.append({
            'insertImage': {
                'url': img1_url,
                'objectId': left_img_id,
                'elementProperties': {
                    'pageObjectId': blank_slide_id,
                    'size': {
                        'width': {'magnitude': inches_to_emu(4.5), 'unit': 'EMU'},
                        'height': {'magnitude': inches_to_emu(3.5), 'unit': 'EMU'}
                    },
                    'transform': {
                        'translateX': {'magnitude': inches_to_emu(0.3), 'unit': 'EMU'},
                        'translateY': {'magnitude': inches_to_emu(0.6), 'unit': 'EMU'}
                    }
                }
            }
        })

    # Right image
    if img2_url:
        right_img_id = str(uuid.uuid4())
        requests.append({
            'insertImage': {
                'url': img2_url,
                'objectId': right_img_id,
                'elementProperties': {
                    'pageObjectId': blank_slide_id,
                    'size': {
                        'width': {'magnitude': inches_to_emu(4.5), 'unit': 'EMU'},
                        'height': {'magnitude': inches_to_emu(3.5), 'unit': 'EMU'}
                    },
                    'transform': {
                        'translateX': {'magnitude': inches_to_emu(5.1), 'unit': 'EMU'},
                        'translateY': {'magnitude': inches_to_emu(0.6), 'unit': 'EMU'}
                    }
                }
            }
        })

    # Left label (10pt)
    left_label_id = str(uuid.uuid4())
    requests.append({
        'insertShape': {
            'objectId': left_label_id,
            'elementProperties': {
                'pageObjectId': blank_slide_id,
                'size': {
                    'width': {'magnitude': inches_to_emu(4.5), 'unit': 'EMU'},
                    'height': {'magnitude': inches_to_emu(0.3), 'unit': 'EMU'}
                },
                'transform': {
                    'translateX': {'magnitude': inches_to_emu(0.3), 'unit': 'EMU'},
                    'translateY': {'magnitude': inches_to_emu(4.2), 'unit': 'EMU'}
                }
            },
            'shapeType': 'TEXT_BOX'
        }
    })

    requests.append({
        'insertText': {
            'objectId': left_label_id,
            'text': '按產品類別分類'
        }
    })

    requests.append({
        'updateTextStyle': {
            'objectId': left_label_id,
            'style': {
                'fontSize': {'magnitude': pt_to_emu(10), 'unit': 'EMU'},
                'bold': True
            },
            'fields': 'fontSize,bold'
        }
    })

    # Right label (10pt)
    right_label_id = str(uuid.uuid4())
    requests.append({
        'insertShape': {
            'objectId': right_label_id,
            'elementProperties': {
                'pageObjectId': blank_slide_id,
                'size': {
                    'width': {'magnitude': inches_to_emu(4.5), 'unit': 'EMU'},
                    'height': {'magnitude': inches_to_emu(0.3), 'unit': 'EMU'}
                },
                'transform': {
                    'translateX': {'magnitude': inches_to_emu(5.1), 'unit': 'EMU'},
                    'translateY': {'magnitude': inches_to_emu(4.2), 'unit': 'EMU'}
                }
            },
            'shapeType': 'TEXT_BOX'
        }
    })

    requests.append({
        'insertText': {
            'objectId': right_label_id,
            'text': '按工作類型分類'
        }
    })

    requests.append({
        'updateTextStyle': {
            'objectId': right_label_id,
            'style': {
                'fontSize': {'magnitude': pt_to_emu(10), 'unit': 'EMU'},
                'bold': True
            },
            'fields': 'fontSize,bold'
        }
    })

    # Bottom info text (10pt)
    bottom_text_id = str(uuid.uuid4())
    requests.append({
        'insertShape': {
            'objectId': bottom_text_id,
            'elementProperties': {
                'pageObjectId': blank_slide_id,
                'size': {
                    'width': {'magnitude': inches_to_emu(9), 'unit': 'EMU'},
                    'height': {'magnitude': inches_to_emu(0.4), 'unit': 'EMU'}
                },
                'transform': {
                    'translateX': {'magnitude': inches_to_emu(0.3), 'unit': 'EMU'},
                    'translateY': {'magnitude': inches_to_emu(4.7), 'unit': 'EMU'}
                }
            },
            'shapeType': 'TEXT_BOX'
        }
    })

    requests.append({
        'insertText': {
            'objectId': bottom_text_id,
            'text': '時間範圍：2026/04/28 - 2026/05/12 | 總工作項目：32項 | 平均每天：2.3項'
        }
    })

    requests.append({
        'updateTextStyle': {
            'objectId': bottom_text_id,
            'style': {
                'fontSize': {'magnitude': pt_to_emu(10), 'unit': 'EMU'}
            },
            'fields': 'fontSize'
        }
    })

    # Execute all requests
    try:
        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={'requests': requests}
        ).execute()
        print("✓ 幻燈片已完成\n")
    except Exception as e:
        print(f"❌ 幻燈片設計出錯: {e}")
        return pres_id, None

    # Get link
    try:
        file = drive_service.files().get(
            fileId=pres_id,
            fields='webViewLink'
        ).execute()
        link = file.get('webViewLink')
    except:
        link = f"https://docs.google.com/presentation/d/{pres_id}/edit"

    return pres_id, link

if __name__ == '__main__':
    print("📊 製作 Google Slides 簡報...\n")

    try:
        pres_id, link = create_presentation()

        if pres_id and link:
            print("="*70)
            print("✅ 簡報已完成！")
            print("="*70)
            print(f"\n🔗 簡報連結：\n{link}\n")
            print("✨ 特點：")
            print("  ✓ 兩張圖表並排放置")
            print("  ✓ 清晰的 10pt 文字標籤")
            print("  ✓ 完整的統計信息")
            print("  ✓ 可直接編輯和分享")
        else:
            print("❌ 簡報製作失敗")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
