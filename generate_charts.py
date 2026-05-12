#!/usr/bin/env python3
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 設定中文字體
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1K3VVKGJn47UTxGy7UGQtnkrO5yDVR9Bp7fHjMDVkv7w'

def get_sheets_service():
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

    return build('sheets', 'v4', credentials=creds)

def parse_date(date_str):
    try:
        parts = date_str.strip().split('/')
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
    except:
        pass
    return None

def is_in_range(date_tuple):
    if not date_tuple:
        return False
    month, day = date_tuple
    if month == 4 and day >= 27:
        return True
    if month == 5 and day <= 8:
        return True
    return False

def classify_project(project_name):
    if not project_name:
        return '未分類'

    project = project_name.strip()

    if '同上' in project:
        return None

    if '大眾' in project and '銷售' in project:
        return '大眾產品組合'

    if '影音【拉新】' in project or '【拉新】' in project:
        return '大眾產品組合'

    if '協助行銷' in project and '錄製' in project:
        return '其他'

    if '４月產業外廣素材' in project or '產業外廣' in project:
        return '產業研究報告'

    if '影音課程' in project or '線上課程' in project or 'Excel財報' in project or 'AI實戰投資術' in project or '【影音課程' in project or '【大眾影音課' in project:
        return '課程'

    if '課程' in project:
        return '課程'

    if '籌碼K線' in project or '籌K' in project or '【籌K】' in project:
        return '籌碼K線'

    if '起漲K線' in project or '起K' in project or '【起漲K線' in project:
        return '起漲K線'

    if '主動式ETF' in project:
        return '主動式ETF'

    if 'ETF' in project or 'etf' in project:
        return 'ETF'

    if '美股K線' in project or '美股' in project or '台美股' in project:
        return '美股K線'

    if '產業研究報告' in project or '產業報告' in project or '【產業報告' in project or '【大眾－產業報告' in project:
        return '產業研究報告'

    if 'AI' in project or '研究' in project or '跨職能' in project:
        return '跨職能'

    return '其他'

def get_stats():
    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SHEET_ID, range='2026').execute()
    values = result.get('values', [])

    category_stats = defaultdict(int)

    for i in range(2, len(values)):
        row = values[i]

        if not row or len(row) == 0:
            continue

        date_str = row[0] if len(row) > 0 else ''

        if '-' in date_str or not date_str:
            continue

        date_tuple = parse_date(date_str)

        if not is_in_range(date_tuple):
            continue

        project = row[4] if len(row) > 4 else ''
        product_category = classify_project(project)

        if product_category is None:
            for j in range(i - 1, 1, -1):
                prev_row = values[j]
                if len(prev_row) > 4:
                    prev_project = prev_row[4] if len(prev_row) > 4 else ''
                    if prev_project and '同上' not in prev_project:
                        product_category = classify_project(prev_project)
                        if product_category is not None:
                            break

            if product_category is None:
                product_category = '未分類'

        category_stats[product_category] += 1

    return dict(category_stats)

def generate_charts():
    stats = get_stats()

    # 按數量排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0] for item in sorted_stats]
    values = [item[1] for item in sorted_stats]

    # 設定顏色
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
    colors = colors[:len(categories)]

    # 圖表 1: 柱狀圖
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)

    # 在柱子上添加數值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_xlabel('產品類別', fontsize=14, fontweight='bold')
    ax.set_ylabel('工作項目數量', fontsize=14, fontweight='bold')
    ax.set_title('2026/4/27 - 5/8 設計工作統計\n（按產品類別）', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.15)

    # 旋轉 x 軸標籤
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(fontsize=11)

    # 添加網格
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig('chart_bar.png', dpi=300, bbox_inches='tight')
    print("✓ 柱狀圖已保存: chart_bar.png")

    # 圖表 2: 圓餅圖
    fig, ax = plt.subplots(figsize=(10, 8))

    wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%',
                                        colors=colors, startangle=90,
                                        textprops={'fontsize': 11})

    # 設定自動百分比文本
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    ax.set_title('2026/4/27 - 5/8 設計工作分佈\n（按產品類別比例）',
                 fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('chart_pie.png', dpi=300, bbox_inches='tight')
    print("✓ 圓餅圖已保存: chart_pie.png")

    # 圖表 3: 詳細統計表
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')

    # 準備表格數據
    total = sum(values)
    table_data = [['產品類別', '數量', '比例']]
    for cat, val in sorted_stats:
        percentage = f"{(val/total)*100:.1f}%"
        table_data.append([cat, str(val), percentage])

    table_data.append(['總計', str(total), '100.0%'])

    # 創建表格
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.4, 0.25, 0.25])

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # 設定表頭樣式
    for i in range(3):
        table[(0, i)].set_facecolor('#4ECDC4')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 設定總計行樣式
    for i in range(3):
        table[(len(table_data)-1, i)].set_facecolor('#FFE5B4')
        table[(len(table_data)-1, i)].set_text_props(weight='bold')

    # 交替行顏色
    for i in range(1, len(table_data)-1):
        for j in range(3):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')

    plt.title('設計工作統計詳表', fontsize=16, fontweight='bold', pad=20)
    plt.savefig('chart_table.png', dpi=300, bbox_inches='tight')
    print("✓ 統計表已保存: chart_table.png")

    print("\n圖表生成完成！")
    print(f"文件位置: /Users/a01-0220-0066/auto_workflow/")
    print(f"  - chart_bar.png（柱狀圖）")
    print(f"  - chart_pie.png（圓餅圖）")
    print(f"  - chart_table.png（統計表）")

if __name__ == '__main__':
    generate_charts()

    # Upload charts to Google Drive
    print("\n" + "="*80)
    print("📤 上傳圖表到 Google Drive...")
    print("="*80)

    try:
        from drive_uploader import upload_charts_to_drive
        GOOGLE_DRIVE_FOLDER_ID = '16RwtvEIZFYwelmTQunLAk9K5H5O8J4tM'
        uploaded = upload_charts_to_drive(GOOGLE_DRIVE_FOLDER_ID)

        if uploaded:
            print(f"\n✅ 成功上傳 {len(uploaded)} 個檔案到 Google Drive")
            for file_info in uploaded:
                print(f"   - {file_info['name']}")
        else:
            print("⚠️  沒有檔案被上傳")
    except Exception as e:
        print(f"❌ Google Drive 上傳失敗: {str(e)}")
        print("   圖表仍然保存在本地目錄")
