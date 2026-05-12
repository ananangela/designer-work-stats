#!/bin/bash

# 設計工作統計工具 - 快速啟動腳本

echo "======================================"
echo "  設計工作統計工具"
echo "======================================"
echo ""

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 首次執行，建立虛擬環境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 安裝依賴..."
    pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client matplotlib seaborn
else
    source venv/bin/activate
fi

echo ""
echo "📊 執行統計分析..."
python3 stats_improved.py

echo ""
echo "📈 生成圖表..."
python3 generate_charts.py

echo ""
echo "✅ 完成！圖表已保存："
echo "   - chart_bar.png （柱狀圖）"
echo "   - chart_pie.png （圓餅圖）"
echo "   - chart_table.png（統計表）"
echo ""
