import numpy as np
import os
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 读取数据
data = []
files = []
for prefix in ['A', 'B', 'C']:
    for i in range(1, 12):
        files.append(f"{prefix}{i}.txt")

for file in files:
    d = np.loadtxt(file)
    values = d[:, 1]
    data.append(values)

X = np.array(data)

# 全局标准化每个特征（时间点）
X = StandardScaler().fit_transform(X.T).T  # 转置标准化后再转回

# PCA降维（保留主成分直到95%方差）
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X)

# 使用降维后的数据进行聚类
X_cluster = X_pca  # 或使用原始数据 X

# K-Means聚类（优化参数）
best_k = 2
best_score = -1
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, n_init=20, random_state=42)
    labels = kmeans.fit_predict(X_cluster)
    if len(np.unique(labels)) < 2:
        continue  # 跳过无效聚类
    score = silhouette_score(X_cluster, labels)
    if score > best_score:
        best_score = score
        best_k = k

kmeans = KMeans(n_clusters=best_k, n_init=20, random_state=42)
kmeans_labels = kmeans.fit_predict(X_cluster)
kmeans_score = silhouette_score(X_cluster, kmeans_labels)

# 层次聚类（自动选择最佳链接方式和K）
best_hc_score = -1
best_hc_k = 2
best_linkage = 'ward'

for linkage in ['ward', 'complete', 'average']:
    for k in range(2, 11):
        hc = AgglomerativeClustering(n_clusters=k, linkage=linkage)
        labels = hc.fit_predict(X_cluster)
        if len(np.unique(labels)) < 2:
            continue
        score = silhouette_score(X_cluster, labels)
        if score > best_hc_score:
            best_hc_score = score
            best_hc_k = k
            best_linkage = linkage

hc = AgglomerativeClustering(n_clusters=best_hc_k, linkage=best_linkage)
hc_labels = hc.fit_predict(X_cluster)
hc_score = silhouette_score(X_cluster, hc_labels)

# 可视化（使用前两个主成分）
pca_vis = PCA(n_components=2)
X_vis = pca_vis.fit_transform(X)

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.scatter(X_vis[:, 0], X_vis[:, 1], c=kmeans_labels, cmap='viridis')
plt.title(f'K-Means (k={best_k}, Sil={kmeans_score:.2f})')

plt.subplot(1, 2, 2)
plt.scatter(X_vis[:, 0], X_vis[:, 1], c=hc_labels, cmap='viridis')
plt.title(f'Hierarchical ({best_linkage}, k={best_hc_k}, Sil={hc_score:.2f})')

plt.tight_layout()
plt.savefig('improved_clusters.png')
plt.close()

print(f"K-Means Silhouette: {kmeans_score:.4f}")
print(f"Hierarchical Silhouette: {hc_score:.4f}")