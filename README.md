# 設計工作統計工具

用於統計設計師在特定日期區間的工作項目，並按產品類別生成圖表。

## 📋 功能

- 從 Google Sheets 讀取設計工作資料
- 按產品類別統計工作項目數量
- 生成簡報用的圖表（柱狀圖、圓餅圖、統計表）

## 🚀 快速開始

### 1. 初始設置（第一次執行）

```bash
cd /Users/a01-0220-0066/designer_work_stats
python3 -m venv venv
source venv/bin/activate
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client matplotlib seaborn
```

### 2. 執行統計並生成圖表

```bash
source venv/bin/activate
python3 stats_improved.py          # 輸出統計結果
python3 generate_charts.py         # 生成圖表
```

## 📊 產品類別分類

統計流程會自動根據項目名稱分類為：

- **課程** - 影音課程、線上課程相關
- **產業研究報告** - 產業分析和研究報告
- **籌碼K線** - 籌碼相關產品
- **起漲K線** - 起漲相關產品
- **美股K線** - 美股相關產品
- **ETF** - ETF 相關產品
- **主動式ETF** - 主動式 ETF 相關
- **大眾產品組合** - 大眾銷售、拉新相關
- **跨職能** - 包含 AI、研究的協作項目
- **其他** - 其他雜項工作

## 📁 檔案說明

- `stats_improved.py` - 核心統計腳本
- `generate_charts.py` - 圖表生成腳本
- `credentials.json` - Google API 認證檔案
- `token.pickle` - OAuth token（首次執行時自動生成）
- `chart_bar.png` - 柱狀圖
- `chart_pie.png` - 圓餅圖
- `chart_table.png` - 統計表

## ⚙️ 自訂統計期間

編輯 `stats_improved.py` 中的 `is_in_range()` 函數：

```python
def is_in_range(date_tuple):
    if not date_tuple:
        return False
    month, day = date_tuple
    # 修改此處的日期範圍
    if month == 4 and day >= 27:
        return True
    if month == 5 and day <= 8:
        return True
    return False
```

## 📝 Google Sheets 設定

- Sheet ID: `1K3VVKGJn47UTxGy7UGQtnkrO5yDVR9Bp7fHjMDVkv7w`
- 工作表名稱: `2026`
- 列結構：
  - 列 0: 日期 (M/D 格式)
  - 列 1: 大項
  - 列 2: 設計者
  - 列 3: 類別
  - 列 4: 項目名稱

## 💡 使用提示

1. 首次執行 `stats_improved.py` 時會開啟瀏覽器要求授權
2. 授權後會自動生成 `token.pickle`，以後無需重複授權
3. 圖表生成在 `/Users/a01-0220-0066/designer_work_stats/` 目錄中
