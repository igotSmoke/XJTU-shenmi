import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

files = []
for prefix in ['A', 'B', 'C']:
    for i in range(1, 12):
        files.append(f"{prefix}{i}.txt")

data = []
for file in files:
    d = np.loadtxt(file)
    values = d[:, 1]
    data.append(values)
X = np.array(data)
X = np.array([(x - x.mean())/x.std() for x in data])

# PCA降维
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X)
X_cluster = X_pca


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




class Myslink:
    def __init__(self, n_clusters=2):
        self.n_clusters = n_clusters
        self.labels_ = None

    def fit_predict(self, X):
        n = X.shape[0]
        clusters = [[i] for i in range(n)]  # 初始每个样本为一个簇
        
        while len(clusters) > self.n_clusters:
            min_dist = np.inf
            merge_i, merge_j = -1, -1
            
            # 遍历所有簇对寻找最小距离
            for i in range(len(clusters)):
                for j in range(i+1, len(clusters)):
                    # 计算单链接距离（簇间最近样本距离）
                    dist = min(np.sqrt(np.sum((X[a] - X[b])**2)) 
                               for a in clusters[i] for b in clusters[j])
                    if dist < min_dist:
                        min_dist, merge_i, merge_j = dist, i, j
            
            # 合并簇
            clusters[merge_i].extend(clusters[merge_j])
            del clusters[merge_j]
        
        # 生成最终标签
        self.labels_ = np.zeros(n, dtype=int)
        for label, cluster in enumerate(clusters):
            for idx in cluster:
                self.labels_[idx] = label
        return self.labels_


# 手动K-Means聚类
best_k, best_score = 2, -1
for k in range(2, 11):
    model = Mykmean(n_clusters=k, random_state=42)
    labels = model.fit_predict(X_cluster)
    if len(np.unique(labels)) < 2:
        continue
    score = silhouette_score(X_cluster, labels)
    if score > best_score:
        best_k, best_score = k, score

mykmeans = Mykmean(n_clusters=best_k, random_state=42)
kmeans_labels = mykmeans.fit_predict(X_cluster)
kmeans_score = silhouette_score(X_cluster, kmeans_labels)

# 手动层次聚类
best_hc_k, best_hc_score = 2, -1
for k in range(2, 11):
    model = Myslink(n_clusters=k)
    labels = model.fit_predict(X_cluster)
    if len(np.unique(labels)) < 2:
        continue
    score = silhouette_score(X_cluster, labels)
    if score > best_hc_score:
        best_hc_k, best_hc_score = k, score

myslink = Myslink(n_clusters=best_hc_k)
hc_labels = myslink.fit_predict(X_cluster)
hc_score = silhouette_score(X_cluster, hc_labels)

# 可视化
pca_vis = PCA(n_components=2)
X_vis = pca_vis.fit_transform(X)

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.scatter(X_vis[:, 0], X_vis[:, 1], c=kmeans_labels, cmap='viridis')
plt.title(f'MyKMeans (k={best_k}, Sil={kmeans_score:.2f})')

plt.subplot(1, 2, 2)
plt.scatter(X_vis[:, 0], X_vis[:, 1], c=hc_labels, cmap='viridis')
plt.title(f'MySingleLink (k={best_hc_k}, Sil={hc_score:.2f})')

plt.tight_layout()
plt.savefig('manual_clusters.png')
plt.close()

print(f"MyKMeans Silhouette: {kmeans_score:.4f}")
print(f"MySingleLink Silhouette: {hc_score:.4f}")