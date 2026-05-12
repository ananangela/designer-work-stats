#!/usr/bin/env python3
"""
Create and upload final presentation to Google Slides
Generates combined image locally, then uploads to prepared presentation
"""
import os
import pickle
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image
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
    """Get authenticated services"""
    creds = None
    token_file = 'token_final.pickle'

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

def create_combined_image():
    """Create combined image with both charts side by side"""
    print("🎨 組合圖表...")

    # Load images
    try:
        img1 = Image.open('presentation_slide_1.png')
        img2 = Image.open('presentation_slide_2.png')
    except FileNotFoundError as e:
        print(f"❌ 圖表檔案不存在: {e}")
        return None

    # Create figure
    fig = plt.figure(figsize=(14, 6))
    fig.patch.set_facecolor('white')

    # Add title
    fig.text(0.5, 0.98, '設計工作統計分析',
             ha='center', fontsize=16, fontweight='bold')

    # Create grid for images
    gs = GridSpec(2, 2, figure=fig, height_ratios=[3, 0.3],
                  hspace=0.15, wspace=0.15,
                  left=0.05, right=0.95, top=0.92, bottom=0.1)

    # Left image
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(img1)
    ax1.axis('off')

    # Right image
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(img2)
    ax2.axis('off')

    # Left label
    ax_label_left = fig.add_subplot(gs[1, 0])
    ax_label_left.axis('off')
    ax_label_left.text(0.5, 0.5, '按產品類別分類',
                      ha='center', va='center', fontsize=10, fontweight='bold')

    # Right label
    ax_label_right = fig.add_subplot(gs[1, 1])
    ax_label_right.axis('off')
    ax_label_right.text(0.5, 0.5, '按工作類型分類',
                       ha='center', va='center', fontsize=10, fontweight='bold')

    # Bottom info
    fig.text(0.5, 0.02, '時間範圍：2026/04/28 - 2026/05/12 | 總工作項目：32個 | 平均每天：2.3項',
             ha='center', fontsize=10)

    # Save
    output_file = 'combined_presentation.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✓ 組合圖表已生成: {output_file}\n")
    return output_file

def upload_combined_image_to_slides(slides_service, drive_service, image_file):
    """Upload combined image to Google Slides presentation"""

    # Create new presentation
    print("📝 建立 Google Slides 簡報...")
    pres = slides_service.presentations().create(
        body={'title': '設計工作統計 - 2026/04/28-05/12'}
    ).execute()

    pres_id = pres.get('presentationId')
    print(f"✓ 簡報已建立\n")

    # Upload image to Drive
    print("📤 上傳圖表到 Google Drive...")
    file_metadata = {'name': os.path.basename(image_file)}
    media = MediaFileUpload(image_file, mimetype='image/png')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    img_id = file.get('id')
    img_url = f'https://drive.google.com/uc?id={img_id}'
    print(f"✓ 圖表已上傳\n")

    # Add slide with image
    print("📐 添加圖表到簡報...")
    requests = [
        {
            'addSlide': {
                'slideLayoutReference': {'predefinedLayout': 'BLANK'}
            }
        }
    ]

    response = slides_service.presentations().batchUpdate(
        presentationId=pres_id,
        body={'requests': requests}
    ).execute()

    # Get slide ID
    pres_data = slides_service.presentations().get(
        presentationId=pres_id).execute()

    slide_id = pres_data['slides'][-1]['objectId']

    # Insert image
    insert_requests = [
        {
            'insertImage': {
                'url': img_url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': 9144000, 'unit': 'EMU'},   # 10 inches
                        'height': {'magnitude': 5715000, 'unit': 'EMU'}   # 6.25 inches
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': 0,
                        'translateY': 0,
                        'unit': 'EMU'
                    }
                }
            }
        }
    ]

    try:
        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={'requests': insert_requests}
        ).execute()
        print(f"✓ 圖表已添加到簡報\n")
    except Exception as e:
        print(f"⚠️  圖表添加有誤: {e}")
        print("   但簡報已建立，可以手動添加圖表\n")

    # Get link
    try:
        file_info = drive_service.files().get(
            fileId=pres_id,
            fields='webViewLink'
        ).execute()
        link = file_info.get('webViewLink')
    except:
        link = f"https://docs.google.com/presentation/d/{pres_id}/edit"

    return pres_id, link

def main():
    """Main workflow"""
    print("🎬 開始製作簡報...\n")

    # Create combined image
    image_file = create_combined_image()
    if not image_file:
        print("❌ 無法建立組合圖表")
        return

    # Get services
    slides_service, drive_service = get_services()

    # Upload to Slides
    try:
        pres_id, link = upload_combined_image_to_slides(
            slides_service, drive_service, image_file)

        print("="*70)
        print("✅ Google Slides 簡報已完成！")
        print("="*70)
        print(f"\n🔗 簡報連結：\n{link}\n")
        print("✨ 簡報特點：")
        print("  ✓ 兩張圖表並排顯示")
        print("  ✓ 清晰的 10pt 文字標籤")
        print("  ✓ 完整的統計信息")
        print("  ✓ 可直接編輯和分享")
        print(f"\n簡報ID: {pres_id}")

    except Exception as e:
        print(f"❌ 出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
