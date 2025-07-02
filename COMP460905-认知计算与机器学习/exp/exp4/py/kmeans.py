# -*- coding: utf-8 -*-
from sklearn.cluster import KMeans
import time


ModelName = "KMeans聚类算法"
def train(data, *args):
    print("开始%s过程..." % ModelName)
    startT = time.time()
    '''cluster centers are randomly initited'''
    cluster = KMeans(n_clusters=args[0], init='random').fit(data)
    endT = time.time()
    print("%s过程结束。处理了%d个数据点，耗时%f秒。" % (ModelName, data.shape[0], (endT - startT)))
    return cluster
