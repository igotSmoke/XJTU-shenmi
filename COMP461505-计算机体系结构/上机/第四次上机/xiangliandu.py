import matplotlib
matplotlib.use('Agg')  # 设置后端为Agg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

# 设置中文字体
font = FontProperties(family='Microsoft YaHei')

# 测试数据
associativities = ['1路', '2路', '4路', '8路']
read_blocks = [253723, 253723, 253723, 253723]
write_blocks = [130733, 130733, 130733, 130733]
replacements = [18265, 16422, 10204, 9580]
read_miss_rates = [1.79, 1.16, 0.27, 0.24]
write_miss_rates = [8.75, 9.40, 7.28, 6.74]
total_miss_rates = [1.84, 1.65, 1.03, 0.97]

# 创建图表
fig = plt.figure(figsize=(15, 10))
plt.style.use('default')

# 1. 参数组合表格
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
ax1.axis('tight')
ax1.axis('off')

# 准备表格数据
table_data = [
    ['Cache大小', '相联度', '块大小', 'Trace文件'],
    ['8KB', '1路', '64B', '047.tomcatv.din'],
    ['8KB', '2路', '64B', '047.tomcatv.din'],
    ['8KB', '4路', '64B', '047.tomcatv.din'],
    ['8KB', '8路', '64B', '047.tomcatv.din']
]

# 创建表格
table = ax1.table(cellText=table_data,
                 loc='center',
                 cellLoc='center',
                 colWidths=[0.25, 0.25, 0.25, 0.25])

# 设置表格样式
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

# 设置表头样式
for i in range(4):
    table[(0, i)].set_facecolor('#34495e')
    table[(0, i)].set_text_props(color='white', fontproperties=font)

# 设置表格内容字体
for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        table[(i, j)].set_text_props(fontproperties=font)

ax1.set_title('测试参数组合', pad=20, fontsize=12, fontproperties=font)

# 2. 访问块数量统计
ax2 = plt.subplot2grid((2, 2), (1, 0))
x = np.arange(len(associativities))
width = 0.35

ax2.bar(x - width/2, read_blocks, width, label='读块数', color='#3498db')
ax2.bar(x + width/2, write_blocks, width, label='写块数', color='#2ecc71')

ax2.set_ylabel('块数量', fontproperties=font)
ax2.set_title('读写块数量统计', fontproperties=font)
ax2.set_xticks(x)
ax2.set_xticklabels(associativities, fontproperties=font)
ax2.legend(prop=font)
ax2.grid(True, linestyle='--', alpha=0.7)

# 3. 失效率统计
ax3 = plt.subplot2grid((2, 2), (1, 1))
x = np.arange(len(associativities))  # 创建x轴位置数组
ax3.plot(x, read_miss_rates, 'o-', label='读失效率', color='#3498db')
ax3.plot(x, write_miss_rates, 's-', label='写失效率', color='#2ecc71')
ax3.plot(x, total_miss_rates, '^-', label='总体失效率', color='#e74c3c')

ax3.set_ylabel('失效率 (%)', fontproperties=font)
ax3.set_title('Cache失效率统计', fontproperties=font)
ax3.set_xticks(x)  # 设置刻度位置
ax3.set_xticklabels(associativities, fontproperties=font)  # 设置刻度标签
ax3.legend(prop=font)
ax3.grid(True, linestyle='--', alpha=0.7)

# 添加替换次数标注
for i, v in enumerate(replacements):
    ax3.text(i, total_miss_rates[i], f'替换: {v:,}', 
             ha='center', va='bottom', fontproperties=font)

plt.tight_layout()
plt.savefig('cache_associativity_analysis.png', dpi=300, bbox_inches='tight') 