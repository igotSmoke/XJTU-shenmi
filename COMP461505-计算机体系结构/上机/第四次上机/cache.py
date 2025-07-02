import math
from collections import OrderedDict

class Cache:
    def __init__(self, cache_size, block_size, associativity):
        self.cache_size = cache_size  # 字节
        self.block_size = block_size  # 字节
        self.associativity = associativity  # 路数
        
        # 计算Cache参数
        self.num_blocks = cache_size // block_size
        self.num_sets = self.num_blocks // associativity
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(self.num_sets))
        self.tag_bits = 32 - self.offset_bits - self.index_bits
        
        # 初始化Cache
        self.cache = [OrderedDict() for _ in range(self.num_sets)]
        
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
    
    def get_set_index(self, address):
        return (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
    
    def get_tag(self, address):
        return address >> (self.offset_bits + self.index_bits)
    
    def access(self, access_type, address):
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
        cache_set = self.cache[set_index]
        
        # 检查是否命中
        if tag in cache_set:
            # 更新LRU顺序
            cache_set.move_to_end(tag)
            return True
        
        # Cache未命中
        self.stats['total_misses'] += 1
        if access_type == 2:
            self.stats['instruction_misses'] += 1
        elif access_type == 0:
            self.stats['data_read_misses'] += 1
        elif access_type == 1:
            self.stats['data_write_misses'] += 1
        
        # 写分配策略
        if len(cache_set) >= self.associativity:
            # 需要替换
            self.stats['replacements'] += 1
            cache_set.popitem(last=False)  # 移除最久未使用的项
        
        # 添加新项
        cache_set[tag] = True
        return False
    
    def get_statistics(self):
        stats = self.stats.copy()
        
        # 计算命中率
        stats['total_hit_rate'] = 1 - (stats['total_misses'] / stats['total_accesses']) if stats['total_accesses'] > 0 else 0
        stats['instruction_hit_rate'] = 1 - (stats['instruction_misses'] / stats['instruction_accesses']) if stats['instruction_accesses'] > 0 else 0
        stats['data_read_hit_rate'] = 1 - (stats['data_read_misses'] / stats['data_reads']) if stats['data_reads'] > 0 else 0
        stats['data_write_hit_rate'] = 1 - (stats['data_write_misses'] / stats['data_writes']) if stats['data_writes'] > 0 else 0
        
        return stats 