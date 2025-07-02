import numpy as np
from dataclasses import dataclass
from typing import List, Dict
import matplotlib.pyplot as plt

@dataclass
class CacheConfig:
    cache_size: int  # 字节
    associativity: int  # 路数
    block_size: int  # 字节

class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = 0
        self.data = None
        self.last_used = 0  # 用于LRU

class Cache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.num_sets = config.cache_size // (config.block_size * config.associativity)
        self.tag_bits = 32 - (self.num_sets.bit_length() - 1) - (config.block_size.bit_length() - 1)
        
        # 初始化cache
        self.cache = [[CacheLine() for _ in range(config.associativity)] 
                     for _ in range(self.num_sets)]
        
        # 统计信息
        self.stats = {
            'total_accesses': 0,
            'total_misses': 0,
            'instruction_accesses': 0,
            'instruction_misses': 0,
            'data_reads': 0,
            'data_read_misses': 0,
            'data_writes': 0,
            'data_write_misses': 0,
            'replacements': 0
        }
        
        self.current_time = 0

    def get_set_index(self, address: int) -> int:
        return (address >> self.config.block_size.bit_length()) & (self.num_sets - 1)

    def get_tag(self, address: int) -> int:
        return address >> (self.config.block_size.bit_length() + (self.num_sets.bit_length() - 1))

    def find_line(self, set_index: int, tag: int) -> int:
        for i, line in enumerate(self.cache[set_index]):
            if line.valid and line.tag == tag:
                return i
        return -1

    def find_lru_line(self, set_index: int) -> int:
        return min(range(self.config.associativity),
                  key=lambda i: self.cache[set_index][i].last_used)

    def access(self, access_type: int, address: int, size: int) -> bool:
        self.current_time += 1
        self.stats['total_accesses'] += 1
        
        # 更新访问类型统计
        if access_type == 2:  # 指令访问
            self.stats['instruction_accesses'] += 1
        elif access_type == 0:  # 数据读
            self.stats['data_reads'] += 1
        elif access_type == 1:  # 数据写
            self.stats['data_writes'] += 1

        set_index = self.get_set_index(address)
        tag = self.get_tag(address)
        
        # 查找cache line
        line_index = self.find_line(set_index, tag)
        
        if line_index != -1:  # Cache hit
            self.cache[set_index][line_index].last_used = self.current_time
            return True
        
        # Cache miss
        self.stats['total_misses'] += 1
        if access_type == 2:
            self.stats['instruction_misses'] += 1
        elif access_type == 0:
            self.stats['data_read_misses'] += 1
        elif access_type == 1:
            self.stats['data_write_misses'] += 1

        # 查找空闲位置
        for i, line in enumerate(self.cache[set_index]):
            if not line.valid:
                line.valid = True
                line.tag = tag
                line.last_used = self.current_time
                return False

        # 需要替换
        self.stats['replacements'] += 1
        lru_index = self.find_lru_line(set_index)
        self.cache[set_index][lru_index].tag = tag
        self.cache[set_index][lru_index].last_used = self.current_time
        return False

    def get_statistics(self) -> Dict:
        stats = self.stats.copy()
        
        # 计算命中率
        stats['total_hit_rate'] = 1 - (stats['total_misses'] / stats['total_accesses'])
        stats['instruction_hit_rate'] = 1 - (stats['instruction_misses'] / stats['instruction_accesses']) if stats['instruction_accesses'] > 0 else 0
        stats['data_read_hit_rate'] = 1 - (stats['data_read_misses'] / stats['data_reads']) if stats['data_reads'] > 0 else 0
        stats['data_write_hit_rate'] = 1 - (stats['data_write_misses'] / stats['data_writes']) if stats['data_writes'] > 0 else 0
        
        return stats

    def plot_statistics(self):
        stats = self.get_statistics()
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # 访问次数统计
        access_types = ['指令访问', '数据读', '数据写']
        access_counts = [stats['instruction_accesses'], 
                        stats['data_reads'], 
                        stats['data_writes']]
        miss_counts = [stats['instruction_misses'], 
                      stats['data_read_misses'], 
                      stats['data_write_misses']]
        
        x = np.arange(len(access_types))
        width = 0.35
        
        ax1.bar(x - width/2, access_counts, width, label='总访问次数')
        ax1.bar(x + width/2, miss_counts, width, label='不命中次数')
        ax1.set_ylabel('次数')
        ax1.set_title('Cache访问统计')
        ax1.set_xticks(x)
        ax1.set_xticklabels(access_types)
        ax1.legend()
        
        # 命中率统计
        hit_rates = [stats['instruction_hit_rate'] * 100,
                    stats['data_read_hit_rate'] * 100,
                    stats['data_write_hit_rate'] * 100]
        
        ax2.bar(access_types, hit_rates)
        ax2.set_ylabel('命中率 (%)')
        ax2.set_title('Cache命中率统计')
        
        plt.tight_layout()
        plt.show() 