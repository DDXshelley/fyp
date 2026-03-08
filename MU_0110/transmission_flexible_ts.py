import numpy as np
import random
import math
import matplotlib.pyplot as plt
import E_poisson
import EDCA_count
import UORA_count
import allocation_algorithm

# N_SFU = 4
# N_STA = 30
# duration = 1000000
# N_RU = 64
# gama = [0.1,0.2,0.3,0.4]  #房间内TS业务的比
#可根据需求和PON系统容量确定采用多大信道
#可分配不同size的光与无线子载波
#传输持续时间动态取整数个slot

#专利方案

def transmission_ul_flexible(N_SFU,N_STA,N_RU,duration,gama):
    # 固定参数
    SIFS = 16
    DIFS = 34
    TF = 224+40*9          #bit
    AIFSN = [7,7]      #[7,3,2,2]               0是TS的参数，1是NTS的参数
    CWmin = [31,31]     #[31,31,15,7]
    CWmax = [1023,1023]    #[1023,1023,31,15]
    AIFSN_sfu = 2
    CWmin_sfu = 7
    CWmax_sfu = 15
    tProcess = 100     #us
    tTrans_w = 1       #us
    tTrans_o = 5/200
    ACK= 432           #bits
    BSRP = 224+40*9       #????????????????????????
    BSR = 224+40*9        #????????????????????????
    MPDU = 11454       #bytes  maximum
    PPDU_su = (40+14+3+MPDU)*8      #bits  maximum
    overhead = (40 + 14 + 3) * 8    #bits  maximum
    rate_suboptical = 9.76          #一条光子载波的速率     bits/us
    num_suboptical_total = 1024                         #光子载波总个数
    set_UL_DURATION_o = 1800
    set_UL_DURATION_w = 3000
    duration_wirelesssub_tf = np.zeros(N_SFU)
    duration_optical_tf = np.zeros(N_SFU)
    num_opticalsub_tf = 5
    num_opticalsub_sfu = np.zeros(N_SFU)
    num_opticalsub_sta = np.zeros((N_SFU,N_STA))
    duration_opticalsub = np.zeros(N_SFU)
    size_RU = np.zeros((N_SFU,N_STA))
    rate_RU_dl = np.zeros((N_SFU,N_STA))
    rate_RU_ul = np.zeros((N_SFU,N_STA))
    sub_RU_ul = np.zeros((N_SFU,N_STA))
    rate_sub_dl = np.zeros((N_SFU,N_STA))
    rate_oru_ul = np.zeros((N_SFU,N_STA))
    size_RU_list = [1,2,4,8,16,32]                #分别是多少个26-tone
    rate_RU_list = [11.1,22.2,47.2,135.4,270.8,576.1]
    rate_sub_list = [19.4,29.1,58.2,145.5,281.3,582]
    ACK_time = SIFS + ACK/rate_RU_list[0] + tProcess + ACK/(2*rate_suboptical)
    ul_duration_max_o = np.zeros(N_SFU)
    ul_duration_max_w = np.zeros(N_SFU)
    Total_allocated = 0
    Total_allocated_ts = 0
    Total_allocated_nts = 0
    Total_utilized = 0
    Total_utilized_ts = 0
    Total_utilized_nts = 0
    req_capacity_ts = np.zeros(N_SFU)
    req_period = np.zeros(N_SFU)

    CWOmin = int(2**1-1)
    CWOmax = int(2**5-1)
    A_CWO = np.ones((N_SFU, N_STA))*CWOmin
    A_BO = np.zeros((N_SFU, N_STA))
    A_Retry = np.zeros((N_SFU, N_STA))
    A1 = np.zeros((N_SFU, N_STA))
    A2 = np.zeros((N_SFU, N_STA))

    # 初始化参数-上行
    Arri_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    Size_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    buff_A_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    buff_S_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    start_time_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    end_time_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    latency_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    arri_data_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    size_data_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    buff_A_SFU_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    buff_S_SFU_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
    arri_SFU_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]

    pack_num_UL = np.zeros((N_SFU, N_STA), dtype=int)
    remain_num_UL = np.zeros((N_SFU, N_STA), dtype=int)
    receive_num_UL = np.zeros((N_SFU, N_STA), dtype=int)
    receive_cycle_num_UL = np.zeros((N_SFU, N_STA), dtype=int)
    mean_latency_UL = np.zeros((N_SFU, N_STA))
    mean_jitter_UL = np.zeros((N_SFU, N_STA))


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
    lam_UL_ts = 600/1000000
    lam_UL_nts = 200/1000000

    # 给每个STA产生UL数据包
    for i in range(N_SFU):
        for j in range(N_STA):
            if j in Set_TS_STA[i]:
            # 给每个STA产生数据包
                [arri, size] = E_poisson.poisson(lam_UL_ts, duration,1)
                Arri_UL[i][j] = arri
                Size_UL[i][j] = size
                buff_A_UL[i][j] = arri
                buff_S_UL[i][j] = size
                pack_num_UL[i,j] = len(arri)
                remain_num_UL[i,j] = len(arri)  
            elif j in Set_NTS_STA[i]:
                [arri, size] = E_poisson.poisson(lam_UL_nts, duration,2)
                Arri_UL[i][j] = arri
                Size_UL[i][j] = size
                buff_A_UL[i][j] = arri
                buff_S_UL[i][j] = size
                pack_num_UL[i,j] = len(arri)  
                remain_num_UL[i,j] = len(arri)            

            # 初始化 receive_time 和 latency 数组
            start_time_UL[i][j] = np.zeros(pack_num_UL[i,j])
            end_time_UL[i][j] = np.zeros(pack_num_UL[i,j])
            latency_UL[i][j] = np.zeros(pack_num_UL[i,j])
            arri_SFU_UL[i][j] = np.zeros(pack_num_UL[i,j])

    T_fixed = (BSRP+BSR+TF+ACK)/(rate_RU_list[0]*9)+(BSRP+BSR+TF+ACK)/(9*2*rate_suboptical)+tProcess+SIFS*5      #214

    ##第一个周期
    tosend_UL = np.zeros((N_SFU,N_STA), dtype=int)
    tosend_ts1 = np.zeros((N_SFU,N_STA), dtype=int)
    tosend_2 = np.zeros((N_SFU,N_STA), dtype=int)
    buffer_size_ts = np.zeros((N_SFU,N_STA))
    buffer_size_con = np.zeros((N_SFU,N_STA))     #第二轮参加竞争的buffer
    request_duration_o = np.zeros((N_SFU,N_STA))
    request_duration_w = np.zeros((N_SFU,N_STA))

    #进行Trigger触发的MU UL
    #同步发送trigger帧
    #判断剩余时间是否足够传
    Timer = 1000*np.ones(N_SFU)
    time_remain = np.zeros(N_SFU)
    for i in range (N_SFU):
        for j in range (N_STA):
            if remain_num_UL[i,j] > 0:
                if buff_A_UL[i][j][0] <= Timer[i]:
                    tosend_UL[i,j] = 1
                    if j in Set_TS_STA[i]:
                        tosend_ts1[i,j] = 1

        #通过UORA传输BSR
        if sum(tosend_ts1[i])>0:
            [A1[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts1[i], N_STA, 32,A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax)    #第一阶段的TS的BSR报告

    # print(Arri_UL)
    # print('TS请求',tosend_ts1)
    # print('TS竞争成功',A1)

    #获取buffer的大小
    for i in range (N_SFU):
        # Timer[i] += BSRP/(rate_RU_list[0]*9) + BSRP/(9*2*rate_suboptical) + SIFS
        for j in range (N_STA):
            if j in Set_TS_STA[i]:
                if ((remain_num_UL[i,j] > 0)and(A1[i,j]==1)):
                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:
                            buffer_size_ts[i,j] += buff_S_UL[i][j][k]
                    req_capacity_ts[i] += buffer_size_ts[i,j]*1.07

    # print('TS请求容量',req_capacity_ts)
    #根据需求确定需要多大信道----这里仅是知道TS STA需要多大信道，对应需要多少26-tone RU
    T_last = 1000*np.ones(N_SFU)
    N_RU_ts = find_BW(req_capacity_ts,T_last)
    # print('TS RU总数',N_RU_ts)

    #分配光与无线资源 - 灵活分配大小-TS STAs
    # for i in range (N_SFU):
    #     if req_capacity_ts[i]>0:
    #         sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
    #         for j in range (N_STA):
    #             if buffer_size_ts[i,j] > 0:
    #                 rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)        #？？？？？？？？？？？？？？假设光资源完全足够，后续修改
    #                 request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
    #                 request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] +overhead/rate_oru_ul[i,j]
    #         ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
    #         ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
    #         req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
    # time_max = max(req_period)


    if sum(req_capacity_ts) == 0:      #所有房间都没有TS STAs有数据要传了
        for i in range (N_SFU):
            ul_duration_max_o[i] = set_UL_DURATION_o
            ul_duration_max_w[i] = set_UL_DURATION_w
            req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed

    else:                              #有房间有汇报的TS STAs有数据要传 
        for i in range (N_SFU):
            if req_capacity_ts[i]>0:
                sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
                for j in range (N_STA):
                    if buffer_size_ts[i,j] > 0:
                        rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)        #？？？？？？？？？？？？？？假设光资源完全足够，后续修改
                        request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
                        request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] +overhead/rate_oru_ul[i,j]
                ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
                ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
                req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
        req_ts_max_o = max(ul_duration_max_o)
        req_ts_max_w = max(ul_duration_max_w)
        for i in range (N_SFU):
            if req_capacity_ts[i]==0:    
                ul_duration_max_o[i] = req_ts_max_o        #全部随机竞争的时间长度
                ul_duration_max_w[i] = req_ts_max_w
                req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
    time_max = max(req_period)    
                

    # print('请求时间',req_period)
    # print('同步时间',time_max)

    #分配固定大小的RU用于随机接入
    N_RU_random = np.zeros(N_SFU,dtype=int)
    for i in range (N_SFU):
        N_RU_random[i] = int(math.floor((N_RU - N_RU_ts[i])/2))            #剩余用于竞争的26-tone RU个数

    #第二轮随机接入
    for i in range (N_SFU):
        for j in range (N_STA):
            if ((remain_num_UL[i,j] > 0)and (A1[i,j]!=1)):
                for k in range (remain_num_UL[i,j]):
                    if buff_A_UL[i][j][k] <= Timer[i]:
                        buffer_size_con[i,j] += buff_S_UL[i][j][k]
                if buffer_size_con[i,j] != 0:
                    tosend_2[i,j] = 1
        #通过UORA传输BSR
        if (sum(tosend_2[i])>0 and (N_RU_random[i] > 0)):
            [A2[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_2[i], N_STA, N_RU_random[i],A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax) 
        
    #数据传输
    for i in range (N_SFU):
        #进行一轮传输
        time_remain[i] = time_max - req_period[i]
        for j in range (N_STA):
            #固定的TS部分       
            if buffer_size_ts[i,j]>0 and A1[i,j] !=0:
                sum_size1 = overhead/rate_RU_ul[i,j]
                sum_size2 = overhead/rate_oru_ul[i,j]

                #计算资源利用率-无线                     实际传输/(实际传输+padding)比例
                Total_allocated += ul_duration_max_w[i]*rate_RU_ul[i,j]
                Total_allocated_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]
                if buffer_size_ts[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_ul[i,j]:
                    Total_utilized += buffer_size_ts[i,j]*1.07
                    Total_utilized_ts += buffer_size_ts[i,j]*1.07
                else:
                    Total_utilized += ul_duration_max_w[i]*rate_RU_ul[i,j]
                    Total_utilized_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]

                for k in range (remain_num_UL[i,j]): 
                    if (buff_A_UL[i][j][k] <= Timer[i]):
                        sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_ul[i,j]
                        if sum_size1 <= ul_duration_max_w[i]:
                            buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                            buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                            sum_size2 += buff_S_UL[i][j][k]/rate_oru_ul[i,j]
                            if sum_size2 < ul_duration_max_o[i]:
                                arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                size_data_UL[i][j].append(buff_S_UL[i][j][k])
                receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                #计算接收时间
                #第一个数据包
                if receive_cycle_num_UL[i,j]>0:
                    end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] +TF/(rate_RU_list[0]*9) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_oru_ul[i,j]
                    if receive_cycle_num_UL[i,j] > 1:
                        for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                            end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_oru_ul[i,j]
                    receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                    if pack_num_UL[i,j] == receive_num_UL[i,j]:
                        buff_A_UL[i][j] = []
                        buff_S_UL[i][j] = []
                        remain_num_UL[i,j] = 0
                    elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                        buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                        buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                        remain_num_UL[i,j] = len(buff_A_UL[i][j])    

            #随机竞争的部分
            if ((buffer_size_con[i,j] > 0) and (A2[i,j] != 0)):  
                a = 1              
                sum_size1 = overhead/rate_RU_list[a]
                sum_size2 = overhead/rate_sub_list[a]
                # Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]
                # if buffer_size_con[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]:
                #     Total_utilized += buffer_size_con[i,j]*1.07
                # else:
                #     Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]

                Total_allocated += ul_duration_max_w[i]*rate_RU_list[a]
                if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                    Total_utilized += buffer_size_con[i,j]*1.07
                else:
                    Total_utilized += ul_duration_max_w[i]*rate_RU_list[a]
                if j in Set_TS_STA[i]:
                    Total_allocated_ts += ul_duration_max_w[i]*rate_RU_list[a]
                    if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                        Total_utilized_ts += buffer_size_con[i,j]*1.07
                    else:
                        Total_utilized_ts += ul_duration_max_w[i]*rate_RU_list[a]
                else:
                    Total_allocated_nts += ul_duration_max_w[i]*rate_RU_list[a]
                    if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                        Total_utilized_nts += buffer_size_con[i,j]*1.07
                    else:
                        Total_utilized_nts += ul_duration_max_w[i]*rate_RU_list[a]

                for k in range (remain_num_UL[i,j]): 
                    if (buff_A_UL[i][j][k] <= Timer[i]):
                        sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_list[a]
                        if sum_size1 <= ul_duration_max_w[i]:
                            buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                            buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                            sum_size2 += buff_S_UL[i][j][k]/rate_sub_list[a]
                            if sum_size2 < ul_duration_max_o[i]:
                                arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                size_data_UL[i][j].append(buff_S_UL[i][j][k])
                receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                #计算接收时间
                #第一个数据包
                if receive_cycle_num_UL[i,j]>0:
                    end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] +TF/(rate_RU_list[0]*8) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_sub_list[a]
                    if receive_cycle_num_UL[i,j] > 1:
                        for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                            end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_sub_list[a]
                    receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                    if pack_num_UL[i,j] == receive_num_UL[i,j]:
                        buff_A_UL[i][j] = []
                        buff_S_UL[i][j] = []
                        remain_num_UL[i,j] = 0
                    elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                        buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                        buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                        remain_num_UL[i,j] = len(buff_A_UL[i][j])                    

        if sum(receive_cycle_num_UL[i]) > 0:
            Timer[i] += ul_duration_max_w[i]+ul_duration_max_o[i] + T_fixed   #+ (TF+BSRP+ACK)/(rate_RU_list[0]*9) + tProcess + (TF+BSRP+ACK)/(9*2*rate_suboptical) + SIFS
        else:
            Timer[i] += DIFS + tTrans_o + tTrans_w #+ BSRP/(rate_RU_list[0]*9)  + BSRP/(9*2*rate_suboptical) + SIFS

    # # print('剩余',time_remain)
    # print('时间轴',Timer)

    for i in range (N_SFU):
        #计算是否需要多轮传输
        while(time_remain[i]>0):
            tosend_UL[i] = 0
            tosend_ts1 = np.zeros((N_SFU,N_STA), dtype=int)
            tosend_2 = np.zeros((N_SFU,N_STA), dtype=int)        
            buffer_size_ts[i] = 0
            buffer_size_con[i] = 0
            req_capacity_ts[i] = 0
            request_duration_w[i] = 0
            request_duration_o[i] = 0
            ul_duration_max_o[i] = 0
            ul_duration_max_w[i] = 0
            req_period[i] = 0
            A1 = np.zeros((N_SFU, N_STA))
            A2 = np.zeros((N_SFU, N_STA))
            N_RU_random = np.zeros(N_SFU,dtype=int)

            for j in range (N_STA):
                if remain_num_UL[i,j] > 0:
                    if buff_A_UL[i][j][0] <= Timer[i]:
                        tosend_UL[i,j] = 1
                        if j in Set_TS_STA[i]:
                            tosend_ts1[i,j] = 1

            #通过UORA传输BSR
            if sum(tosend_ts1[i])>0:
                [A1[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts1[i], N_STA, 32,A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax)
        
            #获取buffer的大小
            # Timer[i] += BSRP/(rate_RU_list[0]*9) + BSRP/(9*2*rate_suboptical) + SIFS
            for j in range (N_STA):
                if j in Set_TS_STA[i]:
                    if ((remain_num_UL[i,j] > 0)and(A1[i,j]==1)):
                        for k in range (remain_num_UL[i,j]):
                            if buff_A_UL[i][j][k] <= Timer[i]:
                                buffer_size_ts[i,j] += buff_S_UL[i][j][k] 
                        req_capacity_ts[i] += buffer_size_ts[i,j]*1.07
            
            if req_capacity_ts[i]>0:     #新一轮有固定TS数据来
                sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
                for j in range (N_STA):
                    if buffer_size_ts[i,j] > 0:
                        rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)        #？？？？？？？？？？？？？？假设光资源完全足够，后续修改
                        request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
                        request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] + overhead/rate_oru_ul[i,j]
                ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
                ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
                req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed

                if (req_period[i]<time_remain[i]):                #仍有空余时间
                    time_remain[i] = time_remain[i] - req_period[i]
                    

                elif (req_period[i]>=time_remain[i]):              #没有空闲时间
                    if time_remain[i]>T_fixed:
                        ul_duration_max_w[i] = min((time_remain[i]-T_fixed)*1/1.57,set_UL_DURATION_w)
                        ul_duration_max_o[i] = min((time_remain[i]-T_fixed)*0.57/1.57,set_UL_DURATION_o)
                        req_period[i] = time_remain[i]
                        time_remain[i] = 0
                    else:
                        ul_duration_max_w[i] = 0
                        ul_duration_max_o[i] = 0
                        time_remain[i] = 0
            else:                       #新一轮没有固定TS数据来
                ul_duration_max_o[i] = set_UL_DURATION_o
                ul_duration_max_w[i] = set_UL_DURATION_w
                req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
                if (req_period[i]<time_remain[i]):                #仍有空余时间
                    time_remain[i] = time_remain[i] - req_period[i]
                    
                elif (req_period[i]>=time_remain[i]):              #没有空闲时间
                    if time_remain[i]>T_fixed:
                        ul_duration_max_w[i] = min((time_remain[i]-T_fixed)*1/1.57,set_UL_DURATION_w)
                        ul_duration_max_o[i] = min((time_remain[i]-T_fixed)*0.57/1.57,set_UL_DURATION_o)
                        req_period[i] = time_remain[i]
                        time_remain[i] = 0
                    else:
                        ul_duration_max_w[i] = 0
                        ul_duration_max_o[i] = 0
                        time_remain[i] = 0            

            #分配固定大小的RU用于随机接入
            N_RU_random[i] = int(math.floor((N_RU - N_RU_ts[i])/2))

            #第二轮随机接入
            for j in range (N_STA):
                if ((remain_num_UL[i,j] > 0)and (A1[i,j]!=1)):
                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:
                            buffer_size_con[i,j] += buff_S_UL[i][j][k]
                    if buffer_size_con[i,j] != 0:
                        tosend_2[i,j] = 1
            #通过UORA传输BSR
            if (sum(tosend_2[i])>0 and (N_RU_random[i] > 0)):
                [A2[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_2[i], N_STA, N_RU_random[i],A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax) 

            #传输过程
            for j in range (N_STA):
                #固定部分
                if buffer_size_ts[i,j]>0 and A1[i,j] !=0:
                    sum_size1 = overhead/rate_RU_ul[i,j]
                    sum_size2 = overhead/rate_oru_ul[i,j]
                    # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):
                    #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]
                    #     if buffer_size_ts[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]:
                    #         Total_utilized += buffer_size_ts[i,j]*1.07
                    #     else:
                    #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]

                    Total_allocated += ul_duration_max_w[i]*rate_RU_ul[i,j]
                    Total_allocated_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]
                    if buffer_size_ts[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_ul[i,j]:
                        Total_utilized += buffer_size_ts[i,j]*1.07
                        Total_utilized_ts += buffer_size_ts[i,j]*1.07
                    else:
                        Total_utilized += ul_duration_max_w[i]*rate_RU_ul[i,j]
                        Total_utilized_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]

                    for k in range (remain_num_UL[i,j]): 
                        if (buff_A_UL[i][j][k] <= Timer[i]):
                            sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_ul[i,j]
                            if sum_size1 <= ul_duration_max_w[i]:
                                buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                sum_size2 += buff_S_UL[i][j][k]/rate_oru_ul[i,j]
                                if sum_size2 < ul_duration_max_o[i]:
                                    arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                    size_data_UL[i][j].append(buff_S_UL[i][j][k])
                    receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                    #计算接收时间
                    #第一个数据包
                    if receive_cycle_num_UL[i,j]>0:
                        end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] +TF/(rate_RU_list[0]*9) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_oru_ul[i,j]
                        if receive_cycle_num_UL[i,j] > 1:
                            for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_oru_ul[i,j]

                        receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                        if pack_num_UL[i,j] == receive_num_UL[i,j]:
                            buff_A_UL[i][j] = []
                            buff_S_UL[i][j] = []
                            remain_num_UL[i,j] = 0
                        elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                            buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                            buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                            remain_num_UL[i,j] = len(buff_A_UL[i][j])        

                #random部分
                if ((buffer_size_con[i,j] > 0) and (A2[i,j] != 0)):                #NTS
                    a = 1
                    sum_size1 = overhead/rate_RU_list[a]
                    sum_size2 = overhead/rate_sub_list[a]
                    # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):
                    #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]
                    #     if buffer_size_con[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]:
                    #         Total_utilized += buffer_size_con[i,j]*1.07
                    #     else:
                    #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]

                    Total_allocated += ul_duration_max_w[i]*rate_RU_list[a]
                    if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                        Total_utilized += buffer_size_con[i,j]*1.07
                    else:
                        Total_utilized += ul_duration_max_w[i]*rate_RU_list[a]
                    
                    if j in Set_TS_STA[i]:
                        Total_allocated_ts += ul_duration_max_w[i]*rate_RU_list[a]
                        if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                            Total_utilized_ts += buffer_size_con[i,j]*1.07
                        else:
                            Total_utilized_ts += ul_duration_max_w[i]*rate_RU_list[a] 
                    else:
                        Total_allocated_nts += ul_duration_max_w[i]*rate_RU_list[a]
                        if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                            Total_utilized_nts += buffer_size_con[i,j]*1.07
                        else:
                            Total_utilized_nts += ul_duration_max_w[i]*rate_RU_list[a]                                               

                    for k in range (remain_num_UL[i,j]): 
                        if (buff_A_UL[i][j][k] <= Timer[i]):
                            sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_list[a]
                            if sum_size1 <= ul_duration_max_w[i]:
                                buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                sum_size2 += buff_S_UL[i][j][k]/rate_sub_list[a]
                                if sum_size2 < ul_duration_max_o[i]:
                                    arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                    size_data_UL[i][j].append(buff_S_UL[i][j][k])
                    receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                    #计算接收时间
                    #第一个数据包
                    if receive_cycle_num_UL[i,j]>0:
                        end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] +TF/(rate_RU_list[0]*8) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_sub_list[a]
                        if receive_cycle_num_UL[i,j] > 1:
                            for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_sub_list[a]
                        receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                        if pack_num_UL[i,j] == receive_num_UL[i,j]:
                            buff_A_UL[i][j] = []
                            buff_S_UL[i][j] = []
                            remain_num_UL[i,j] = 0
                        elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                            buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                            buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                            remain_num_UL[i,j] = len(buff_A_UL[i][j])                       


            if sum(receive_cycle_num_UL[i]) > 0:
                Timer[i] += ul_duration_max_w[i]+ul_duration_max_o[i] + T_fixed  #SIFS + (TF+BSRP+ACK)/(rate_RU_list[0]*9) + tProcess + (TF+BSRP+ACK)/(9*2*rate_suboptical) + SIFS

            else:
                Timer[i] += DIFS + tTrans_o + tTrans_w + T_fixed #BSRP/(rate_RU_list[0]*9)  + BSRP/(9*2*rate_suboptical) + SIFS

    # print('Timer',Timer)                                
    while True:
    # for ss in range (100):
        flag = [[] for _ in range(N_SFU)]
        Set_success = [[] for _ in range(N_SFU)]
        timer = np.zeros(N_SFU)
        tosend_size_dl = np.zeros((N_SFU,N_STA))
        tosend_DL = np.zeros((N_SFU,N_STA), dtype=int)
        receive_cycle_num_DL = np.zeros((N_SFU, N_STA), dtype=int)
        receive_cycle_num_UL = np.zeros((N_SFU, N_STA), dtype=int)
        buff_A_SFU_DL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        buff_S_SFU_DL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)] 
        num_buff_sfu = np.zeros((N_SFU,N_STA), dtype=int)
        tosend_UL = np.zeros((N_SFU,N_STA), dtype=int)
        buff_A_SFU_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        buff_S_SFU_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        arri_data_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        size_data_UL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        arri_data_DL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]
        size_data_DL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)] 
        arri_SFU_DL = [[[] for _ in range(N_STA)] for _ in range(N_SFU)]   
        num_opticalsub_sta = np.zeros((N_SFU,N_STA))
        duration_opticalsub = np.zeros(N_SFU)
        size_RU = np.zeros((N_SFU,N_STA))
        duration_wirelesssub = np.zeros(N_SFU)   
        request_duration_o = np.zeros((N_SFU,N_STA))
        request_duration_w = np.zeros((N_SFU,N_STA)) 
        duration_opticalsub_tf = np.zeros(N_SFU)
        duration_wirelesssub_tf = np.zeros(N_SFU)
        num_opticalsub_tf = 5
        tosend_dl = np.zeros(N_SFU)
        dl_duration_request = np.zeros(N_SFU)
        dl_duration_request1 = np.zeros(N_SFU)
        dl_duration_max = np.zeros(N_SFU)
        uplink_duration = np.zeros(N_SFU)   
        rate_sub_dl = np.zeros((N_SFU,N_STA)) 
        rate_RU_dl = np.zeros((N_SFU,N_STA)) 
        A = np.zeros((N_SFU, N_STA)) 
        rate_RU_ul = np.zeros((N_SFU,N_STA))
        rate_oru_ul = np.zeros((N_SFU,N_STA))
        sub_RU_ul = np.zeros((N_SFU,N_STA))
        ul_duration_max_o = np.zeros(N_SFU)
        ul_duration_max_w = np.zeros(N_SFU)
        req_capacity = np.zeros(N_SFU)
        req_period = np.zeros(N_SFU)
        time_remain = np.zeros(N_SFU)
        tosend_ts1 = np.zeros((N_SFU,N_STA), dtype=int)
        tosend_2 = np.zeros((N_SFU,N_STA), dtype=int)
        buffer_size_ts = np.zeros((N_SFU,N_STA))
        buffer_size_con = np.zeros((N_SFU,N_STA))     #第二轮参加竞争的buffer
        A1 = np.zeros((N_SFU, N_STA))
        A2 = np.zeros((N_SFU, N_STA))
        req_capacity_ts = np.zeros(N_SFU)

        # print('--------------')
        #通过UORA传输BSR
        for i in range (N_SFU):
            for j in range (N_STA):
                if remain_num_UL[i,j] > 0:
                    if buff_A_UL[i][j][0] <= Timer[i]:
                        tosend_UL[i,j] = 1
                        if j in Set_TS_STA[i]:
                            tosend_ts1[i,j] = 1
            
            if sum(tosend_ts1[i])>0:
                [A1[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts1[i], N_STA, 36,A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax)
            
        #获取buffer的大小
        for i in range (N_SFU):
            for j in range (N_STA):
                if ((remain_num_UL[i,j] > 0)and(A1[i,j]==1)):
                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:
                            buffer_size_ts[i,j] += buff_S_UL[i][j][k] 
                    req_capacity_ts[i] += buffer_size_ts[i,j]*1.07

        #根据需求确定需要多大信道
        
        N_RU_ts = find_BW(req_capacity_ts,req_period)
        for i in range (N_SFU):
            if N_RU_ts[i] == N_RU:
                N_RU_ts[i] -= 16
        # print('request',buffer_size_ts)
        # print('TS_RU',N_RU_ts)
        
    #     #分配光与无线资源 - 灵活分配大小
    #     print(req_capacity_ts)
    #     for i in range (N_SFU):
    #         if sum(buffer_size_ts[i]) > 0:
    #             print(i)
    #             sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
    #             for j in range (N_STA):
    #                 if buffer_size_ts[i,j] > 0:
    #                     rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)
    #                     request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
    #                     request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] + overhead/rate_oru_ul[i,j] 
    #             ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
    #             ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
    #             # req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
    #         else:
    #             ul_duration_max_o[i] = set_UL_DURATION_o
    #             ul_duration_max_w[i] = set_UL_DURATION_w
    #         #     req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
        
    #         req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed  
    #     time_max = max(req_period)
        # print(req_capacity_ts)
        if sum(req_capacity_ts) == 0:      #所有房间都没有TS STAs有数据要传了
            for i in range (N_SFU):
                ul_duration_max_o[i] = set_UL_DURATION_o
                ul_duration_max_w[i] = set_UL_DURATION_w
                req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed

        else:                              #有房间有汇报的TS STAs有数据要传 
            for i in range (N_SFU):
                if req_capacity_ts[i]>0:
                    sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
                    for j in range (N_STA):
                        if buffer_size_ts[i,j] > 0:
                            rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)        #？？？？？？？？？？？？？？假设光资源完全足够，后续修改
                            request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
                            request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] +overhead/rate_oru_ul[i,j]
                    ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
                    ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
                    req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
            req_ts_max_o = max(ul_duration_max_o)
            req_ts_max_w = max(ul_duration_max_w)
            for i in range (N_SFU):
                if req_capacity_ts[i]==0:    
                    ul_duration_max_o[i] = req_ts_max_o        #全部随机竞争的时间长度
                    ul_duration_max_w[i] = req_ts_max_w
                    req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
        time_max = max(req_period)  

        

        #分配固定大小的RU用于随机接入
        N_RU_random = np.zeros(N_SFU,dtype=int)
        for i in range (N_SFU):
            N_RU_random[i] = int(math.floor((N_RU - N_RU_ts[i])/2))
        
        
    #     # print(req_capacity_ts)
    #     # print('RU_ts=',N_RU_ts,'RU_random=',N_RU_random)
    #     # print(time_max)

        #第二轮随机接入
        for i in range (N_SFU):
            for j in range (N_STA):
                if ((remain_num_UL[i,j] > 0)and (A1[i,j]!=1)):
                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:
                            buffer_size_con[i,j] += buff_S_UL[i][j][k]
                    if buffer_size_con[i,j] != 0:
                        tosend_2[i,j] = 1
            #通过UORA传输BSR
            if sum(tosend_2[i])>0 and N_RU_random[i]>0:
                [A2[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_2[i], N_STA, N_RU_random[i],A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax) 
        
        # print('A2=',A2)
        # print('req_duration',req_period)

        #数据传输
        for i in range (N_SFU):
            time_remain[i] = time_max - req_period[i]
            for j in range (N_STA): 
                #固定的TS部分 
                if buffer_size_ts[i,j]>0 and A1[i,j] !=0:
                    sum_size1 = overhead/rate_RU_ul[i,j]
                    sum_size2 = overhead/rate_oru_ul[i,j]   
                    # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):
                    #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]
                    #     if buffer_size_ts[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]:
                    #         Total_utilized += buffer_size_ts[i,j]*1.07
                    #     else:
                    #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]

                    Total_allocated += ul_duration_max_w[i]*rate_RU_ul[i,j]
                    Total_allocated_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]
                    if buffer_size_ts[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_ul[i,j]:
                        Total_utilized += buffer_size_ts[i,j]*1.07
                        Total_utilized_ts += buffer_size_ts[i,j]*1.07
                    else:
                        Total_utilized += ul_duration_max_w[i]*rate_RU_ul[i,j]
                        Total_utilized_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]

                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:                                
                            sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_ul[i,j]
                            if sum_size1 <= ul_duration_max_w[i]:                                 
                                buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                sum_size2 += buff_S_UL[i][j][k]/rate_oru_ul[i,j]
                                if sum_size2 < ul_duration_max_o[i]:
                                    arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                    size_data_UL[i][j].append(buff_S_UL[i][j][k])
                                                                                            
                    #假设光资源肯定足够，1：1情况,到达SFU的肯定有足够的光资源能到达MFU
                    receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                        
                    #计算接收时间
                    #第一个数据包
                    if receive_cycle_num_UL[i,j]>0:
                        end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] + TF/(rate_RU_list[0]*9) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_oru_ul[i,j]
                        if receive_cycle_num_UL[i,j] > 1:
                            for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_oru_ul[i,j]
                    
                        receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                        if pack_num_UL[i,j] == receive_num_UL[i,j]:
                            buff_A_UL[i][j] = []
                            buff_S_UL[i][j] = []
                            remain_num_UL[i,j] = 0
                        elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                            buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                            buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                            remain_num_UL[i,j] = len(buff_A_UL[i][j])  
                
                #随机竞争的部分
                if ((buffer_size_con[i,j] > 0) and (A2[i,j] != 0)):                #NTS
                    a = 1
                    sum_size1 = overhead/rate_RU_list[a]
                    sum_size2 = overhead/rate_sub_list[a]
                    # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):             
                    #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]
                    #     if buffer_size_con[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]:
                    #         Total_utilized += buffer_size_con[i,j]*1.07
                    #     else:
                    #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]
                    Total_allocated += ul_duration_max_w[i]*rate_RU_list[a]
                    if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                        Total_utilized += buffer_size_con[i,j]*1.07
                    else:
                        Total_utilized += ul_duration_max_w[i]*rate_RU_list[a]
                    if j in Set_TS_STA[i]:
                        Total_allocated_ts += ul_duration_max_w[i]*rate_RU_list[a]
                        if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                            Total_utilized_ts += buffer_size_con[i,j]*1.07
                        else:
                            Total_utilized_ts += ul_duration_max_w[i]*rate_RU_list[a]
                    else:
                        Total_allocated_nts += ul_duration_max_w[i]*rate_RU_list[a]
                        if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                            Total_utilized_nts += buffer_size_con[i,j]*1.07
                        else:
                            Total_utilized_nts += ul_duration_max_w[i]*rate_RU_list[a]                        

                    for k in range (remain_num_UL[i,j]):
                        if buff_A_UL[i][j][k] <= Timer[i]:                                
                            sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_list[a]
                            if sum_size1 <= ul_duration_max_w[i]:                                 
                                buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                sum_size2 += buff_S_UL[i][j][k]/rate_sub_list[a]
                                if sum_size2 < ul_duration_max_o[i]:
                                    arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                    size_data_UL[i][j].append(buff_S_UL[i][j][k])
                                                                                            
                    #假设光资源肯定足够，1：1情况,到达SFU的肯定有足够的光资源能到达MFU
                    receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                        
                    #计算接收时间
                    #第一个数据包
                    if receive_cycle_num_UL[i,j]>0:
                        end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] + TF/(rate_RU_list[0]*8) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_sub_list[a]
                        if receive_cycle_num_UL[i,j] > 1:
                            for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_sub_list[a]
                    
                        receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                        if pack_num_UL[i,j] == receive_num_UL[i,j]:
                            buff_A_UL[i][j] = []
                            buff_S_UL[i][j] = []
                            remain_num_UL[i,j] = 0
                        elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                            buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                            buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                            remain_num_UL[i,j] = len(buff_A_UL[i][j])              


            if sum(receive_cycle_num_UL[i]) > 0:
                Timer[i] += ul_duration_max_w[i]+ul_duration_max_o[i] + T_fixed
            else:
                Timer[i] += DIFS + tTrans_o + tTrans_w

        # print('本轮收到的',receive_cycle_num_UL)


        for i in range (N_SFU):
            #计算是否需要多轮传输
            while(time_remain[i]>0):
                tosend_UL[i] = 0
                req_capacity[i] = 0
                request_duration_w[i] = 0
                request_duration_o[i] = 0
                ul_duration_max_o[i] = 0
                ul_duration_max_w[i] = 0
                req_period[i] = 0
                receive_cycle_num_UL[i] = 0
                buff_A_SFU_UL[i] = [[] for _ in range(N_STA)]
                buff_S_SFU_UL[i] = [[] for _ in range(N_STA)]
                arri_data_UL[i] = [[] for _ in range(N_STA)]
                size_data_UL[i] = [[] for _ in range(N_STA)]
                tosend_ts1 = np.zeros((N_SFU,N_STA), dtype=int)
                tosend_2 = np.zeros((N_SFU,N_STA), dtype=int)        
                buffer_size_ts[i] = 0
                buffer_size_con[i] = 0
                req_capacity_ts[i] = 0        
                A1 = np.zeros((N_SFU, N_STA))
                A2 = np.zeros((N_SFU, N_STA))
                N_RU_random = np.zeros(N_SFU,dtype=int)       

                for j in range (N_STA):
                    if remain_num_UL[i,j] > 0:
                        if buff_A_UL[i][j][0] <= Timer[i]:
                            tosend_UL[i,j] = 1
                            if j in Set_TS_STA[i]:
                                tosend_ts1[i,j] = 1

                #通过UORA传输BSR
                if sum(tosend_ts1[i])>0:
                    [A1[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_ts1[i], N_STA, 36,A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax)
            
                #获取buffer的大小
                # Timer[i] += BSRP/(rate_RU_list[0]*9) + BSRP/(9*2*rate_suboptical) + SIFS
                for j in range (N_STA):
                    if ((remain_num_UL[i,j] > 0)and(A1[i,j]==1)):
                        for k in range (remain_num_UL[i,j]):
                            if buff_A_UL[i][j][k] <= Timer[i]:
                                buffer_size_ts[i,j] += buff_S_UL[i][j][k] 
                        req_capacity_ts[i] += buffer_size_ts[i,j]*1.07
                
                if req_capacity_ts[i]>0:      #新一轮有固定TS数据来
                    sub_RU_ul[i],rate_RU_ul[i]=allocation_algorithm.allocation(N_RU_ts[i],buffer_size_ts[i])
                    for j in range (N_STA):
                        if buffer_size_ts[i,j] > 0:
                            rate_oru_ul[i,j] = sub_RU_ul[i,j]*(rate_suboptical*2)        #？？？？？？？？？？？？？？假设光资源完全足够，后续修改
                            request_duration_w[i,j] = buffer_size_ts[i,j]*1.07/rate_RU_ul[i,j] + overhead/rate_RU_ul[i,j]
                            request_duration_o[i,j] = buffer_size_ts[i,j]*1.07/rate_oru_ul[i,j] + overhead/rate_oru_ul[i,j]
                    ul_duration_max_o[i] = min(max(request_duration_o[i]),set_UL_DURATION_o)
                    ul_duration_max_w[i] = min(max(request_duration_w[i]),set_UL_DURATION_w)
                    req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
                    
                    if (req_period[i]<time_remain[i]):                #仍有空余时间
                        time_remain[i] = time_remain[i] - req_period[i]
                        
                    elif (req_period[i]>=time_remain[i]):               #没有空闲时间
                        if time_remain[i]>T_fixed:
                            ul_duration_max_w[i] = min((time_remain[i]-T_fixed)*1/1.57,set_UL_DURATION_w)
                            ul_duration_max_o[i] = min((time_remain[i]-T_fixed)*0.57/1.57,set_UL_DURATION_o)
                            req_period[i] = time_remain[i]
                            time_remain[i] = 0
                        else:
                            ul_duration_max_w[i] = 0
                            ul_duration_max_o[i] = 0
                            time_remain[i] = 0
                else:                                #新一轮没有固定TS数据来
                    ul_duration_max_o[i] = set_UL_DURATION_o
                    ul_duration_max_w[i] = set_UL_DURATION_w
                    req_period[i] = ul_duration_max_o[i] + ul_duration_max_w[i] + T_fixed
                    if (req_period[i]<time_remain[i]):                #仍有空余时间
                        time_remain[i] = time_remain[i] - req_period[i]
                        
                    elif (req_period[i]>=time_remain[i]):              #没有空闲时间
                        if time_remain[i]>T_fixed:
                            ul_duration_max_w[i] = min((time_remain[i]-T_fixed)*1/1.57,set_UL_DURATION_w)
                            ul_duration_max_o[i] = min((time_remain[i]-T_fixed)*0.57/1.57,set_UL_DURATION_o)
                            req_period[i] = time_remain[i]
                            time_remain[i] = 0
                        else:
                            ul_duration_max_w[i] = 0
                            ul_duration_max_o[i] = 0
                            time_remain[i] = 0  

                #分配固定大小的RU用于随机接入
                N_RU_random[i] = int(math.floor((N_RU - N_RU_ts[i])/2))                         
                    
                #第二轮随机接入
                for j in range (N_STA):
                    if ((remain_num_UL[i,j] > 0)and (A1[i,j]!=1)):
                        for k in range (remain_num_UL[i,j]):
                            if buff_A_UL[i][j][k] <= Timer[i]:
                                buffer_size_con[i,j] += buff_S_UL[i][j][k]
                        if buffer_size_con[i,j] != 0:
                            tosend_2[i,j] = 1
                #通过UORA传输BSR
                if sum(tosend_2[i])>0 and N_RU_random[i]>0:
                    [A2[i], _, A_CWO[i], A_BO[i], A_Retry[i]] = UORA_count.UORA_count(tosend_2[i], N_STA, N_RU_random[i],A_CWO[i],A_BO[i], A_Retry[i], CWOmin, CWOmax) 


                #传输过程
                for j in range (N_STA):
                    #TS固定部分
                    if buffer_size_ts[i,j]>0 and A1[i,j] !=0:
                        sum_size1 = overhead/rate_RU_ul[i,j]
                        sum_size2 = overhead/rate_oru_ul[i,j]
                        # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):
                        #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]
                        #     if buffer_size_ts[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]:
                        #         Total_utilized += buffer_size_ts[i,j]*1.07
                        #     else:
                        #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_ul[i,j]

                        Total_allocated += ul_duration_max_w[i]*rate_RU_ul[i,j]
                        Total_allocated_ts += ul_duration_max_w[i]*rate_RU_ul[i,j]
                        if buffer_size_ts[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_ul[i,j]:
                            Total_utilized += buffer_size_ts[i,j]*1.07
                            Total_utilized_ts += buffer_size_ts[i,j]*1.07
                        else:
                            Total_utilized += ul_duration_max_w[i]*rate_RU_ul[i,j]
                            Total_utilized_nts += ul_duration_max_w[i]*rate_RU_ul[i,j]

                        for k in range (remain_num_UL[i,j]): 
                            if (buff_A_UL[i][j][k] <= Timer[i]):
                                sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_ul[i,j]
                                if sum_size1 <= ul_duration_max_w[i]:
                                    buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                    buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                    sum_size2 += buff_S_UL[i][j][k]/rate_oru_ul[i,j]
                                    if sum_size2 < ul_duration_max_o[i]:
                                        arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                        size_data_UL[i][j].append(buff_S_UL[i][j][k])
                        receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                        #计算接收时间
                        #第一个数据包
                        if receive_cycle_num_UL[i,j]>0:
                            end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] + TF/(rate_RU_list[0]*9) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_oru_ul[i,j]
                            if receive_cycle_num_UL[i,j] > 1:
                                for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                    end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_oru_ul[i,j]

                            receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                            if pack_num_UL[i,j] == receive_num_UL[i,j]:
                                buff_A_UL[i][j] = []
                                buff_S_UL[i][j] = []
                                remain_num_UL[i,j] = 0
                            elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                                buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                                buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                                remain_num_UL[i,j] = len(buff_A_UL[i][j])  

                    #random部分
                    if ((buffer_size_con[i,j] > 0) and (A2[i,j] != 0)):                #NTS
                        a = 1
                        sum_size1 = overhead/rate_RU_list[a]
                        sum_size2 = overhead/rate_sub_list[a]
                        # if (ul_duration_max_w[i] != 0 and ul_duration_max_o[i] != 0):
                        #     Total_allocated += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]
                        #     if buffer_size_con[i,j]*1.07 <= (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]:
                        #         Total_utilized += buffer_size_con[i,j]*1.07
                        #     else:
                        #         Total_utilized += (req_period[i]-T_fixed)*ul_duration_max_w[i]/(ul_duration_max_w[i]+ul_duration_max_o[i])*rate_RU_list[a]                       

                        Total_allocated += ul_duration_max_w[i]*rate_RU_list[a]
                        if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                            Total_utilized += buffer_size_con[i,j]*1.07
                        else:
                            Total_utilized += ul_duration_max_w[i]*rate_RU_list[a]
                        
                        if j in Set_TS_STA[i]:
                            Total_allocated_ts += ul_duration_max_w[i]*rate_RU_list[a]
                            if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                                Total_utilized_ts += buffer_size_con[i,j]*1.07
                            else:
                                Total_utilized_ts += ul_duration_max_w[i]*rate_RU_list[a]
                        else:
                            Total_allocated_nts += ul_duration_max_w[i]*rate_RU_list[a]
                            if buffer_size_con[i,j]*1.07 <= ul_duration_max_w[i]*rate_RU_list[a]:
                                Total_utilized_nts += buffer_size_con[i,j]*1.07
                            else:
                                Total_utilized_nts += ul_duration_max_w[i]*rate_RU_list[a]                            



                        for k in range (remain_num_UL[i,j]): 
                            if (buff_A_UL[i][j][k] <= Timer[i]):
                                sum_size1 += buff_S_UL[i][j][k][0]/rate_RU_list[a]
                                if sum_size1 <= ul_duration_max_w[i]:
                                    buff_A_SFU_UL[i][j].append(buff_A_UL[i][j][k])                #刷新，不累加的
                                    buff_S_SFU_UL[i][j].append(buff_S_UL[i][j][k])
                                    sum_size2 += buff_S_UL[i][j][k]/rate_sub_list[a]
                                    if sum_size2 < ul_duration_max_o[i]:
                                        arri_data_UL[i][j].append(buff_A_UL[i][j][k])
                                        size_data_UL[i][j].append(buff_S_UL[i][j][k])
                        receive_cycle_num_UL[i,j] = len(arri_data_UL[i][j])
                        #计算接收时间
                        #第一个数据包
                        if receive_cycle_num_UL[i,j]>0:
                            end_time_UL[i][j][receive_num_UL[i,j]] = Timer[i] + TF/(rate_RU_list[0]*8) + SIFS + ul_duration_max_w[i] + tProcess + size_data_UL[i][j][0]/rate_sub_list[a]
                            if receive_cycle_num_UL[i,j] > 1:
                                for k in range ((receive_num_UL[i,j]+1),(receive_num_UL[i,j]+ receive_cycle_num_UL[i,j])):
                                    end_time_UL[i][j][k] = end_time_UL[i][j][k-1] + size_data_UL[i][j][k-receive_num_UL[i,j]]/rate_sub_list[a]

                            receive_num_UL[i,j] += receive_cycle_num_UL[i,j]                                                             
                            if pack_num_UL[i,j] == receive_num_UL[i,j]:
                                buff_A_UL[i][j] = []
                                buff_S_UL[i][j] = []
                                remain_num_UL[i,j] = 0
                            elif pack_num_UL[i,j] > receive_num_UL[i,j]:
                                buff_A_UL[i][j] = buff_A_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]                           #所有剩下没传的
                                buff_S_UL[i][j] = buff_S_UL[i][j][-(pack_num_UL[i,j]-receive_num_UL[i,j]):]
                                remain_num_UL[i,j] = len(buff_A_UL[i][j])  

                if sum(receive_cycle_num_UL[i]) > 0:
                    Timer[i] += ul_duration_max_w[i]+ul_duration_max_o[i] + T_fixed

                else:
                    Timer[i] += DIFS + tTrans_o + tTrans_w + T_fixed

        receive_num = sum(sum(receive_num_UL)) 
        pack_num = sum(sum(pack_num_UL)) 
        # b = sum(sum(receive_num_UL))
        # d = sum(sum(pack_num_UL))
        

        # print('--------------')   
        # resource_ut1 = Total_allocated  
    #     # resource_ut2 = Total_utilized
    #     # resource_ut = Total_utilized/Total_allocated
    #     # print('utilization1=',resource_ut1)
    #     # print('utilization2=',resource_ut2)
    #     # print('utilization=',resource_ut)  

        # print('receive',receive_num_UL)
        # print('pack',pack_num_UL)
        # print('remain',remain_num_UL)
        # print(Timer)


        if np.array_equal(receive_num,pack_num):
            break
        else:
            continue


    # #计算时延和抖动
    latency_ts_sum = np.zeros(N_SFU)
    latency_nts_sum = np.zeros(N_SFU)
    jitter_ts_sum = np.zeros(N_SFU)
    jitter_nts_sum = np.zeros(N_SFU)
    for i in range (N_SFU):  
        for j in range (N_STA):
            for k in range (pack_num_UL[i,j]):
                latency_UL[i][j][k] = end_time_UL[i][j][k] - Arri_UL[i][j][k]

            mean_latency_UL[i,j] = np.mean(latency_UL[i][j])
            mean_jitter_UL[i,j] = np.std(latency_UL[i][j])  
    average_latency_ul = np.mean(mean_latency_UL)/1000
    average_jitter_ul = np.mean(mean_jitter_UL)/1000

    for i in range (N_SFU):
        for j in range (N_STA):
            if j in Set_TS_STA[i]:
                latency_ts_sum[i] += mean_latency_UL[i,j]
                jitter_ts_sum[i] += mean_jitter_UL[i,j]
            else:
                latency_nts_sum[i] += mean_latency_UL[i,j]
                jitter_nts_sum[i] += mean_jitter_UL[i,j]

    latency_ts = None
    latency_nts = None
    jitter_ts = None
    jitter_nts = None
    if sum(N_TS_STA) != 0:     
        latency_ts = sum(latency_ts_sum)/sum(N_TS_STA)/1000 
        jitter_ts = sum(jitter_ts_sum)/sum(N_TS_STA)/1000
    else:
        latency_ts = None
        jitter_ts = None

    if sum(N_NTS_STA) != 0: 
        latency_nts = sum(latency_nts_sum)/sum(N_NTS_STA)/1000
        jitter_nts = sum(jitter_nts_sum)/sum(N_NTS_STA)/1000
    else:
        latency_nts = None
        jitter_nts = None
        
    resource_ut = Total_utilized/Total_allocated
    resource_ts = Total_utilized_ts/Total_allocated_ts
    resource_nts = Total_utilized_nts/Total_allocated_nts

    print('latency_ts=',latency_ts)
    print('latency_nts=',latency_nts)
    print('Utilization=',resource_ut)
    print('Utilization_ts=',resource_ts)
    print('Utilization_nts=',resource_nts)

    # print('utilization1=',resource_ut1)
    # print('utilization2=',resource_ut2)
    # print('utilization=',resource_ut)    
    return latency_ts,latency_nts,jitter_ts,jitter_nts,resource_ts,resource_nts

def find_BW(req,T_last):
    N_RU = np.zeros(len(req))
    for i in range (len(req)):
        if req[i] == 0:
            N_RU[i] = 0
        elif req[i]>0 and req[i]<143*T_last[i]:
            N_RU[i] = 8
        elif req[i]>=143*T_last[i] and req[i]<287*T_last[i]:
            N_RU[i] = 16
        elif req[i]>=287*T_last[i] and req[i]<600*T_last[i]:    
            N_RU[i] = 32
        elif req[i]>=600*T_last[i]:
            N_RU[i] = 64
    return N_RU

def request_RU_size(num):
    if num <= 1:
        a = 1
    elif num>1 and num <= 2:
        a = 2
    elif num>2 and num<=4:
        a = 4
    elif num>4 and num<=8:
        a = 8
    elif num>8 and num<=16:
        a = 16
    elif num>16 and num<=32:
        a = 32
    elif num>32 and num<=64:
        a = 64
    return a

# N_SFU = 4
# N_STA = 30
# duration = 1000000
# N_RU = 64
# gama = [0.1,0.2,0.3,0.4]    #房间内TS业务的比
# latency_ts,latency_nts,jitter_ts,jitter_nts,resource_ut,resource_ts,resource_nts = transmission_ul_flexible(N_SFU,N_STA,N_RU,duration,gama)
# print('ave_delay_dl=',ave_delay_dl)
# print('ave_delay_ul=',ave_delay_ul)