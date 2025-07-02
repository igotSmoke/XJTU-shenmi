# -*- coding: utf-8 -*-
import numpy as np
import time

ModelName = "凝聚法层次聚类算法"

class FixedAgglomerativeClustering:
    def __init__(self, n_clusters=2, linkage='single'):
        self.n_clusters = n_clusters
        self.linkage = linkage
        self.labels_ = None

    def fit(self, X):
        n_samples = X.shape[0]
        dist_matrix = self._pairwise_distance(X)
        active = np.ones(n_samples, dtype=bool)  # 跟踪可用簇索引
        sizes = np.ones(n_samples, dtype=int)    # 各簇包含的样本数
        
        current_clusters = [[i] for i in range(n_samples)]
        cluster_count = n_samples

        while cluster_count > self.n_clusters:
            # 寻找最小距离的活跃簇对
            min_dist = np.inf
            merge_pair = (-1, -1)
            
            # 仅遍历活跃簇的索引
            active_ids = np.where(active)[0]
            for i in range(len(active_ids)):
                for j in range(i+1, len(active_ids)):
                    a = active_ids[i]
                    b = active_ids[j]
                    if dist_matrix[a, b] < min_dist:
                        min_dist = dist_matrix[a, b]
                        merge_pair = (a, b)

            if merge_pair[0] == -1:
                break

            # 合并簇（复用第一个簇的索引）
            a, b = merge_pair
            current_clusters[a].extend(current_clusters[b])
            sizes[a] += sizes[b]
            active[b] = False  # 标记第二个簇为不活跃
            
            # 更新距离矩阵
            for k in active_ids:
                if k == a or not active[k]:
                    continue
                new_dist = self._calc_linkage(dist_matrix, a, b, k, sizes)
                dist_matrix[a, k] = dist_matrix[k, a] = new_dist

            cluster_count -= 1

        # 生成最终标签
        self.labels_ = np.zeros(n_samples, dtype=int)
        valid_clusters = [c for i, c in enumerate(current_clusters) if active[i]]
        for label, cluster in enumerate(valid_clusters[:self.n_clusters]):
            for idx in cluster:
                self.labels_[idx] = label
        return self

    def _pairwise_distance(self, X):
        """向量化计算距离矩阵"""
        return np.sqrt(((X[:, np.newaxis, :] - X)**2).sum(axis=2))

    def _calc_linkage(self, dist_matrix, a, b, k, sizes):
        """根据链接策略计算新距离"""
        if self.linkage == 'single':
            return min(dist_matrix[a, k], dist_matrix[b, k])
        elif self.linkage == 'complete':
            return max(dist_matrix[a, k], dist_matrix[b, k])
        elif self.linkage == 'average':
            return (dist_matrix[a, k]*sizes[a] + dist_matrix[b, k]*sizes[b]) / (sizes[a] + sizes[b])
        else:
            raise ValueError(f"不支持的链接方式: {self.linkage}")

def train(data, *args):
    print("开始%s过程..." % ModelName)
    startT = time.time()
    
    n_clusters = args[0] if args else 2
    linkage = args[1] if len(args)>=2 else 'single'
    
    cluster = FixedAgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit(data)
    
    endT = time.time()
    print("%s过程结束。处理了%d个数据点，耗时%.3f秒" % (ModelName, data.shape[0], endT-startT))
    return cluster