# -*- coding: utf-8 -*-
from sklearn.cluster import DBSCAN
import time


ModelName = "DBSCAN聚类算法"
def train(data, *args):
    print("开始%s过程..." % ModelName)
    startT = time.time()
    '''
    eps_para,min_samples_para: the parameters need to be manually specified.
    '''
    cluster = DBSCAN(eps=args[0], min_samples=args[1]).fit(data)
    endT = time.time()
    print("%s过程结束。处理了%d个数据点，耗时%f秒。" % (ModelName, data.shape[0], (endT - startT)))
    return cluster
