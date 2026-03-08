import numpy as np
from scipy import stats
import random
import math
import E_poisson
import UORA_count
import analysis_new
import math
import matplotlib.pyplot as plt

#第三章方案
# #仿真参数
# N_SFU = 1
# N_STA = 10            #假设所有STA都是RTA STA，全参与竞争，指定分配暂不考虑
# CWOmin = [3,3]
# CWOmax = [15,15]
# duration = 1000000
# tTXOP = 1000
# N_TU_total = 512
# gama = [0.5]
# N_RU = 9

def transmission(N_SFU,N_STA,gama,N_RU,N_TU_total,CWOmax,CWOmin,duration,tTXOP):

    # 固定参数
    load_w = 0.5
    tSIFS = 16
    tTF = 100
    tBA = 68
    tBSRP = 100
    tBSR = 20
    distance_pon = 1
    rate_wifi = 1*26*N_RU*10*5/6/(12.8+0.8)
    rate_subcarrierblock = 10000 / N_TU_total
    rate_RU = 50  #1*26*10*5/6/(12.8+0.8)
    tProcess = 100
    tTrans_w = 1
    tTrans_p = distance_pon * 5
    tim =  tBSRP + tSIFS + tTrans_p * 1 + tTrans_w * 1 + tProcess * 3
    # T = tTXOP + tSIFS + tTrans_w * 3 + tTrans_p *3 + tProcess * 9
    slot = tTXOP + tSIFS + tTrans_w * 3 + tTrans_p * 3 + tProcess * 9
    # tPPDU = tTXOP - tTF - tBA - tSIFS * 2
    tPPDU = tTXOP
    T = tPPDU + tTF + tBA + tSIFS * 2 + tSIFS + tBA + tSIFS + tBSRP + tSIFS + tTrans_p * 3 + tTrans_w * 3 + tProcess * 9
    phy_overhead_wifi = 40                #wifi物理层开销
    pon_overhead_fs = 32                  #pon物理层开销 ,FS header + PSBu  32bit + 4Byte

    # 初始化参数
    Arri = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    Size = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    pack_num = np.zeros((N_SFU, N_STA), dtype=int)

    buff_A = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    buff_S = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    arri_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    size_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    arri_data = [[] for _ in range(N_TU_total)]
    size_data = [[] for _ in range(N_TU_total)]

    start_time = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    end_time = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    receive_num = np.zeros((N_SFU, N_STA), dtype=int)
    receive_cycle_num = np.zeros((N_SFU, N_STA), dtype=int)
    remain_num = np.zeros((N_SFU, N_STA), dtype=int)
    latency = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    jitter = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]


    buffer_interface = np.zeros((N_SFU, N_STA))
    mean_latency = np.zeros((N_SFU, N_STA))
    mean_jitter = np.zeros((N_SFU, N_STA))
    tosend_ts_bsr = np.zeros((N_SFU, N_STA), dtype=int)
    tosend = np.zeros((N_SFU, N_STA), dtype=int)
    tosend_total = np.zeros((N_SFU, N_STA), dtype=int)
    alphas = np.zeros(N_SFU)
    N_accesspon = 0
    N_STA_total = 0
    N_accesswifi = 0
    N_accesspon_ts  = 0
    N_accesspon_nts  = 0
    N_RU_totalnum = 0
    N_RU_totalts = 0
    N_RU_totalnts = 0
    N_TU_totalnum = 0
    N_accesswifi_ts = 0
    N_accesswifi_nts = 0
    N_TS_total = 0
    N_NTS_total = 0
    Timer = tim
    occupy_ts = 0
    alloc_ts = 0
    occupy_nts = 0
    alloc_nts = 0

    RU_fix = np.zeros((N_SFU), dtype=int)          #用于固定分配的RU
    RU_random = np.zeros((N_SFU), dtype=int)       #用于随机竞争的RU
    TU_fix = np.zeros((N_SFU), dtype=int)
    TU_random = np.zeros((N_SFU), dtype=int)
    TU = np.zeros((N_SFU), dtype=int)
    N_BSR_ts = np.zeros((N_SFU), dtype=int)
    N_contention = np.zeros((N_SFU), dtype=int)
    RU_ts = np.zeros((N_SFU), dtype=int)          #用于固定分配的RU

    #划分两种业务的STA
    N_TS_STA = np.zeros(N_SFU)
    N_NTS_STA = np.zeros(N_SFU)
    Set_TS_STA = [[] for _ in range(N_SFU)]
    Set_NTS_STA = [[] for _ in range(N_SFU)]

    for i in range(N_SFU):
        N_TS_STA[i] = int(math.ceil(gama[i] * N_STA))   #TS STA的个数
        N_NTS_STA[i] = N_STA - N_TS_STA[i]  
        if N_TS_STA[i] != 0:
            while len(Set_TS_STA[i]) < N_TS_STA[i]:
                num = random.randint(0,N_STA-1)
                if num not in Set_TS_STA[i]:
                    Set_TS_STA[i].append(num)
                    Set_TS_STA[i] = sorted(Set_TS_STA[i])
            for j in range (N_STA):
                if j not in Set_TS_STA[i]:
                    Set_NTS_STA[i].append(j)
                    Set_NTS_STA[i] = sorted(Set_NTS_STA[i])
        else:
            while len(Set_NTS_STA[i]) < N_NTS_STA[i]:
                num = random.randint(0,N_STA-1)
                if num not in Set_NTS_STA[i]:
                    Set_NTS_STA[i].append(num)
                    Set_NTS_STA[i] = sorted(Set_NTS_STA[i])

    # 计算到达率
    lam_ts = 400/1000000
    lam_nts = 200/1000000

    # 给每个STA产生数据包
    for i in range(N_SFU):
        for j in range(N_STA):
            if j in Set_TS_STA[i]:
            # 给每个STA产生数据包
                [arri, size] = E_poisson.poisson(lam_ts, duration,1)
                Arri[i][j] = arri
                Size[i][j] = size
                buff_A[i][j] = arri
                buff_S[i][j] = size
                pack_num[i,j] = len(arri)
                remain_num[i,j] = len(arri)  
            elif j in Set_NTS_STA[i]:
                [arri, size] = E_poisson.poisson(lam_nts, duration,2)
                Arri[i][j] = arri
                Size[i][j] = size
                buff_A[i][j] = arri
                buff_S[i][j] = size
                pack_num[i,j] = len(arri)  
                remain_num[i,j] = len(arri)            

            # 初始化 receive_time 和 latency 数组
            start_time[i][j] = np.zeros(pack_num[i,j])
            end_time[i][j] = np.zeros(pack_num[i,j])
            latency[i][j] = np.zeros(pack_num[i,j])
            jitter[i][j] = np.zeros(pack_num[i,j]-1)

    contention_bsr = np.zeros((N_SFU,N_STA))
    contention = np.zeros((N_SFU,N_STA))
    A_CWO = np.ones((N_SFU,N_STA))              #竞争窗口
    A_BO = np.zeros((N_SFU, N_STA))
    A_Retry = np.zeros((N_SFU, N_STA))
    CWOmin_list = np.zeros((N_SFU, N_STA))
    CWOmax_list = np.zeros((N_SFU, N_STA))

    for i in range (N_SFU):
        for j in range (N_STA):
            if j in Set_TS_STA[i]:
                CWOmax_list[i,j] = CWOmax[0]
                CWOmin_list[i,j] = CWOmin[0]
                A_CWO[i,j] = CWOmin[0]
                A_BO[i,j] = random.randint(1,A_CWO[i,j])
            else:
                CWOmax_list[i,j] = CWOmax[1]
                CWOmin_list[i,j] = CWOmin[1]
                A_CWO[i,j] = CWOmin[1]
                A_BO[i,j] = random.randint(1,A_CWO[i,j])

    #第一个周期
    #STA判断是否有数据要发送
    for i in range(N_SFU):
        for j in range(N_STA):
            if Arri[i][j][0] <= tim:
                if j in Set_TS_STA[i]:
                    tosend_ts_bsr[i,j] = 1                   #BSR阶段有数据要发送的TS STA

        #BSR采用UORA过程，得到哪几个STA成功发送了BSR
        [contention_bsr[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts_bsr[i], 1, N_STA, N_RU, A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])
        N_BSR_ts[i] = sum(contention_bsr[i])
        N_contention[i] = N_STA - N_BSR_ts[i]
        # N_accesswifi_ts = N_accesswifi_ts + N_BSR_ts[i]

    #初始分配RU与TU
    for i in range (N_SFU):
        RU_fix[i] = N_BSR_ts[i]
        RU_random[i] = N_RU - RU_fix[i]
        TU_fix[i] = RU_fix[i]
        if N_contention[i] != 0:
            RU_ts[i] = int(math.ceil(RU_random[i]*((N_TS_STA[i]-N_BSR_ts[i])/N_contention[i])))
            N_RU_totalts += RU_fix[i] + RU_ts[i]
            N_RU_totalnts += RU_random[i] - RU_ts[i]
        else:
            N_RU_totalts += N_RU
            N_RU_totalnts += 0
        #根据公式动态计算所需的光资源
        [_,alphas[i]]=analysis_new.tau(N_contention[i], RU_random[i], CWOmin[1], CWOmax[1])
        TU_random[i] = int(math.ceil(alphas[i] * RU_random[i]))

    if (sum(TU_fix)+sum(TU_random)) <= N_TU_total:
        for i in range (N_SFU):
            TU[i] = TU_fix[i] + TU_random[i]
    else:
        if sum(TU_fix) <= N_TU_total:
            for i in range (N_SFU):
                TU[i] = TU_fix[i] + (N_TU_total-sum(TU_fix))*(TU_random[i]/(sum(TU_random)))
        else:
            for i in range (N_SFU):
                TU[i] = (TU_fix[i]/sum(TU_fix))*N_TU_total

    #判断是否有新到来的数据
    Timer += tBSR + tSIFS + tTF + tSIFS 
    for i in range(N_SFU):
        for j in range (N_STA):
            if Arri[i][j][0] <= Timer:
                tosend[i,j] = 1
                tosend_total[i,j] = 1
                if contention_bsr[i,j] == 1:
                    tosend[i,j] = 0                       #找出需要随机接入的STA
                if j in Set_TS_STA[i]:
                    N_TS_total += 1
                else:
                    N_NTS_total += 1
            
    #第二阶段的随机接入过程
    for i in range (N_SFU):
        if sum(tosend[i]) > 0:                                      #有数据要发，则竞争
            [contention[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend[i], 1, N_STA, RU_random[i], A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])

    #Wi-Fi传输部分
    for i in range (N_SFU):  
        for j in range (N_STA):
            if contention_bsr[i,j] == 1:
                N_accesswifi_ts += 1
                N_accesswifi += 1 
                alloc_ts += rate_RU*tTXOP
                sum_size = 0
                for k in range (pack_num[i,j]):
                    if buff_A[i][j][k] <= Timer:
                        sum_size = sum_size + buff_S[i][j][k]/rate_RU
                        if sum_size + phy_overhead_wifi <= tPPDU:
                            arri_data_ap[i][j].append(buff_A[i][j][k])
                            size_data_ap[i][j].append(buff_S[i][j][k])
                            occupy_ts += buff_S[i][j][k][0]
            if contention[i,j] == 1:
                N_accesswifi += 1 
                if j in Set_TS_STA[i]:
                    N_accesswifi_ts += 1
                    alloc_ts += rate_RU*tTXOP
                else:
                    N_accesswifi_nts += 1
                    alloc_nts += rate_RU*tTXOP
                sum_size = 0
                for k in range (pack_num[i,j]):
                    if buff_A[i][j][k] <= Timer:
                        sum_size = sum_size + buff_S[i][j][k]/rate_RU
                        if sum_size + phy_overhead_wifi <= tPPDU:
                            arri_data_ap[i][j].append(buff_A[i][j][k])
                            size_data_ap[i][j].append(buff_S[i][j][k])
                            if j in Set_TS_STA[i]:
                                occupy_ts += buff_S[i][j][k][0]
                            else:
                                occupy_nts += buff_S[i][j][k][0]

    #光传输部分
    g = 0
    for i in range (N_SFU):  
        m = 0
        #先计算固定分配的部分
        for j in range (N_STA):
            if contention_bsr[i,j] == 1:
                if m < TU[i]:
                    N_accesspon_ts += 1
                    receive_cycle_num[i,j] = 0
                    arri_data[g].append(arri_data_ap[i][j])
                    size_data[g].append(size_data_ap[i][j])
                    g += 1
                    m += 1

                    #计算buffer中没传完剩余的buffer 
                    receive_cycle_num[i,j] = len(arri_data_ap[i][j])
                    receive_num[i,j] = receive_num[i,j] + receive_cycle_num[i,j]
                    if pack_num[i,j] == receive_num[i,j]:
                        buff_A[i][j] = []
                        buff_S[i][j] = []
                        remain_num[i,j] = 0
                    elif pack_num[i,j] > receive_num[i,j]:
                        buff_A[i][j] = buff_A[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        buff_S[i][j] = buff_S[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        remain_num[i,j] = len(buff_A[i][j])

                    #计算接收时间
                    #第一个数
                    start_time[i][j][0] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                    end_time[i][j][0] = start_time[i][j][0] + size_data_ap[i][j][0]/ rate_RU
                    buffer_interface[i,j] = buffer_interface[i,j] + phy_overhead_wifi + size_data_ap[i][j][0]
                    if buffer_interface[i,j] >= 1500*8:           #满1500加一个帧头
                        end_time[i][j][0] += (18 + size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock         #加上PON MAC和PHY的封装
                        buffer_interface[i,j] = 0
                    else:
                        end_time[i][j][0] += (size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock

                    #后面的数
                    if receive_cycle_num[i,j] > 1:
                        for k in range (1,receive_cycle_num[i,j]):
                            end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k]/ rate_RU
                            buffer_interface[i,j] = buffer_interface[i,j] + size_data_ap[i][j][k]
                            if buffer_interface[i,j] >= 1500*8:
                                end_time[i][j][k] += (18+size_data_ap[i][j][k])/ rate_subcarrierblock
                                buffer_interface[i,j] = 0
                            elif buffer_interface[i,j] < 1500*8:
                                    end_time[i][j][k] += size_data_ap[i][j][k]/ rate_subcarrierblock           

        #再计算随机接入的部分
        for j in range (N_STA):
            if contention[i,j] == 1:
                receive_cycle_num[i,j] = 0
                if m < TU[i]:                    
                    arri_data[g].append(arri_data_ap[i][j])
                    size_data[g].append(size_data_ap[i][j])
                    g += 1
                    m += 1
                    if j in Set_TS_STA[i]:
                        N_accesspon_ts += 1
                    else:
                        N_accesspon_nts += 1

                    #计算buffer中没传完剩余的buffer 
                    receive_cycle_num[i,j] = len(arri_data_ap[i][j])
                    receive_num[i,j] = receive_num[i,j] + receive_cycle_num[i,j]
                    if pack_num[i,j] == receive_num[i,j]:
                        buff_A[i][j] = []
                        buff_S[i][j] = []
                        remain_num[i,j] = 0
                    elif pack_num[i,j] > receive_num[i,j]:
                        buff_A[i][j] = buff_A[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        buff_S[i][j] = buff_S[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        remain_num[i,j] = len(buff_A[i][j])

                    #计算接收时间
                    #第一个数
                    start_time[i][j][0] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                    end_time[i][j][0] = start_time[i][j][0] + size_data_ap[i][j][0]/ rate_RU
                    buffer_interface[i,j] = buffer_interface[i,j] + phy_overhead_wifi + size_data_ap[i][j][0]
                    if buffer_interface[i,j] >= 1500*8:           #满1500加一个帧头
                        end_time[i][j][0] += (18 + size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock         #加上PON MAC和PHY的封装
                        buffer_interface[i,j] = 0
                    else:
                        end_time[i][j][0] += (size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock

                    #后面的数
                    if receive_cycle_num[i,j] > 1:
                        for k in range (1,receive_cycle_num[i,j]):
                            end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k]/ rate_RU
                            buffer_interface[i,j] = buffer_interface[i,j] + size_data_ap[i][j][k]
                            if buffer_interface[i,j] >= 1500*8:
                                end_time[i][j][k] += (18+size_data_ap[i][j][k])/ rate_subcarrierblock
                                buffer_interface[i,j] = 0
                            elif buffer_interface[i,j] < 1500*8:
                                end_time[i][j][k] += size_data_ap[i][j][k]/ rate_subcarrierblock        

    h = 0
    for i in range (N_TU_total):
        if len(arri_data[i]) != 0:
            h += 1
    Timer += T 
    N_STA_total = N_STA_total + sum(sum(tosend_total)) 
    N_accesspon  = N_accesspon + h
    N_RU_totalnum = N_RU_totalnum + N_RU*N_SFU
    N_TU_totalnum = N_TU_totalnum + sum(TU)

    s = 0
    #循环=======================================================================================
    while True:
        s += 1
        tosend_ts_bsr = np.zeros((N_SFU, N_STA), dtype=int)
        tosend = np.zeros((N_SFU, N_STA), dtype=int)
        tosend_total = np.zeros((N_SFU, N_STA), dtype=int)
        contention_bsr = np.zeros((N_SFU, N_STA), dtype=int)
        contention = np.zeros((N_SFU, N_STA), dtype=int)
        buffer_interface = np.zeros((N_SFU, N_STA))
        RU_fix = np.zeros((N_SFU), dtype=int)
        RU_ts = np.zeros((N_SFU), dtype=int)          #用于固定分配的RU
        RU_random = np.zeros((N_SFU), dtype=int)
        TU_fix = np.zeros((N_SFU), dtype=int)
        TU_random = np.zeros((N_SFU), dtype=int)
        TU = np.zeros((N_SFU), dtype=int)

        arri_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]  #%每个周期成功接入的STA传给ONU的数据的到达时间点
        size_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]  #每个周期成功接入的STA传给ONU的数据的大小
        arri_data = [[] for _ in range(N_TU_total)]                       #成功传输得到PON的数据到达时间点
        size_data = [[] for _ in range(N_TU_total)]                       #成功传输得到PON的数据包大小
        receive_cycle_num = np.zeros((N_SFU, N_STA), dtype=int)
        N_BSR_ts = np.zeros((N_SFU), dtype=int)
        N_contention = np.zeros((N_SFU), dtype=int)
        alphas = np.zeros((N_SFU))

        #判断是否有数据发送
        for i in range (N_SFU):     
            for j in range (N_STA):
                if remain_num[i,j] > 0:
                    if buff_A[i][j][0] <= Timer:
                        if j in Set_TS_STA[i]:
                            tosend_ts_bsr[i,j] = 1

        #BSR采用UORA过程，得到哪几个STA成功发送了BSR
        for i in range (N_SFU):
            [contention_bsr[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts_bsr[i], 1, N_STA, N_RU, A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])
            N_BSR_ts[i] = sum(contention_bsr[i])
            N_contention[i] = N_STA - N_BSR_ts[i]
            # N_accesswifi_ts = N_accesswifi_ts + N_BSR_ts[i]

            #分配RU，根据数量分配
            RU_fix[i] = N_BSR_ts[i]
            RU_random[i] = N_RU - RU_fix[i]
            TU_fix[i] = RU_fix[i]
            if N_contention[i] != 0:
                RU_ts[i] = int(math.ceil(RU_random[i]*((N_TS_STA[i]-N_BSR_ts[i])/N_contention[i])))  
                N_RU_totalts += RU_fix[i] + RU_ts[i]
                N_RU_totalnts += RU_random[i] - RU_ts[i]
            else:
                RU_ts[i] = 0
                N_RU_totalts += N_RU
                N_RU_totalnts += 0
            
            if N_contention[i] > 0 and RU_random[i] > 0:
                [_,alphas[i]]=analysis_new.tau(N_contention[i], RU_random[i], CWOmin[0], CWOmax[0])
                TU_random[i] = int(math.ceil(alphas[i] * RU_random[i])) 

        if (sum(TU_fix)+sum(TU_random)) <= N_TU_total:
            for i in range (N_SFU):
                TU[i] = TU_fix[i] + TU_random[i]
        else:
            if sum(TU_fix) <= N_TU_total:
                for i in range (N_SFU):
                    TU[i] = TU_fix[i] + (N_TU_total-sum(TU_fix))*(TU_random[i]/(sum(TU_random)))
            else:
                TU[i] = N_TU_total*TU_fix[i]/sum(TU_fix)


        Timer += tBSR + tSIFS + tTF + tSIFS 
        for i in range(N_SFU):
            for j in range (N_STA):
                if remain_num[i,j] > 0:
                    if buff_A[i][j][0] <= Timer:
                        tosend[i,j] = 1
                        tosend_total[i,j] = 1
                        if contention_bsr[i,j] == 1:
                            tosend[i,j] = 0
                        if j in Set_TS_STA[i]:
                            N_TS_total += 1
                        else:
                            N_NTS_total += 1 

        #第二阶段的随机接入过程
        for i in range (N_SFU):
            if sum(tosend[i]) > 0:
                [contention[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend[i], 1, N_STA, RU_random[i], A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])                         
        #无线传输部分
        for i in range (N_SFU):
            for j in range (N_STA):
                if contention_bsr[i,j] == 1:
                    N_accesswifi += 1 
                    N_accesswifi_ts += 1
                    sum_size = 0
                    alloc_ts += rate_RU*tTXOP
                    for k in range (remain_num[i,j]):
                        if buff_A[i][j][k] <= Timer:
                            sum_size = sum_size + buff_S[i][j][k]/rate_RU
                            if sum_size + phy_overhead_wifi <= tPPDU:
                                arri_data_ap[i][j].append(buff_A[i][j][k])
                                size_data_ap[i][j].append(buff_S[i][j][k])
                                occupy_ts += buff_S[i][j][k][0]
                if contention[i,j] == 1:
                    N_accesswifi += 1 
                    if j in Set_TS_STA[i]:
                        N_accesswifi_ts += 1
                        alloc_ts += rate_RU*tTXOP
                    else:
                        N_accesswifi_nts += 1
                        alloc_nts += rate_RU*tTXOP
                    sum_size = 0
                    for k in range (remain_num[i,j]):
                        if buff_A[i][j][k] <= Timer:
                            sum_size = sum_size + buff_S[i][j][k]/rate_RU
                            if sum_size + phy_overhead_wifi <= tPPDU:
                                arri_data_ap[i][j].append(buff_A[i][j][k])
                                size_data_ap[i][j].append(buff_S[i][j][k])
                                if j in Set_TS_STA[i]:
                                    occupy_ts += buff_S[i][j][k][0]
                                else:
                                    occupy_nts += buff_S[i][j][k][0]

        #光传输部分
        g = 0
        for i in range (N_SFU):  
            m = 0
            for j in range (N_STA):
                if contention_bsr[i,j] == 1:
                    if m < TU[i]:
                        N_accesspon_ts += 1
                        arri_data[g].append(arri_data_ap[i][j])
                        size_data[g].append(size_data_ap[i][j])
                        receive_cycle_num[i,j] = len(arri_data_ap[i][j]) 
                        g += 1
                        m += 1

                        #计算接收时间
                        #第一个数
                        start_time[i][j][receive_num[i,j]] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                        end_time[i][j][receive_num[i,j]] = start_time[i][j][receive_num[i,j]] + size_data_ap[i][j][0]/ rate_RU
                        buffer_interface[i,j] = buffer_interface[i,j] + phy_overhead_wifi + size_data_ap[i][j][0]
                        if buffer_interface[i,j] >= 1500*8:           #满1500加一个帧头
                            end_time[i][j][receive_num[i,j]] += (18 + size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock         #加上PON MAC和PHY的封装
                            buffer_interface[i,j] = 0
                        else:
                            end_time[i][j][receive_num[i,j]] += (size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock
                        #后面的数
                        if receive_cycle_num[i,j] > 1:
                            for k in range ((receive_num[i,j]+1),(receive_num[i,j]+receive_cycle_num[i,j])):
                                end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k-receive_num[i,j]]/ rate_RU
                                buffer_interface[i,j] = buffer_interface[i,j] + size_data_ap[i][j][k-receive_num[i,j]]
                                if buffer_interface[i,j] >= 1500*8:
                                    end_time[i][j][k] += (18+size_data_ap[i][j][k-receive_num[i,j]])/ rate_subcarrierblock
                                    buffer_interface[i,j] = 0
                                elif buffer_interface[i,j] < 1500*8:
                                    end_time[i][j][k] += size_data_ap[i][j][k-receive_num[i,j]]/ rate_subcarrierblock                                                                       
                        
                        receive_num[i,j] = receive_num[i,j] + receive_cycle_num[i,j]
                        if pack_num[i,j] == receive_num[i,j]:
                            buff_A[i][j] = []
                            buff_S[i][j] = []
                            remain_num[i,j] = 0
                        elif pack_num[i,j] > receive_num[i,j]:
                            buff_A[i][j] = buff_A[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                            buff_S[i][j] = buff_S[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                            remain_num[i,j] = len(buff_A[i][j])
                
            for j in range (N_STA):
                if contention[i,j] == 1:
                    if m < TU[i]:
                        arri_data[g].append(arri_data_ap[i][j])
                        size_data[g].append(size_data_ap[i][j])
                        receive_cycle_num[i,j] = len(arri_data_ap[i][j]) 
                        g += 1
                        m += 1
                        if j in Set_TS_STA[i]:
                            N_accesspon_ts += 1
                        else:
                            N_accesspon_nts += 1

                        #计算接收时间
                        #第一个数
                        start_time[i][j][receive_num[i,j]] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                        end_time[i][j][receive_num[i,j]] = start_time[i][j][receive_num[i,j]] + size_data_ap[i][j][0]/ rate_RU
                        buffer_interface[i,j] = buffer_interface[i,j] + phy_overhead_wifi + size_data_ap[i][j][0]
                        if buffer_interface[i,j] >= 1500*8:           #满1500加一个帧头
                            end_time[i][j][receive_num[i,j]] += (18 + size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock         #加上PON MAC和PHY的封装
                            buffer_interface[i,j] = 0
                        else:
                            end_time[i][j][receive_num[i,j]] += (size_data_ap[i][j][0] + pon_overhead_fs + 4 * 8)/ rate_subcarrierblock
                        #后面的数
                        if receive_cycle_num[i,j] > 1:
                            for k in range ((receive_num[i,j]+1),(receive_num[i,j]+receive_cycle_num[i,j])):
                                end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k-receive_num[i,j]]/ rate_RU
                                buffer_interface[i,j] = buffer_interface[i,j] + size_data_ap[i][j][k-receive_num[i,j]]
                                if buffer_interface[i,j] >= 1500*8:
                                    end_time[i][j][k] += (18+size_data_ap[i][j][k-receive_num[i,j]])/ rate_subcarrierblock
                                    buffer_interface[i,j] = 0
                                elif buffer_interface[i,j] < 1500*8:
                                    end_time[i][j][k] += size_data_ap[i][j][k-receive_num[i,j]]/ rate_subcarrierblock                                                                     
                        
                        receive_num[i,j] = receive_num[i,j] + receive_cycle_num[i,j]
                        if pack_num[i,j] == receive_num[i,j]:
                            buff_A[i][j] = []
                            buff_S[i][j] = []
                            remain_num[i,j] = 0
                        elif pack_num[i,j] > receive_num[i,j]:
                            buff_A[i][j] = buff_A[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                            buff_S[i][j] = buff_S[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                            remain_num[i,j] = len(buff_A[i][j])

        for i in range (N_SFU):
            if sum(tosend_total[i]) == 0:
                Timer += 100
            else:
                N_RU_totalnum = N_RU_totalnum + N_RU

        h = 0
        for i in range (N_TU_total):
            if len(arri_data[i]) != 0:
                h += 1

        Timer += T
        N_STA_total = N_STA_total + sum(sum(tosend_total)) 
        N_accesspon  = N_accesspon + h
        N_TU_totalnum = N_TU_totalnum + sum(TU)

        # v = sum(TU)
        # print('----------------')
        # print('TU_fix=',TU_fix)
        # print('TU=',v)
        # print('h=',h)


        if np.array_equal(receive_num,pack_num):
            break
        else:
            continue


    #计算时延和抖动
    latency_ts_sum = np.zeros(N_SFU)
    latency_nts_sum = np.zeros(N_SFU)
    jitter_ts_sum = np.zeros(N_SFU)
    jitter_nts_sum = np.zeros(N_SFU)
    latency1 = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    jitter1 = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    for i in range (N_SFU):
        for j in range (N_STA):
            #计算latency
            for k in range (pack_num[i,j]):
                latency[i][j][k] = end_time[i][j][k] - Arri[i][j][k]
                if k > 0:
                    jitter[i][j][k-1] = abs((end_time[i][j][k] - Arri[i][j][k])-(end_time[i][j][k-1] - Arri[i][j][k-1]))

            latency[i][j] = sorted(latency[i][j]) 
            jitter[i][j] = sorted(latency[i][j]) 
            for k in range ((math.ceil(pack_num[i,j]*0.05)),(pack_num[i,j]-math.ceil(pack_num[i,j]*0.05))):
                latency1[i][j].append(latency[i][j][k])
                jitter1[i][j].append(jitter[i][j][k])
            
            mean_latency[i,j] = np.mean(latency1[i][j])
            # mean_jitter[i][j] = np.std(latency1[i][j])   
            mean_jitter[i,j] = np.mean(jitter1[i][j])

    for i in range (N_SFU):
        for j in range (N_STA):
            if j in Set_TS_STA[i]:
                latency_ts_sum[i] += mean_latency[i,j]
                jitter_ts_sum[i] += mean_jitter[i,j]
            else:
                latency_nts_sum[i] += mean_latency[i,j]
                jitter_nts_sum[i] += mean_jitter[i,j]  

    latency_ts = None
    latency_nts = None
    jitter_ts = None
    jitter_nts = None
    if sum(N_TS_STA) != 0:     
        latency_ts = sum(latency_ts_sum)/sum(N_TS_STA)   
        jitter_ts = sum(jitter_ts_sum)/sum(N_TS_STA)
    else:
        latency_ts = None
        jitter_ts = None

    if sum(N_NTS_STA) != 0: 
        latency_nts = sum(latency_nts_sum)/sum(N_NTS_STA)
        jitter_nts = sum(jitter_nts_sum)/sum(N_NTS_STA)
    else:
        latency_nts = None
        jitter_nts = None

    #计算资源利用率
    Ut_RU = N_accesswifi/N_RU_totalnum
    Ut_RU_ts = (N_accesswifi_ts+N_accesswifi_nts)/N_RU_totalnum            #比的是RU个数
    Ut_RU_nts = N_accesswifi_nts/N_RU_totalnum
    Ut_TU = N_accesspon/N_TU_totalnum
    # Ut_TU_ts = N_accesspon_ts/N_TU_totalnum
    # Ut_TU_nts = N_accesspon_nts/N_TU_totalnum

    RU_effciency_ts = occupy_ts/alloc_ts                #(实际传输)/(实际传输+padding)
    RU_effciency_nts = occupy_nts/alloc_nts

    #计算成功接入概率
    SAP = N_accesspon/N_STA_total
    Ps = N_accesswifi/N_STA_total
    if N_TS_total != 0:
        SAP_ts = N_accesswifi_ts/N_TS_total
    else:
        SAP_ts = None
    if N_NTS_total != 0:
        SAP_nts = N_accesswifi_nts/N_NTS_total    
    else:
        SAP_nts = None
    return latency_ts,latency_nts,jitter_ts,jitter_nts,SAP_ts,SAP_nts,Ut_RU_ts,Ut_RU_nts,RU_effciency_ts,RU_effciency_nts

# N_SFU = 4
# N_STA = 30            #假设所有STA都是RTA STA，全参与竞争，指定分配暂不考虑
# CWOmin = [7,7]
# CWOmax = [31,31]
# duration = 1000000
# tTXOP = 2000
# N_TU_total = 170
# gama = [0.1,0.2,0.3,0.4]#[0.2,0.3,0.4,0.6,0.7,0.8]  
# N_RU = 16
# latency_ts,latency_nts,jitter_ts,jitter_nts,SAP_ts,SAP_nts,Ut_RU_ts,Ut_RU_nts,RU_effciency_ts,RU_effciency_nts = transmission(N_SFU,N_STA,gama,N_RU,N_TU_total,CWOmax,CWOmin,duration,tTXOP)
# print('latency_ts=',latency_ts)
# print('latency_nts=',latency_nts)
# print('SAP_ts=',SAP_ts)
# print('SAP_nts=',SAP_nts)
# print('Ut_RU_ts=',Ut_RU_ts)
# print('Ut_RU_nts=',Ut_RU_nts)
# print('RU_effciency_ts=',RU_effciency_ts)
# print('RU_effciency_nts=',RU_effciency_nts) 




    