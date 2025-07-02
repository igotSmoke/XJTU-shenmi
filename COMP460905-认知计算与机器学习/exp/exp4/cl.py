# -*- coding: utf-8 -*-
# 修正后的cl.py
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
import sklearn.metrics as skm  # 添加缺失的metrics模块
import matplotlib.pyplot as plt  # 添加可视化模块
import kmeans as km
import linkage as lk
import dbscan as db

def load_iris_data():
    """载入并预处理iris数据集"""
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    # 标准化处理
    X = StandardScaler().fit_transform(X)
    return X, y

def test(x, y, cluster, modelName):
    """评估聚类结果"""
    print("\n" + "="*60)
    print(f"{modelName}聚类结果：")
    pred_label = cluster.labels_
    
    # 计算评估指标
    ari = skm.adjusted_rand_score(y, pred_label)
    nmi = skm.normalized_mutual_info_score(y, pred_label)
    print(f"ARI = {ari:.3f}, NMI = {nmi:.3f}")
    
    # 二维可视化（使用前两个特征）
    plt.figure(figsize=(8,4))
    plt.subplot(121)
    plt.scatter(x[:,0], x[:,1], c=y, cmap='viridis', s=20)
    plt.title("True Labels")
    
    plt.subplot(122)
    plt.scatter(x[:,0], x[:,1], c=pred_label, cmap='viridis', s=20)
    plt.title(f"{modelName} Clustering")
    plt.savefig(f"{modelName}_iris.png")
    plt.close()

if __name__ == '__main__':
    # 载入数据
    X, y = load_iris_data()
    
    # 测试KMeans
    kmeans_model = km.train(X, 3)  # 参数调整为仅接收簇数
    test(X, y, kmeans_model, "KMeans")
    
    # 测试层次聚类
    linkage_model = lk.train(X, 3, "average")
    test(X, y, linkage_model, "linkage")
    
    # 测试DBSCAN
    dbscan_model = db.train(X, 0.5, 5)
    test(X, y, dbscan_model, "DBSCAN")