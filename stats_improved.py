#!/usr/bin/env python3
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import defaultdict
from auth_helper import get_credentials_file
from data_manager import DataManager

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
            # Use auth_helper to get credentials file
            credentials_file = get_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
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

def get_previous_week_range():
    """計算前兩週的日期範圍 (過去 14 天)"""
    from datetime import datetime, timedelta

    today = datetime.now()
    week_start = today - timedelta(days=14)

    return week_start, today

def is_in_range(date_tuple):
    """檢查日期是否在前一週範圍內"""
    if not date_tuple:
        return False

    from datetime import datetime

    month, day = date_tuple
    week_start, week_end = get_previous_week_range()

    # 構造 2026 年的日期物件進行比較
    try:
        check_date = datetime(2026, month, day)
    except:
        return False

    return week_start <= check_date <= week_end

def classify_project(project_name):
    """根據項目名稱識別產品類別"""
    if not project_name:
        return '未分類'

    project = project_name.strip()

    # 檢查「同上」項目 - 返回 None，由呼叫者處理
    if '同上' in project:
        return None

    # 檢查「大眾X月銷售」 -> 大眾產品組合
    if '大眾' in project and '銷售' in project:
        return '大眾產品組合'

    # 檢查「影音【拉新】」 -> 大眾產品組合
    if '影音【拉新】' in project or '【拉新】' in project:
        return '大眾產品組合'

    # 檢查「協助行銷」 -> 其他
    if '協助行銷' in project and '錄製' in project:
        return '其他'

    # 檢查「產業」相關 -> 產業研究報告
    if '４月產業外廣素材' in project or '產業外廣' in project:
        return '產業研究報告'

    # 優先檢查課程相關（優先於地域相關詞）
    if '影音課程' in project or '線上課程' in project or 'Excel財報' in project or 'AI實戰投資術' in project or '【影音課程' in project or '【大眾影音課' in project:
        return '課程'

    # 檢查課程（泛）
    if '課程' in project:
        return '課程'

    # 原有的分類規則
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

    # 檢查「跨職能」- 如果包含 AI、研究等字眼
    if 'AI' in project or '研究' in project or '跨職能' in project:
        return '跨職能'

    # 其他雜項
    return '其他'

def stats_improved():
    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SHEET_ID, range='2026').execute()
    values = result.get('values', [])

    category_stats = defaultdict(int)
    all_data = []

    # 從第 3 行開始（第 2 行是標題）
    for i in range(2, len(values)):
        row = values[i]

        if not row or len(row) == 0:
            continue

        date_str = row[0] if len(row) > 0 else ''

        # 跳過日期範圍行
        if '-' in date_str or not date_str:
            continue

        date_tuple = parse_date(date_str)

        if not is_in_range(date_tuple):
            continue

        # 提取數據
        date_val = row[0] if len(row) > 0 else ''
        large_cat = row[1] if len(row) > 1 else ''
        designer = row[2] if len(row) > 2 else ''
        category = row[3] if len(row) > 3 else ''
        project = row[4] if len(row) > 4 else ''

        # 從項目名稱中分類
        product_category = classify_project(project)

        # 如果是「同上」，往前追溯
        if product_category is None:
            # 往前查找不是「同上」的項目
            for j in range(i - 1, 1, -1):
                prev_row = values[j]
                if len(prev_row) > 4:
                    prev_project = prev_row[4] if len(prev_row) > 4 else ''
                    prev_date = prev_row[0] if len(prev_row) > 0 else ''

                    if prev_project and '同上' not in prev_project and prev_date:
                        product_category = classify_project(prev_project)
                        if product_category is not None:
                            # 用完整的項目名稱更新 project
                            project = f"{prev_project} (同上項目)"
                            break

            # 如果還是找不到，就標記為未分類
            if product_category is None:
                product_category = '未分類'

        category_stats[product_category] += 1

        all_data.append({
            'date': date_val,
            'large_cat': large_cat,
            'designer': designer,
            'category': category,
            'project': project,
            'product_category': product_category
        })

    # 輸出統計結果
    from datetime import datetime
    week_start, week_end = get_previous_week_range()
    date_range = f"{week_start.strftime('%Y/%m/%d')} - {week_end.strftime('%Y/%m/%d')}"

    print("\n" + "="*80)
    print(f"【前兩週工作統計（{date_range}）】")
    print("="*80)

    if not category_stats:
        print("指定日期範圍內沒有找到數據")
        return

    # 按數量排序
    sorted_stats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)

    total = sum(category_stats.values())

    print(f"\n{'產品類別':<20} {'數量':>10}")
    print("-" * 35)

    for category, count in sorted_stats:
        print(f"{category:<20} {count:>10}")

    print("-" * 35)
    print(f"{'總計':<20} {total:>10}")

    # 計算按「類別」的統計
    print("\n" + "="*80)
    print("【按「類別」統計（表單原始分類）】")
    print("="*80)

    category_original_stats = defaultdict(int)
    for item in all_data:
        original_category = item['category'] if item['category'] else '未分類'
        category_original_stats[original_category] += 1

    sorted_original_stats = sorted(category_original_stats.items(), key=lambda x: x[1], reverse=True)
    total_original = sum(category_original_stats.values())

    # Save data to JSON files
    dm = DataManager()
    dm.save_raw_data(all_data)
    dm.save_statistics(category_stats, category_original_stats)

    print(f"\n{'類別':<30} {'數量':>10}")
    print("-" * 45)

    for category, count in sorted_original_stats:
        print(f"{category:<30} {count:>10}")

    print("-" * 45)
    print(f"{'總計':<30} {total_original:>10}")

    # 輸出詳細數據
    print("\n" + "="*80)
    print("【詳細數據（按日期排序）】")
    print("="*80)

    # 按日期排序
    all_data.sort(key=lambda x: (parse_date(x['date']) or (99, 99)))

    current_date = None
    for item in all_data:
        if item['date'] != current_date:
            current_date = item['date']
            print(f"\n【{current_date}】")

        print(f"  {item['product_category']:<20} | {item['designer']:<8} | {item['project'][:50]}")

if __name__ == '__main__':
    stats_improved()
