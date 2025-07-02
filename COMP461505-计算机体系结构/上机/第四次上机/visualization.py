import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from matplotlib.font_manager import FontProperties

class CacheVisualizer:
    def __init__(self, stats):
        self.stats = stats
        plt.style.use('default')  # 使用默认样式
        
        # 设置中文字体
        self.font = FontProperties(family='Microsoft YaHei')
        
        # 基础样式设置
        plt.rcParams['figure.facecolor'] = 'white'  # 设置图表背景色
        plt.rcParams['axes.facecolor'] = 'white'    # 设置坐标轴背景色
        plt.rcParams['grid.color'] = '#E0E0E0'      # 设置网格线颜色
        plt.rcParams['grid.linestyle'] = '--'       # 设置网格线样式
        plt.rcParams['font.size'] = 10              # 设置默认字体大小

    def create_detailed_report(self, master):
        """创建详细的Cache性能报告"""
        fig = plt.figure(figsize=(12, 4))
        
        # 创建表格
        ax = fig.add_subplot(111)
        self._plot_detailed_stats_table(ax)
        
        plt.tight_layout()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        return canvas

    def _plot_detailed_stats_table(self, ax):
        """绘制详细统计信息表格"""
        ax.axis('tight')
        ax.axis('off')
        
        # 准备表格数据
        table_data = [
            ['访问类型', '总次数', '未命中次数', '未命中率'],
            ['总体访问', 
             f"{self.stats['total_accesses']:,}",
             f"{self.stats['total_misses']:,}",
             f"{self.stats['total_misses']/self.stats['total_accesses']*100:.2f}%"],
            ['指令访问',
             f"{self.stats['instruction_accesses']:,}",
             f"{self.stats['instruction_misses']:,}",
             f"{self.stats['instruction_misses']/self.stats['instruction_accesses']*100:.2f}%" if self.stats['instruction_accesses'] > 0 else "0.00%"],
            ['数据读',
             f"{self.stats['data_reads']:,}",
             f"{self.stats['data_read_misses']:,}",
             f"{self.stats['data_read_misses']/self.stats['data_reads']*100:.2f}%" if self.stats['data_reads'] > 0 else "0.00%"],
            ['数据写',
             f"{self.stats['data_writes']:,}",
             f"{self.stats['data_write_misses']:,}",
             f"{self.stats['data_write_misses']/self.stats['data_writes']*100:.2f}%" if self.stats['data_writes'] > 0 else "0.00%"]
        ]
        
        # 创建表格
        table = ax.table(cellText=table_data,
                        loc='center',
                        cellLoc='center',
                        colWidths=[0.2, 0.3, 0.3, 0.2])
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # 设置表头样式
        for i in range(4):
            table[(0, i)].set_facecolor('#34495e')
            table[(0, i)].set_text_props(color='white', fontproperties=self.font)
        
        # 设置表格内容字体
        for i in range(len(table_data)):
            for j in range(len(table_data[0])):
                table[(i, j)].set_text_props(fontproperties=self.font)
        
        ax.set_title('Cache性能统计', pad=20, fontsize=12, fontproperties=self.font) 