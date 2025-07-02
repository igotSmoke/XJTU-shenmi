# Cache模拟器

这是一个用于模拟Cache执行过程的图形化工具，支持多种Cache配置参数和统计信息的可视化展示。

## 功能特点

- 支持图形化界面操作
- 可配置的Cache参数：
  - Cache大小：8KB、16KB、32KB、64KB
  - 相联度：1、2、4、8
  - 块大小：16B、32B、64B、128B
- 使用LRU替换算法
- 写失效策略采用写分配
- 支持多种统计信息的可视化展示
- 支持trace文件输入

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python gui.py
```

2. 在图形界面中：
   - 选择Cache配置参数（大小、相联度、块大小）
   - 点击"选择文件"按钮选择trace文件
   - 点击"运行模拟"按钮开始模拟
   - 查看统计结果和图表

## Trace文件格式

每行格式为：`access_type address size/data`
- access_type: 0（load data）、1（store data）、2（fetch instruction）
- address: 32位地址（16进制表示）
- size/data: 数据大小

## 统计信息

模拟器会显示以下统计信息：
- 总访问次数和不命中次数
- 指令访问的统计信息
- 数据读写的统计信息
- Cache替换次数
- 各类访问的命中率

## 图表展示

程序会生成两个图表：
1. Cache访问统计：显示各类访问的总次数和不命中次数
2. Cache命中率统计：显示各类访问的命中率 