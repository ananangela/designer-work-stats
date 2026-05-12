#!/usr/bin/env python3
"""
Create Google Sheets with design work statistics for easy Slides integration
"""
import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from auth_helper import get_credentials_file

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheets_service():
    """Authenticate and return Google Sheets service"""
    creds = None
    sheets_token_file = 'token_sheets.pickle'

    if os.path.exists(sheets_token_file):
        with open(sheets_token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(sheets_token_file, 'wb') as token:
            pickle.dump(creds, token)

    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service

def create_summary_sheet():
    """Create a Google Sheet with design work statistics summary"""
    sheets_service, drive_service = get_sheets_service()

    # Create spreadsheet
    spreadsheet_body = {
        'properties': {
            'title': '設計工作統計總結 - 2026/04/28-05/12'
        }
    }

    spreadsheet = sheets_service.spreadsheets().create(
        body=spreadsheet_body).execute()

    spreadsheet_id = spreadsheet.get('id')
    print(f"✓ Google Sheet已建立")
    print(f"📊 Sheet ID: {spreadsheet_id}")

    # Get the sheet link
    drive_file = drive_service.files().get(
        fileId=spreadsheet_id,
        fields='webViewLink'
    ).execute()

    sheet_link = drive_file.get('webViewLink')
    print(f"🔗 Sheet連結: {sheet_link}")

    # Add data to sheets
    add_data_to_sheet(sheets_service, spreadsheet_id)

    return spreadsheet_id, sheet_link

def add_data_to_sheet(sheets_service, spreadsheet_id):
    """Add design work statistics to the sheet"""

    # Data from statistics
    product_categories = [
        ['產品類別', '工作項目數', '百分比'],
        ['課程', 12, '37.5%'],
        ['產業研究報告', 8, '25.0%'],
        ['大眾產品組合', 5, '15.6%'],
        ['籌碼K線', 3, '9.4%'],
        ['其他', 2, '6.3%'],
        ['起漲K線', 1, '3.1%'],
        ['跨職能', 1, '3.1%'],
        ['', '', ''],
        ['合計', 32, '100%']
    ]

    work_types = [
        ['工作類型', '工作項目數', '百分比'],
        ['行銷圖', 16, '43.2%'],
        ['短影音', 9, '24.3%'],
        ['素材處理', 5, '13.5%'],
        ['跨職能', 3, '8.1%'],
        ['商品頁', 2, '5.4%'],
        ['動畫', 2, '5.4%'],
        ['', '', ''],
        ['合計', 37, '100%']
    ]

    # Prepare update requests
    requests = [
        {
            'pasteData': {
                'data': format_data_for_sheets(product_categories),
                'coordinate': {
                    'sheetId': 0,
                    'rowIndex': 0,
                    'columnIndex': 0
                }
            }
        },
        {
            'pasteData': {
                'data': format_data_for_sheets(work_types),
                'coordinate': {
                    'sheetId': 0,
                    'rowIndex': 0,
                    'columnIndex': 4
                }
            }
        }
    ]

    # Format headers
    requests.extend(format_headers(spreadsheet_id))

    # Execute updates
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    # Add summary section
    add_summary_section(sheets_service, spreadsheet_id)

    print("✓ 數據已添加到 Google Sheet")

def format_data_for_sheets(data):
    """Convert data to Google Sheets format"""
    formatted_data = []
    for row in data:
        formatted_row = []
        for cell in row:
            formatted_row.append({
                'userEnteredValue': {'stringValue': str(cell)}
            })
        formatted_data.append({'values': formatted_row})

    return '\n'.join([str(row) for row in formatted_data])

def format_headers(spreadsheet_id):
    """Format header rows"""
    return [
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 3
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.78,
                            'green': 0.12,
                            'blue': 0.23
                        },
                        'textFormat': {
                            'foregroundColor': {
                                'red': 1,
                                'green': 1,
                                'blue': 1
                            },
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 4,
                    'endColumnIndex': 7
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.78,
                            'green': 0.12,
                            'blue': 0.23
                        },
                        'textFormat': {
                            'foregroundColor': {
                                'red': 1,
                                'green': 1,
                                'blue': 1
                            },
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        }
    ]

def add_summary_section(sheets_service, spreadsheet_id):
    """Add summary metrics section"""
    summary_data = [
        ['', 'KEY METRICS'],
        ['統計期間', '2026/04/28 - 2026/05/12'],
        ['總工作項目', '32項'],
        ['天數', '14天'],
        ['日均工作項目', '2.3項'],
        ['主要工作類別', '課程（37.5%）'],
        ['主要工作類型', '行銷圖（43.2%）']
    ]

    requests = [
        {
            'pasteData': {
                'data': summary_data,
                'coordinate': {
                    'sheetId': 0,
                    'rowIndex': 12,
                    'columnIndex': 0
                }
            }
        }
    ]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    print("✓ 摘要信息已添加")

if __name__ == '__main__':
    print("📊 正在建立 Google Sheet...\n")

    try:
        sheet_id, link = create_summary_sheet()
        print("\n" + "="*60)
        print("✅ Google Sheet 已建立完成！")
        print("="*60)
        print(f"\n🔗 Sheet連結: {link}")
        print(f"\n💡 後續步驟:")
        print("  1. 點擊上方連結開啟 Google Sheet")
        print("  2. 複製表格資料")
        print("  3. 在 Google Slides 中插入 → 表格，貼上資料")
        print("  4. 或使用我們生成的圖表 (presentation_*.png)")

    except Exception as e:
        print(f"❌ 建立 Sheet 失敗: {str(e)}")
