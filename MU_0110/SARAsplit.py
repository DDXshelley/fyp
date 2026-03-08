import math
import numpy as np

def split(N_SFU,N_STA,N_RU_total,demands,Set_TS,T):

    cw = 11.1
    rou = 2
    S=1024
    N_RU_req=np.zeros((N_SFU,N_STA))         #请求的26-tone RU的个数
    N_sc_req=np.zeros((N_SFU,N_STA))         #请求的对应26-tone RU的匹配的光子载波数 
    N_RU_ts=np.zeros(N_SFU,dtype=int)
    N_RU_nts = np.zeros(N_SFU,dtype=int)
    N_sc_ts=np.zeros(N_SFU)
    N_sc_nts = np.zeros(N_SFU)
    RU_RA = np.zeros(N_SFU,dtype=int)    
    for i in range (N_SFU):
        if T[i] > 0:
            for j in range (N_STA):
                N_RU_req[i,j] = math.ceil(demands[i,j]/(0.37*T[i]*cw))

    # print('需求',N_RU_req)
    for i in range (N_SFU):
        a = sum(N_RU_req[i])
        b_ts = 0
        b_nts = 0
        if a > N_RU_total:
            for j in range (N_STA):
                if j in Set_TS[i]:
                    b_ts += N_RU_req[i,j]
                else:
                    b_nts += N_RU_req[i,j]
            if b_ts <= N_RU_total:
                for j in range (N_STA):
                    if j not in Set_TS[i]:
                        N_RU_req[i,j] = math.floor((N_RU_total-b_ts)*N_RU_req[i,j]/b_nts)
            else:
                for j in range (N_STA):
                    if j in Set_TS[i]:
                        N_RU_req[i,j] = math.floor(N_RU_total*N_RU_req[i,j]/b_ts)
                    else:
                        N_RU_req[i,j] = 0


        for j in range (N_STA):
            N_sc_req[i,j] = N_RU_req[i,j]*rou
            if j in Set_TS[i]:
                N_RU_ts[i] += N_RU_req[i,j]
                N_sc_ts[i] += N_sc_req[i,j]
            else:
                N_RU_nts[i] += N_RU_req[i,j] 
                N_sc_nts[i] += N_sc_req[i,j]
           
    # print('需求',N_RU_req)
            
    for i in range (N_SFU):
        if sum(sum(N_sc_req))>S and sum(N_sc_ts)<=S:
            N_sc_nts[i] = math.floor((S-sum(N_sc_ts))*N_sc_nts[i]/(sum(N_sc_nts)))
            N_RU_nts[i] = math.floor(N_sc_nts[i]/rou)
        elif sum(sum(N_sc_req))>S and sum(N_sc_ts)>S:
            N_sc_ts[i] = math.floor(S*N_sc_ts[i]/(sum(N_sc_ts)))
            N_RU_ts[i] = math.floor(N_sc_ts[i]/rou)
            N_sc_nts[i] = 0
            N_RU_nts[i] = 0
    
    for i in range (N_SFU):
        RU_RA[i] = int(N_RU_total - N_RU_nts[i]-N_RU_ts[i])
    return N_RU_ts,N_RU_nts,RU_RA


# # # 示例使用
# total_apples = 64
# demands = [2,30,1,28,3,4,1,29,2]
# Set_TS = [1,3,7]
# result,rate = allocation(total_apples, demands)
# print("最终分配:", result)
# print("速率",rate)

# a = [1,2,4,8,6,32]
# b = a.index(2)
# print(b)


