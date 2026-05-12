#!/usr/bin/env python3
"""
Generate presentation slides for design work statistics
Follows C-Money operation meeting style
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np

# Set Chinese font
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# Color scheme from presentation
COLOR_RED = '#C41E3A'
COLOR_DARK_RED = '#8B0000'
COLOR_BROWN = '#6B4423'
COLOR_LIGHT_GRAY = '#F5F5F5'
COLOR_TEXT = '#333333'

# Data from design work statistics
product_categories = {
    '課程': 12,
    '產業研究報告': 8,
    '大眾產品組合': 5,
    '籌碼K線': 3,
    '其他': 2,
    '起漲K線': 1,
    '跨職能': 1
}

original_categories = {
    '行銷圖': 16,
    '短影音': 9,
    '素材處理': 5,
    '跨職能': 3,
    '商品頁': 2,
    '動畫': 2
}

def create_slide_1():
    """Slide 1: Design workload by product category"""
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('white')

    # Title area
    ax_title = fig.add_axes([0, 0.85, 1, 0.15])
    ax_title.axis('off')

    # Red header bar
    header_bar = mpatches.Rectangle((0, 0.5), 0.3, 0.5,
                                    transform=ax_title.transAxes,
                                    facecolor=COLOR_RED, edgecolor='none')
    ax_title.add_patch(header_bar)

    ax_title.text(0.02, 0.75, '設計工作統計', fontsize=32, fontweight='bold',
                  color='white', transform=ax_title.transAxes, va='center')
    ax_title.text(0.35, 0.75, '按產品類別分類', fontsize=24,
                  color=COLOR_TEXT, transform=ax_title.transAxes, va='center')

    ax_title.text(0.02, 0.15, '時間範圍：2026/04/28 - 2026/05/12（前兩週）',
                  fontsize=14, color=COLOR_TEXT, transform=ax_title.transAxes)

    # Main chart area
    ax_chart = fig.add_axes([0.08, 0.15, 0.85, 0.65])

    categories = list(product_categories.keys())
    values = list(product_categories.values())
    total = sum(values)

    # Sort by value
    sorted_data = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
    categories, values = zip(*sorted_data)

    # Color gradient
    colors = ['#FF6B6B', '#FF8C8C', '#FFA5A5', '#FFB8B8', '#D4605A', '#B85450', '#9B4846']

    bars = ax_chart.barh(categories, values, color=colors[:len(categories)],
                         edgecolor='black', linewidth=1.5, height=0.6)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        width = bar.get_width()
        percentage = (val / total) * 100
        ax_chart.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                     f'{val}項\n({percentage:.1f}%)',
                     ha='left', va='center', fontsize=11, fontweight='bold')

    ax_chart.set_xlabel('工作項目數量', fontsize=14, fontweight='bold', color=COLOR_TEXT)
    ax_chart.set_ylim(-0.5, len(categories) - 0.5)
    ax_chart.set_xlim(0, max(values) * 1.25)
    ax_chart.grid(axis='x', alpha=0.3, linestyle='--')
    ax_chart.set_axisbelow(True)

    # Stats box
    stats_text = f"總計：{total}項工作\n時間跨度：14天\n平均每天：{total/14:.1f}項"
    ax_chart.text(0.98, 0.02, stats_text, transform=ax_chart.transAxes,
                 fontsize=12, verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor=COLOR_LIGHT_GRAY, alpha=0.8, pad=1))

    ax_chart.tick_params(axis='y', labelsize=12)
    ax_chart.tick_params(axis='x', labelsize=11)

    plt.savefig('presentation_slide_1.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 簡報Slide 1已保存: presentation_slide_1.png")
    plt.close()

def create_slide_2():
    """Slide 2: Design workload by original categories"""
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('white')

    # Title area
    ax_title = fig.add_axes([0, 0.85, 1, 0.15])
    ax_title.axis('off')

    # Red header bar
    header_bar = mpatches.Rectangle((0, 0.5), 0.3, 0.5,
                                    transform=ax_title.transAxes,
                                    facecolor=COLOR_RED, edgecolor='none')
    ax_title.add_patch(header_bar)

    ax_title.text(0.02, 0.75, '設計工作統計', fontsize=32, fontweight='bold',
                  color='white', transform=ax_title.transAxes, va='center')
    ax_title.text(0.35, 0.75, '按工作類型分類', fontsize=24,
                  color=COLOR_TEXT, transform=ax_title.transAxes, va='center')

    ax_title.text(0.02, 0.15, '時間範圍：2026/04/28 - 2026/05/12（前兩週）',
                  fontsize=14, color=COLOR_TEXT, transform=ax_title.transAxes)

    # Main chart area
    ax_chart = fig.add_axes([0.08, 0.15, 0.85, 0.65])

    categories = list(original_categories.keys())
    values = list(original_categories.values())
    total = sum(values)

    # Sort by value
    sorted_data = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
    categories, values = zip(*sorted_data)

    # Color palette - matching presentation style
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']

    bars = ax_chart.barh(categories, values, color=colors[:len(categories)],
                         edgecolor='black', linewidth=1.5, height=0.6)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        width = bar.get_width()
        percentage = (val / total) * 100
        ax_chart.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                     f'{val}項\n({percentage:.1f}%)',
                     ha='left', va='center', fontsize=11, fontweight='bold')

    ax_chart.set_xlabel('工作項目數量', fontsize=14, fontweight='bold', color=COLOR_TEXT)
    ax_chart.set_ylim(-0.5, len(categories) - 0.5)
    ax_chart.set_xlim(0, max(values) * 1.25)
    ax_chart.grid(axis='x', alpha=0.3, linestyle='--')
    ax_chart.set_axisbelow(True)

    # Key insights box
    insights = "重點發現：\n• 行銷圖為主要工作類型（43.2%）\n• 短影音持續成長（24.3%）\n• 多角度素材產出（素材處理13.5%）"
    ax_chart.text(0.98, 0.02, insights, transform=ax_chart.transAxes,
                 fontsize=11, verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor=COLOR_LIGHT_GRAY, alpha=0.8, pad=1))

    ax_chart.tick_params(axis='y', labelsize=12)
    ax_chart.tick_params(axis='x', labelsize=11)

    plt.savefig('presentation_slide_2.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 簡報Slide 2已保存: presentation_slide_2.png")
    plt.close()

def create_summary_slide():
    """Slide 3: Executive summary with key metrics"""
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('white')

    # Title area
    ax_title = fig.add_axes([0, 0.85, 1, 0.15])
    ax_title.axis('off')

    # Red header bar
    header_bar = mpatches.Rectangle((0, 0.5), 0.15, 0.5,
                                    transform=ax_title.transAxes,
                                    facecolor=COLOR_RED, edgecolor='none')
    ax_title.add_patch(header_bar)

    ax_title.text(0.02, 0.75, '摘要', fontsize=32, fontweight='bold',
                  color='white', transform=ax_title.transAxes, va='center')

    # Content area
    ax_content = fig.add_axes([0.08, 0.15, 0.85, 0.65])
    ax_content.axis('off')

    # KPI boxes
    kpis = [
        ('32', '總工作項目', '2026/04/28-05/12'),
        ('14', '天數', '前兩週'),
        ('課程', '最多工作類別', '12項 (37.5%)'),
        ('行銷圖', '最主要工作類型', '16項 (43.2%)')
    ]

    # 4 boxes in 2x2 grid
    box_width = 0.22
    box_height = 0.35
    x_positions = [0.08, 0.53]
    y_positions = [0.45, 0.08]

    for idx, (value, label, sublabel) in enumerate(kpis):
        row = idx // 2
        col = idx % 2
        x = x_positions[col]
        y = y_positions[row]

        # Box background
        rect = mpatches.FancyBboxPatch((x, y), box_width, box_height,
                                      transform=ax_content.transAxes,
                                      boxstyle="round,pad=0.01",
                                      facecolor=COLOR_LIGHT_GRAY,
                                      edgecolor=COLOR_RED, linewidth=3)
        ax_content.add_patch(rect)

        # Content
        ax_content.text(x + box_width/2, y + box_height*0.65, value,
                       transform=ax_content.transAxes, fontsize=28, fontweight='bold',
                       ha='center', va='center', color=COLOR_RED)
        ax_content.text(x + box_width/2, y + box_height*0.35, label,
                       transform=ax_content.transAxes, fontsize=12, fontweight='bold',
                       ha='center', va='center', color=COLOR_TEXT)
        ax_content.text(x + box_width/2, y + box_height*0.1, sublabel,
                       transform=ax_content.transAxes, fontsize=10,
                       ha='center', va='center', color='#666666')

    plt.savefig('presentation_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 簡報Summary已保存: presentation_summary.png")
    plt.close()

if __name__ == '__main__':
    print("📊 生成簡報圖表...")
    create_slide_1()
    create_slide_2()
    create_summary_slide()
    print("\n✅ 簡報圖表生成完成！")
    print("📁 文件位置：")
    print("   - presentation_slide_1.png（產品類別分析）")
    print("   - presentation_slide_2.png（工作類型分析）")
    print("   - presentation_summary.png（關鍵指標摘要）")
