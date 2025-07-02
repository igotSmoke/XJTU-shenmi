import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QComboBox, QPushButton,
                           QFileDialog, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt
from cache import Cache, CacheConfig

class CacheSimulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cache模拟器')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建配置组
        config_group = QGroupBox('Cache配置')
        config_layout = QHBoxLayout()
        
        # Cache大小选择
        cache_size_layout = QVBoxLayout()
        cache_size_layout.addWidget(QLabel('Cache大小:'))
        self.cache_size_combo = QComboBox()
        self.cache_size_combo.addItems(['8KB', '16KB', '32KB', '64KB'])
        cache_size_layout.addWidget(self.cache_size_combo)
        config_layout.addLayout(cache_size_layout)
        
        # 相联度选择
        associativity_layout = QVBoxLayout()
        associativity_layout.addWidget(QLabel('相联度:'))
        self.associativity_combo = QComboBox()
        self.associativity_combo.addItems(['1', '2', '4', '8'])
        associativity_layout.addWidget(self.associativity_combo)
        config_layout.addLayout(associativity_layout)
        
        # 块大小选择
        block_size_layout = QVBoxLayout()
        block_size_layout.addWidget(QLabel('块大小:'))
        self.block_size_combo = QComboBox()
        self.block_size_combo.addItems(['16B', '32B', '64B', '128B'])
        block_size_layout.addWidget(self.block_size_combo)
        config_layout.addLayout(block_size_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 文件选择
        file_group = QGroupBox('Trace文件')
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel('未选择文件')
        self.select_file_btn = QPushButton('选择文件')
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.select_file_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 运行按钮
        self.run_btn = QPushButton('运行模拟')
        self.run_btn.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_btn)
        
        # 结果显示
        result_group = QGroupBox('模拟结果')
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.trace_file_path = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择Trace文件', '', 'Text Files (*.txt *.din);;All Files (*)')
        if file_path:
            self.trace_file_path = file_path
            self.file_path_label.setText(file_path)

    def parse_size(self, size_str: str) -> int:
        size_map = {'KB': 1024, 'B': 1}
        value = int(size_str[:-2])
        unit = size_str[-2:]
        return value * size_map[unit]

    def run_simulation(self):
        if not self.trace_file_path:
            self.result_text.setText('请先选择Trace文件！')
            return
        
        # 获取配置
        cache_size = self.parse_size(self.cache_size_combo.currentText())
        associativity = int(self.associativity_combo.currentText())
        block_size = self.parse_size(self.block_size_combo.currentText())
        
        # 创建Cache实例
        config = CacheConfig(cache_size, associativity, block_size)
        cache = Cache(config)
        
        # 读取并处理trace文件
        try:
            with open(self.trace_file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        access_type = int(parts[0])
                        address = int(parts[1], 16)  # 16进制地址
                        size = int(parts[2])
                        cache.access(access_type, address, size)
            
            # 获取统计结果
            stats = cache.get_statistics()
            
            # 显示结果
            result_text = f"""Cache配置:
- Cache大小: {self.cache_size_combo.currentText()}
- 相联度: {self.associativity_combo.currentText()}
- 块大小: {self.block_size_combo.currentText()}

统计结果:
- 总访问次数: {stats['total_accesses']}
- 总不命中次数: {stats['total_misses']}
- 总命中率: {stats['total_hit_rate']*100:.2f}%

指令访问:
- 总次数: {stats['instruction_accesses']}
- 不命中次数: {stats['instruction_misses']}
- 命中率: {stats['instruction_hit_rate']*100:.2f}%

数据读:
- 总次数: {stats['data_reads']}
- 不命中次数: {stats['data_read_misses']}
- 命中率: {stats['data_read_hit_rate']*100:.2f}%

数据写:
- 总次数: {stats['data_writes']}
- 不命中次数: {stats['data_write_misses']}
- 命中率: {stats['data_write_hit_rate']*100:.2f}%

替换次数: {stats['replacements']}"""
            
            self.result_text.setText(result_text)
            
            # 显示图表
            cache.plot_statistics()
            
        except Exception as e:
            self.result_text.setText(f'运行出错：{str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CacheSimulatorGUI()
    window.show()
    sys.exit(app.exec_()) 