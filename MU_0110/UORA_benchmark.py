import numpy as np

#每个周期进行的UORA过程
def UORA_count(B,  N_STA, N_RU, A_CWO, A_BO, A_Retry, CWOmin, CWOmax):
    RETRYmax = 10000                          #最大重传次数
    N_STA1 = np.sum(B)                #有数据要传的STA的个数
    A = np.zeros( N_STA)
    flag = np.zeros( N_RU)

    def fresh_BO(OCW):                        #随机产生一个BO值
        new_BO = 0
        new_BO = np.random.randint(OCW + 1, size=1) 
        return new_BO


    def inc_OCW(Retry, OCWmin, OCWmax):       #设置竞争窗口
        new_OCW = (OCWmin + 1) * 2**Retry - 1
        # new_OCW[new_OCW > OCWmax] = OCWmax
        new_OCW = min(new_OCW,OCWmax)
        return new_OCW 

    #初始定义
    # A_Retry = np.zeros((N_AP,N_STA))                #重传次数
    # colls = np.zeros((N_STA, RETRYmax))      #碰撞矩阵
    # succs = np.zeros((N_STA, RETRYmax))      #成功矩阵
    # s_cnt = np.zeros(N_STA)                  #成功的STA的序号
    # A_CWO = np.ones((N_AP,N_STA)) * CWOmin          #竞争窗口
    # A_BO = np.zeros((N_AP, N_STA))


    Send_set = np.arange(0, N_STA)                        #所有STA序号
    Set_success = []
    Set_fail = []
    RU_occupied = np.zeros((N_STA, N_RU))                    #RU矩阵，RU被选中，置一
    if int(N_STA1) != 0:
        for j in range(N_STA):
            if B[j] == 1:
                # A_BO[i,j] = fresh_BO(A_CWO[i,j])             #随机产生的退避计数值 
                if   A_BO[j] - N_RU <= 0:
                    Set_success.append(j)
                elif A_BO[j] - N_RU > 0:
                    Set_fail.append(j)   
    # print('更新后的A_BO=',A_BO)
    # print('本周期计数值到达0的STA序号=',Set_success)
    # print('本周期计数值未到达0的STA序号=',Set_fail)

    #传输STA,更新BO，检测碰撞
    for c in  Set_success:
        RU_occupied[c, np.random.randint(0, N_RU)] = 1        #每个STA随机选择一个RU
    # print('RU_occupied=',RU_occupied)

    # s_cnt[Send_set - 1] = 0                                   #成功传输的STA个数
    #碰撞检测
    for n_ru in range(N_RU):                                  #碰撞检测
        con_num = sum(RU_occupied[:,n_ru])         #统计每个RU被几个STA占用            
        if con_num == 1:                                    #只有一个STA要传
            ru_choosen = np.where(RU_occupied[:, n_ru] == 1)[0]
            # print('第'+str(n_ru)+'被占用的RU的序号d=',ru_choosen)
            flag[n_ru] = 1                              #没有发生碰撞，标记为1
            # succs[int(d), int(A_Retry[int(d)]) + 1] += 1
            # s_cnt[int(d)] += 1
            for c in Set_success:
                if RU_occupied[c,n_ru] == 1:
                    A_Retry[c] = 0                        #成功，重传次数为0
                    A_CWO[c] = inc_OCW(A_Retry[c], CWOmin[c], CWOmax[c]) #重置CWO
                    A_BO[c] = fresh_BO(A_CWO[c])                  #重置BO                               
                    A[c] = 1
        elif con_num > 1:                                   #有多个STA要传
            ru_choosen = np.where(RU_occupied[:, n_ru] == 1)[0]
            # print('第'+str(n_ru)+'被占用的RU的序号d=',ru_choosen)
            flag[n_ru] = 2                               #发生碰撞，标记为2
            # for sta in range(len(d)):
            #     # d[sta] = int(d[sta])
            #     colls[int(d[sta]), int(A_Retry[d[sta]]) + 1] += 1
            #     A_Retry[int(d[sta])] += 1
            for c in Set_success:
                if RU_occupied[c,n_ru] == 1:
                    A_Retry[c] += 1                        #成功，重传次数为0
                    if A_Retry[c] == RETRYmax:
                        A_CWO[c] = inc_OCW(0, CWOmin[c], CWOmax[c])  #达到上限，重置重传次数
                        A_BO[c] = fresh_BO(A_CWO[c])                  #重置BO 
                    else:
                        A_CWO[c] = inc_OCW(A_Retry[c], CWOmin[c], CWOmax[c]) #碰撞窗口翻倍
                        A_BO[c] = fresh_BO(A_CWO[c])                  #重置BO 
        # elif con_num == 0:                                   #没有STA要传
        #     for c in Set_fail:
            # print('第'+str(n_ru)+'个RU未被占用')
            
    for c in Set_fail:
        A_BO[c] -= N_RU
    return A, flag, A_CWO, A_BO, A_Retry



# # #计算测试
# #round 1
# N_AP = 1 
# N_STA = 10
# N_RU = 5
# CWOmin = 7
# CWOmax = 31
# A_CWO = np.ones((N_AP,N_STA)) * CWOmin          #竞争窗口
# A_BO = np.zeros((N_AP, N_STA))
# B = np.random.randint(2, size=(N_AP,N_STA))
# A_Retry = np.zeros((N_AP, N_STA))
# for i in range(N_AP):
#     for j in range(N_STA):
#         if B[i,j] == 1:
#             A_BO[i,j] = np.random.randint(A_CWO[i,j] + 1, size=1)             #随机产生的退避计数值
# print('初始A_BO=', A_BO)

# [A, flag, A_CWO1, A_BO1, ARetry1] = UORA_count(B, N_AP, N_STA, N_RU, A_CWO, A_BO, A_Retry, CWOmin, CWOmax)
# print('round 1')
# print("input STA=", B)
# print("output STA=", A)
# print("flag=", flag)
# print("A_CWO=", A_CWO1)
# print("A_BO=", A_BO1)
# print("ARetry=", ARetry1)

# #round 2
# B = np.random.randint(2, size=(N_AP,N_STA))
# [A, flag, A_CWO2, A_BO2, ARetry2] = UORA_count(B, N_AP, N_STA, N_RU, A_CWO1, A_BO1, ARetry1, CWOmin, CWOmax)
# print('round 2')
# print("input STA=", B)
# print("output STA=", A)
# print("flag=", flag)
# print("A_CWO=", A_CWO2)
# print("ARetry=", ARetry2)