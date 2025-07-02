import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from cache import Cache
from visualization import CacheVisualizer

class CacheSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cache模拟器")
        self.root.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建参数选择区域
        self.create_parameter_frame()
        
        # 创建结果显示区域
        self.create_result_frame()
        
        # 设置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def create_parameter_frame(self):
        """创建参数选择区域"""
        param_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding="5")
        param_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Trace文件选择
        ttk.Label(param_frame, text="Trace文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.trace_file_var = tk.StringVar()
        ttk.Entry(param_frame, textvariable=self.trace_file_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(param_frame, text="浏览", command=self.browse_trace_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Cache大小选择
        ttk.Label(param_frame, text="Cache大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cache_size_var = tk.StringVar(value="8192")
        cache_size_combo = ttk.Combobox(param_frame, textvariable=self.cache_size_var, 
                                      values=["8192", "16384", "32768", "65536"])
        cache_size_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 相联度选择
        ttk.Label(param_frame, text="相联度:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.associativity_var = tk.StringVar(value="4")
        associativity_combo = ttk.Combobox(param_frame, textvariable=self.associativity_var,
                                         values=["1", "2", "4", "8"])
        associativity_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 块大小选择
        ttk.Label(param_frame, text="块大小:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.block_size_var = tk.StringVar(value="64")
        block_size_combo = ttk.Combobox(param_frame, textvariable=self.block_size_var,
                                      values=["16", "32", "64", "128"])
        block_size_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 运行按钮
        ttk.Button(param_frame, text="运行模拟", command=self.run_simulation).grid(row=4, column=1, pady=10)

    def create_result_frame(self):
        """创建结果显示区域"""
        self.result_frame = ttk.LabelFrame(self.main_frame, text="模拟结果", padding="5")
        self.result_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 创建文本显示区域
        self.text_result = tk.Text(self.result_frame, height=10, width=80)
        self.text_result.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建图表显示区域
        self.chart_frame = ttk.Frame(self.result_frame)
        self.chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置网格权重
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(1, weight=1)

    def browse_trace_file(self):
        """浏览并选择trace文件"""
        filename = filedialog.askopenfilename(
            title="选择Trace文件",
            filetypes=[("Trace files", "*.din"), ("All files", "*.*")]
        )
        if filename:
            self.trace_file_var.set(filename)

    def run_simulation(self):
        """运行Cache模拟"""
        try:
            # 获取参数
            trace_file = self.trace_file_var.get()
            if not trace_file or not os.path.exists(trace_file):
                messagebox.showerror("错误", "请选择有效的Trace文件")
                return
            
            cache_size = int(self.cache_size_var.get())
            associativity = int(self.associativity_var.get())
            block_size = int(self.block_size_var.get())
            
            # 创建Cache实例
            cache = Cache(cache_size, block_size, associativity)
            
            # 读取并处理trace文件
            with open(trace_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        access_type = int(parts[0])
                        address = int(parts[1], 16)
                        cache.access(access_type, address)
            
            # 获取统计信息
            stats = cache.get_statistics()
            
            # 显示文本结果
            self.display_text_results(stats)
            
            # 显示图表
            self.display_charts(stats)
            
        except Exception as e:
            messagebox.showerror("错误", f"模拟过程中出现错误：{str(e)}")

    def display_text_results(self, stats):
        """显示文本形式的统计结果"""
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "Cache模拟结果：\n\n")
        
        # 总体统计
        self.text_result.insert(tk.END, f"总访问次数：{stats['total_accesses']:,}\n")
        self.text_result.insert(tk.END, f"总未命中次数：{stats['total_misses']:,}\n")
        self.text_result.insert(tk.END, f"总未命中率：{stats['total_misses']/stats['total_accesses']*100:.2f}%\n\n")
        
        # 指令访问统计
        self.text_result.insert(tk.END, "指令访问：\n")
        self.text_result.insert(tk.END, f"总次数：{stats['instruction_accesses']:,}\n")
        self.text_result.insert(tk.END, f"未命中次数：{stats['instruction_misses']:,}\n")
        self.text_result.insert(tk.END, f"未命中率：{stats['instruction_misses']/stats['instruction_accesses']*100:.2f}%\n\n")
        
        # 数据读统计
        self.text_result.insert(tk.END, "数据读：\n")
        self.text_result.insert(tk.END, f"总次数：{stats['data_reads']:,}\n")
        self.text_result.insert(tk.END, f"未命中次数：{stats['data_read_misses']:,}\n")
        self.text_result.insert(tk.END, f"未命中率：{stats['data_read_misses']/stats['data_reads']*100:.2f}%\n\n")
        
        # 数据写统计
        self.text_result.insert(tk.END, "数据写：\n")
        self.text_result.insert(tk.END, f"总次数：{stats['data_writes']:,}\n")
        self.text_result.insert(tk.END, f"未命中次数：{stats['data_write_misses']:,}\n")
        self.text_result.insert(tk.END, f"未命中率：{stats['data_write_misses']/stats['data_writes']*100:.2f}%\n\n")
        
        # 替换次数
        self.text_result.insert(tk.END, f"替换次数：{stats['replacements']:,}\n")

    def display_charts(self, stats):
        """显示统计图表"""
        # 清除旧的图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 创建新的图表
        visualizer = CacheVisualizer(stats)
        canvas = visualizer.create_detailed_report(self.chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def main():
    root = tk.Tk()
    app = CacheSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 