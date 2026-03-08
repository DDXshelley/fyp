import numpy as np
from scipy import stats
import random
import math
import E_poisson
import UORA_count
import analysis_new
import math
import matplotlib.pyplot as plt

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
    rate_RU = 47.2  #1*26*10*5/6/(12.8+0.8)
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
    N_TU_allocatenum = 0
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
    lam_ts = 400/1000000                  #600         #400
    lam_nts = 200/1000000                              #400

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
        RU_fix[i] = N_BSR_ts[i]

    #判断是否有新到来的数据
    Timer += tBSR + tSIFS + tTF + tSIFS 
    for i in range(N_SFU):
        for j in range (N_STA):
            if Arri[i][j][0] <= Timer:
                tosend[i,j] = 1
                tosend_total[i,j] = 1
                N_STA_total += 1
                if contention_bsr[i,j] == 1:
                    tosend[i,j] = 0                       #找出需要随机接入的STA
                if j in Set_TS_STA[i]:
                    N_TS_total += 1
                else:
                    N_NTS_total += 1
            
    #第二阶段的随机接入过程
    for i in range (N_SFU):
        if sum(tosend[i]) > 0:                                      #有数据要发，则竞争
            RU_random[i] = N_RU - RU_fix[i]
            [contention[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend[i], 1, N_STA, RU_random[i], A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])
        else:
            RU_random[i] = 0
        # N_RU_totalnum += RU_fix[i] + RU_random[i]
        # [_,alphas[i]]=analysis_new.tau(N_contention[i], RU_random[i], CWOmin[1], CWOmax[1])
        # TU_random[i] = int(math.ceil(alphas[i] * RU_random[i]))
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

                #后面的数
                if receive_cycle_num[i,j] > 1:
                    for k in range (1,receive_cycle_num[i,j]):
                        end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k]/ rate_RU

        for j in range (N_STA):
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

                #后面的数
                if receive_cycle_num[i,j] > 1:
                    for k in range (1,receive_cycle_num[i,j]):
                        end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k]/ rate_RU      

    Timer += T 
    # N_STA_total = N_STA_total + sum(sum(tosend_total))
    N_RU_totalnum += N_SFU*N_RU

    #循环=======================================================================================
    while True:
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
        N_contention = np.zeros((N_SFU), dtype=int)

        arri_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]  #%每个周期成功接入的STA传给ONU的数据的到达时间点
        size_data_ap = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]  #每个周期成功接入的STA传给ONU的数据的大小
        arri_data = [[] for _ in range(N_TU_total)]                       #成功传输得到PON的数据到达时间点
        size_data = [[] for _ in range(N_TU_total)]                       #成功传输得到PON的数据包大小
        receive_cycle_num = np.zeros((N_SFU, N_STA), dtype=int)
        N_BSR_ts = np.zeros((N_SFU), dtype=int)
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
            
        
        Timer += tBSR + tSIFS + tTF + tSIFS 
        for i in range(N_SFU):
            for j in range (N_STA):
                if remain_num[i,j] > 0:
                    if buff_A[i][j][0] <= Timer:
                        tosend[i,j] = 1
                        tosend_total[i,j] = 1
                        N_STA_total += 1
                        if contention_bsr[i,j] == 1:
                            tosend[i,j] = 0
                        if j in Set_TS_STA[i]:
                            N_TS_total += 1
                        else:
                            N_NTS_total += 1 

        #第二阶段的随机接入过程
        for i in range (N_SFU):
            if sum(tosend[i]) > 0:
                RU_random[i] = N_RU - RU_fix[i]
                [contention[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend[i], 1, N_STA, RU_random[i], A_CWO[i], A_BO[i], A_Retry[i], CWOmin_list[i], CWOmax_list[i])                         
            else:
                RU_random[i] = 0
            # [_,alphas[i]]=analysis_new.tau(N_contention[i], RU_random[i], CWOmin[1], CWOmax[1])
            # TU_random[i] = int(math.ceil(alphas[i] * RU_random[i]))
            # N_RU_totalnum += RU_fix[i] + RU_random[i]

        # # aa = np.zeros(N_SFU)
        # bb = np.zeros(N_SFU)
        # for i in range (N_SFU):
        #     # aa[i] = sum(tosend[i]) 
        #     bb[i] = sum(contention[i])
        # print('--------------------')
        # print('RU=',RU_random)
        # print('TU_random=',TU_random)        
        # print('succ_random=',bb)

        #无线传输部分
        for i in range (N_SFU):
            for j in range (N_STA):
                if contention_bsr[i,j] == 1:
                    N_accesswifi += 1 
                    N_accesswifi_ts += 1
                    alloc_ts += rate_RU*tTXOP
                    sum_size = 0
                    for k in range (remain_num[i,j]):
                        if buff_A[i][j][k] <= Timer:
                            sum_size = sum_size + buff_S[i][j][k]/rate_RU
                            if sum_size + phy_overhead_wifi <= tPPDU:
                                arri_data_ap[i][j].append(buff_A[i][j][k])
                                size_data_ap[i][j].append(buff_S[i][j][k])
                                occupy_ts += buff_S[i][j][k][0]

                    #计算接收时间
                    #第一个数
                    receive_cycle_num[i,j] = len(arri_data_ap[i][j]) 
                    start_time[i][j][receive_num[i,j]] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                    end_time[i][j][receive_num[i,j]] = start_time[i][j][receive_num[i,j]] + size_data_ap[i][j][0]/ rate_RU

                    #后面的数
                    if receive_cycle_num[i,j] > 1:
                        for k in range ((receive_num[i,j]+1),(receive_num[i,j]+receive_cycle_num[i,j])):
                            end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k-receive_num[i,j]]/ rate_RU                                                                     
                    
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

                    #计算接收时间
                    #第一个数
                    receive_cycle_num[i,j] = len(arri_data_ap[i][j]) 
                    start_time[i][j][receive_num[i,j]] = Timer + phy_overhead_wifi + tTrans_w * 1 + tTrans_p * 1 + tProcess
                    end_time[i][j][receive_num[i,j]] = start_time[i][j][receive_num[i,j]] + size_data_ap[i][j][0]/ rate_RU

                    #后面的数
                    if receive_cycle_num[i,j] > 1:
                        for k in range ((receive_num[i,j]+1),(receive_num[i,j]+receive_cycle_num[i,j])):
                            end_time[i][j][k] = end_time[i][j][k-1] + size_data_ap[i][j][k-receive_num[i,j]]/ rate_RU                                                                  
                    
                    receive_num[i,j] = receive_num[i,j] + receive_cycle_num[i,j]
                    if pack_num[i,j] == receive_num[i,j]:
                        buff_A[i][j] = []
                        buff_S[i][j] = []
                        remain_num[i,j] = 0
                    elif pack_num[i,j] > receive_num[i,j]:
                        buff_A[i][j] = buff_A[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        buff_S[i][j] = buff_S[i][j][-(pack_num[i,j]-receive_num[i,j]):]
                        remain_num[i,j] = len(buff_A[i][j])


        
        Timer += T
        # N_STA_total = N_STA_total + sum(sum(tosend_total)) 
        N_RU_totalnum = N_RU_totalnum + N_RU*N_SFU
     

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
                if k >0:
                    jitter[i][j][k-1] = abs((end_time[i][j][k] - Arri[i][j][k])-(end_time[i][j][k-1] - Arri[i][j][k-1]))                
            latency[i][j] = sorted(latency[i][j]) 
            jitter[i][j] = sorted(jitter[i][j]) 
            for k in range ((math.ceil(pack_num[i,j]*0.05)),(pack_num[i,j]-math.ceil(pack_num[i,j]*0.05))):
                latency1[i][j].append(latency[i][j][k])
                jitter1[i][j].append(jitter[i][j][k])

            
            mean_latency[i,j] = np.mean(latency1[i][j])
            # mean_jitter[i][j] = np.std(latency1[i][j]) 
            mean_jitter[i][j] = np.mean(jitter1[i][j])  

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
    Ut_RU_ts = (N_accesswifi_ts+N_accesswifi_nts)/N_RU_totalnum
    Ut_RU_nts = N_accesswifi_nts/N_RU_totalnum
    RU_effciency_ts = occupy_ts/alloc_ts                #(实际传输)/(实际传输+padding)
    RU_effciency_nts = occupy_nts/alloc_nts

    #计算成功接入概率
    Ps = N_accesswifi/N_STA_total
    if N_TS_total != 0:
        Ps_ts = N_accesswifi_ts/N_TS_total
    else:
        Ps_ts = None
    if N_NTS_total != 0:
        Ps_nts = N_accesswifi_nts/N_NTS_total   
    else:
        Ps_nts = None
    return latency_ts,latency_nts,jitter_ts,jitter_nts,Ps_ts,Ps_nts,Ut_RU_ts,Ut_RU_nts,RU_effciency_ts,RU_effciency_nts


# N_SFU = 1
# N_STA = 20            #假设所有STA都是RTA STA，全参与竞争，指定分配暂不考虑
# CWOmin = [7,7]
# CWOmax = [63,63]
# duration = 1000000
# tTXOP = 3000
# N_TU_total = 170
# gama = [0.3]#[0.2,0.3,0.4,0.6,0.7,0.8]  
# N_RU = 16
# latency_ts,latency_nts,jitter_ts,jitter_nts,Ut_RU,Ut_RU_ts,Ut_RU_nts,Ps,Ps_ts,Ps_nts = transmission(N_SFU,N_STA,gama,N_RU,N_TU_total,CWOmax,CWOmin,duration,tTXOP)
# print('latency_ts=',latency_ts)
# print('latency_nts=',latency_nts)
# print('Ut_RU=',Ut_RU)              
# print('Ut_RU_ts=',Ut_RU_ts)
# print('Ut_RU_nts=',Ut_RU_nts)  
# print('Ps=',Ps)  
# print('Ps_ts=',Ps_ts)
# print('Ps_nts=',Ps_nts)  

# N_SFU = 6
# N_STA_Array = np.arange(3,33,3)            #假设所有STA都是RTA STA，全参与竞争，指定分配暂不考虑
# CWOmin = [7,7]
# CWOmax = [31,31]
# duration = 1000000
# tTXOP = 1000
# N_TU_total = 342
# gama = [0,0.2,0.4,0.6,0.8,1]    #[0,0.2,0.4,0.6,0.8,1]   
# N_RU = 16
# Ut_RU = np.zeros(len(N_STA_Array))
# Ut_TU = np.zeros(len(N_STA_Array))
# a = np.zeros(len(N_STA_Array))
# latency_ts = np.zeros(len(N_STA_Array))
# latency_nts = np.zeros(len(N_STA_Array))
# Ps = np.zeros(len(N_STA_Array))
# Ps_ts = np.zeros(len(N_STA_Array))
# Ps_nts = np.zeros(len(N_STA_Array))
# Ut_RU_ts = np.zeros(len(N_STA_Array))
# Ut_RU_nts = np.zeros(len(N_STA_Array))
# for i in range (len(N_STA_Array)):
#     latency_ts[i],latency_nts[i],_,_,Ut_RU[i],Ut_TU[i],_,Ps[i],Ps_ts[i],Ps_nts[i],_,_,Ut_RU_ts[i],Ut_RU_nts[i] = transmission(N_SFU,N_STA_Array[i],gama,N_RU,N_TU_total,CWOmax,CWOmin,duration,tTXOP)

# # plt.figure(1)
# # plt.subplot(121)
# # plt.plot(N_STA_Array,latency_ts)  
# # plt.xlabel('Number of STAs per SFU')
# # plt.ylabel('Latency-TS')
# # plt.xlim(0,30)
# # plt.grid(True)

# # plt.subplot(122)
# # plt.plot(N_STA_Array,latency_nts)  
# # plt.xlabel('Number of STAs per SFU')
# # plt.ylabel('Latency-NTS')
# # plt.xlim(0,30)
# # plt.grid(True)
# # plt.show()

# #第二个图
# plt.figure(1)
# plt.subplot(131)
# plt.plot(N_STA_Array,Ut_RU)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('Wireless Resource utilization(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)

# plt.subplot(132)
# plt.plot(N_STA_Array,Ut_RU_ts)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('Wireless Resource utilization of TS(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)

# plt.subplot(133)
# plt.plot(N_STA_Array,Ut_RU_nts)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('Wireless Resource utilization of NTS(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)
# plt.show()

# plt.figure(2)
# plt.subplot(131)
# plt.plot(N_STA_Array,Ps)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('Ps of Wi-Fi side(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)

# plt.subplot(132)
# plt.plot(N_STA_Array,Ps_ts)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('SAP of TS service in Wi-Fi side(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)

# plt.subplot(133)
# plt.plot(N_STA_Array,Ps_nts)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('SAP of NTS service in Wi-Fi side(100%)')
# plt.xlim(0,30)
# plt.ylim(0,1)
# plt.grid(True)
# plt.show()

                    



    