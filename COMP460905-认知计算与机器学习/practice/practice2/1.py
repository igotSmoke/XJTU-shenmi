import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from tslearn.metrics import cdist_dtw
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

plt.style.use('seaborn-v0_8')

# 创建图片保存目录
os.makedirs('plots', exist_ok=True)

# --------------------------
# 数据加载与预处理
# --------------------------
def load_and_preprocess(data_dir):
    """加载并标准化时间序列数据"""
    file_list = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    file_list.sort()
    
    time_series = []
    for file in file_list:
        data = np.loadtxt(os.path.join(data_dir, file))
        ts = data[:, 1]  # 提取数值序列
        time_series.append(ts)
    
    scaler = StandardScaler()
    return scaler.fit_transform(np.array(time_series)), file_list

# --------------------------
# 聚类算法模块
# --------------------------
def apply_slink(X, n_clusters=3):
    """层次聚类（Single Linkage）"""
    print("Calculating DTW distance matrix...")
    dtw_dist = cdist_dtw(X)
    condensed_dist = squareform(dtw_dist, force='tovector')
    linkage_matrix = linkage(condensed_dist, method='single')
    labels = fcluster(linkage_matrix, t=n_clusters, criterion='maxclust') - 1
    return labels, dtw_dist


class Mykmean:
    def __init__(self, n_clusters=3, max_iter=500, tol=1e-8, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centroids = None
        self.labels_ = None

    def fit_predict(self, X):
        np.random.seed(self.random_state)
        # 随机初始化中心点
        idx = np.random.choice(X.shape[0], self.n_clusters, replace=False)
        self.centroids = X[idx]
        
        for _ in range(self.max_iter):
            # 计算每个样本到各中心的距离
            distances = np.sqrt(((X[:, np.newaxis] - self.centroids)**2).sum(axis=2))
            labels = np.argmin(distances, axis=1)  # 分配标签
            
            # 计算新中心点
            new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(self.n_clusters)])
            
            # 判断是否收敛
            if np.all(np.abs(new_centroids - self.centroids) < self.tol):
                break
            self.centroids = new_centroids
        
        self.labels_ = labels
        return self.labels_






def apply_kmeans(X, n_clusters=3):
    """K-means聚类"""
    kmeans = Mykmean(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(X)

# --------------------------
# 可视化模块（添加保存功能）
# --------------------------
def plot_clusters(X, labels, method_name, data_type):
    """绘制PCA降维后的聚类分布"""
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab10', s=60)
    plt.title(f'{method_name} Clustering (PCA)')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.colorbar(scatter, label='Cluster')
    plt.grid(True)
    plt.savefig(f'plots/{method_name}_{data_type}_pca.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_time_series_clusters(X, labels, method_name):
    """绘制各簇代表性时序样本"""
    unique_labels = np.unique(labels)
    plt.figure(figsize=(12, 8))
    
    for i, label in enumerate(unique_labels):
        cluster_samples = X[labels == label]
        n_samples = len(cluster_samples)
        
        # 动态选择样本
        display_indices = np.random.choice(n_samples, min(3, n_samples), replace=False)
        
        plt.subplot(len(unique_labels), 1, i+1)
        for idx in display_indices:
            plt.plot(cluster_samples[idx], alpha=0.5, lw=1.5)
        plt.ylabel(f'Cluster {label}', rotation=0, ha='right', labelpad=20)
        plt.xticks([])
        plt.xlim(0, len(cluster_samples[0]))
    
    plt.suptitle(f"{method_name} Time Series Clusters")
    plt.tight_layout()
    plt.savefig(f'plots/{method_name}_ts_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_distance_heatmap(distance_matrix, labels, method_name):
    """绘制距离矩阵热力图"""
    sorted_indices = np.argsort(labels)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(distance_matrix[sorted_indices][:, sorted_indices], 
              cmap='viridis', aspect='auto')
    plt.colorbar(label='DTW Distance')
    plt.title(f"{method_name} Sorted Distance Matrix")
    plt.xlabel("Samples")
    plt.ylabel("Samples")
    plt.savefig(f'plots/{method_name}_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

# --------------------------
# 主流程
# --------------------------
def main():
    # 数据准备
    X, filenames = load_and_preprocess('test_data')
    
    # 执行两种聚类算法
    slink_labels, dtw_matrix = apply_slink(X)
    kmeans_labels = apply_kmeans(X)
    
    # 评估指标计算
    print(f"\nSLink 轮廓系数: {silhouette_score(dtw_matrix, slink_labels, metric='precomputed'):.3f}")
    print(f"K-means 轮廓系数: {silhouette_score(X, kmeans_labels):.3f}")
    
    # 可视化展示（生成6张图）
    # SLink可视化
    plot_clusters(X, slink_labels, "SLink", "features")
    plot_distance_heatmap(dtw_matrix, slink_labels, "SLink")
    plot_time_series_clusters(X, slink_labels, "SLink")
    
    # K-means可视化
    plot_clusters(X, kmeans_labels, "KMeans", "features")
    plot_distance_heatmap(dtw_matrix, kmeans_labels, "KMeans")
    plot_time_series_clusters(X, kmeans_labels, "KMeans")

if __name__ == "__main__":
    main()