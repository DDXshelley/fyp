#产生泊松数据流

import random
import numpy as np
import math

def poisson(lam, time, type):
    """
    产生泊松数据流
    :param lam:到达率,每us到达的数据包数目
    :param time: 时间区间,以us为单位
    :param rate: OLT传输速率,信道容量
    :return: arri, size
    """

    def E_packets(n,type):
        """
        产生数据包
        :param n: 需要产生的数据包
        :param rate:
        :return: pkt是数据包的持续时间,单位为us
        """
        # minimal = 64 + 8  # 最小64bytes + 8bytes preamble (+ 12bytes inter frame gap)
        # maximal = 1518 + 8
        if type == 1:
            pkt_size = 200 * np.ones(n) * 8 + 240
            # pkt_size = (minimal + np.floor(np.random.random() * (maximal - minimal + 1))) *np.ones(n) * 8 + 240  # bytes
        elif type == 2:
            pkt_size = 1500 * np.ones(n) * 8 + 240
            # pkt_size = (minimal + np.floor(np.random.random() * (maximal - minimal + 1))) *np.ones(n) * 8 + 240  # bytes

        #pkt_size = minimal + np.floor(np.random.random() * (maximal - minimal + 1))  # bytes
        pkt = pkt_size        #单位bit

        return pkt

    # arri = [[] for _ in range(4)]         #元胞数组的表达方式
    # size = [[] for _ in range(4)]         #元胞数组的表达方式

    arri = []
    size = []
    current = 0

    temp = np.random.exponential(scale=1.0/lam)# 随机生成符合指数分布的随机数

    while current + temp <= time:
        current = temp + current
        #seq = range(4)
        #target = random.choice(seq)
        #arri[target].append(current)
        #size[target].append(E_packets(1, rate))
        arri.append(current)
        size.append(E_packets(1, type))    #arri点对应的包大小

        temp = np.random.exponential(scale=1.0 / lam)

    return arri, size

# #计算测试
# lam = 286.8*0.5/(10*850*8)
# time = 1000000
# rate = 286.8
# [arri, size] = poisson(lam, time, rate, 1)
# # print("arri=", arri)
# print("size=", size[0])

# [arri, size] = poisson(lam, time, rate, 2)
# # print("arri=", arri)
# print("size=", size[0])