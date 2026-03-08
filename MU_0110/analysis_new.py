import numpy as np
import math
import scipy.optimize
import matplotlib.pyplot as plt

def tau(N, R, CWOmin, CWOmax):
    m=math.log(CWOmax+1,2)- math.log(CWOmin+1,2) 
    m = int(m)

    def tau(t):
        p=1-(1-t/R)**(N-1)
        X0 = (-1*R/2)*math.floor(CWOmin/R)**2 + (CWOmin-R/2)*math.floor(CWOmin/R)
        W = []
        X = []
        for k in range (m):
            W.append((CWOmin+1)*2**k-1)
            X.append((-1*R/2)*math.floor(W[k]/R)**2 + (W[k]-R/2)*math.floor(W[k]/R))

        if m == 0:
            print(m)
            result = t - (CWOmin +1)/(CWOmin + 1 + X0)
        elif m == 1:
            SUM =0
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m)
        elif m == 2:
            SUM = X[1]*p/2
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m)
        elif m == 3:
            SUM = (X[2]*p**2)/4 + (X[1]*p)/2   
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m)
        elif m == 4:
            SUM = (X[3]*p**3)/8 + (X[2]*p**2)/4 + (X[1]*p)/2  
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m)
        elif m == 5:
            SUM = (X[4]*p**4)/16 + (X[3]*p**3)/8 + (X[2]*p**2)/4 + (X[1]*p)/2 
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m) 
        elif m == 6:
            SUM = (X[5]*p**5)/32 + (X[4]*p**4)/16 + (X[3]*p**3)/8 + (X[2]*p**2)/4 + (X[1]*p)/2  
            result = t - (CWOmin +1)/( CWOmin + 1 + (1-p)*X0 + (1-p) * SUM + X[m-1]*(p/2)**m) 
        elif m > 6:
            print('this backoff stage value is not supported.')             
        return result

    t = scipy.optimize.fsolve(tau,[0])
    alpha = (N*t*(1-t/R)**(N-1))/R
    r = N*t*(1-t/R)**(N-1)
    return t,alpha

def analysis1(a, N, R, CWOmin, CWOmax):
    N_TS_total = 0
    N_NTS_total = 0

    [tau1,_] =tau((a*N), R, CWOmin, CWOmax)           #BSR阶段所有STA都参与竞争
    N_ts_bsr = (a*N)*tau1*(1-tau1/R)**((a*N)-1)     #BSR阶段成功竞争到RU的TS STA的数量
    N_contention = N - N_ts_bsr                #下一周期需要参与竞争的所有STA的数量
    r_fixed = N_ts_bsr
    r_succ1 = r_fixed

    #计算实际占用的无线资源个数
    r_random = R - r_fixed
    [tau2,_] =tau(N_contention, r_random, CWOmin, CWOmax) 
    r_succ2 = N_contention*tau2*(1-tau2/r_random)**(N_contention-1)        #预计第二个周期参与竞争的STA需要的RU个数
    r_succ_ts = ((a*N)-N_ts_bsr)/N_contention*r_succ2
    r_succ_nts = ((1-a)*N)/N_contention*r_succ2

    r = r_succ1 + r_succ2             #预计成功占用的RU个数，即预计成功传输到WiFi端的STA个数
    N_TS_total = a*N
    N_NTS_total = (N - a*N)

    Ut_wireless = r/R
    Ut_wireless_ts = r_fixed+r_succ_ts/R
    Ut_wireless_nts = r_succ_nts/R
    SAP_ts = r_succ_ts+r_fixed/N_TS_total
    SAP_nts = r_succ_nts/N_NTS_total
    SAP = r/N

    return Ut_wireless,Ut_wireless_ts,Ut_wireless_nts,SAP,SAP_ts,SAP_nts

def analysis2(N_SFU,a, N, R, CWOmin, CWOmax,N_TU_total):
    tau1 = np.zeros(N_SFU)
    tau2 = np.zeros(N_SFU)
    N_ts_bsr = np.zeros(N_SFU)
    N_contention = np.zeros(N_SFU)
    r_fixed = np.zeros(N_SFU)
    r_succ1 = np.zeros(N_SFU)
    r_succ2 = np.zeros(N_SFU)
    r_succ_ts = np.zeros(N_SFU)
    r_succ_nts = np.zeros(N_SFU)
    r_random = np.zeros(N_SFU)
    r = np.zeros(N_SFU)
    N_TS_total = 0
    N_NTS_total = 0

    for i in range (N_SFU):
        [tau1[i],_] =tau((a[i]*N), R, CWOmin, CWOmax)           #BSR阶段所有STA都参与竞争
        N_ts_bsr[i] = (a[i]*N)*tau1[i]*(1-tau1[i]/R)**((a[i]*N)-1)     #BSR阶段成功竞争到RU的TS STA的数量
        N_contention[i] = N - N_ts_bsr[i]                #下一周期需要参与竞争的所有STA的数量
        r_fixed[i] = N_ts_bsr[i]
        r_succ1[i] = r_fixed[i]

        #计算实际占用的无线资源个数
        r_random[i] = R - r_fixed[i]
        [tau2[i],_] =tau(N_contention[i], r_random[i], CWOmin, CWOmax) 
        r_succ2[i] = N_contention[i]*tau2[i]*(1-tau2[i]/r_random[i])**(N_contention[i]-1)        #预计第二个周期参与竞争的STA需要的RU个数
        r_succ_ts[i] = ((a[i]*N)-N_ts_bsr[i])/N_contention[i]*r_succ2[i]
        r_succ_nts[i] = ((1-a[i])*N)/N_contention[i]*r_succ2[i]

        r[i] = r_succ1[i] + r_succ2[i]             #预计成功占用的RU个数，即预计成功传输到WiFi端的STA个数
        N_TS_total += a[i]*N
        N_NTS_total += (N - a[i]*N)
        # g = math.ceil(r_succ1)+math.ceil(r_succ2)
        # N_SFU_max = int(math.floor(N_TU_total/g))
    Ut_wireless = sum(r)/(R*N_SFU)
    Ut_wireless_ts = (sum(r_fixed)+sum(r_succ_ts))/(R*N_SFU)
    Ut_wireless_nts = sum(r_succ_nts)/(R*N_SFU)
    SAP_ts = (sum(r_succ_ts)+sum(r_fixed))/N_TS_total
    SAP_nts = sum(r_succ_nts)/N_NTS_total
    SAP = sum(r)/(N*N_SFU)

    return Ut_wireless,Ut_wireless_ts,Ut_wireless_nts,SAP,SAP_ts,SAP_nts

def analysis3(N_SFU,a, N, R, CWOmin, CWOmax,N_TU_total):
    tau1 = np.zeros(N_SFU)
    tau2 = np.zeros(N_SFU)
    N_ts_bsr = np.zeros(N_SFU)
    N_contention = np.zeros(N_SFU)
    r_fixed = np.zeros(N_SFU)
    r_succ1 = np.zeros(N_SFU)
    r_succ2 = np.zeros(N_SFU)
    r_succ_ts = np.zeros(N_SFU)
    r_succ_nts = np.zeros(N_SFU)
    r_random = np.zeros(N_SFU)
    r = np.zeros(N_SFU)
    N_TS_total = 0
    N_NTS_total = 0
    n_ts = np.zeros(N_SFU)

    for i in range (N_SFU):
        n_ts[i] = math.ceil(a[i]*N)
        [tau1[i],_] =tau(n_ts[i], R, CWOmin, CWOmax)           #BSR阶段所有STA都参与竞争
        N_ts_bsr[i] = math.ceil(n_ts[i]*tau1[i]*(1-tau1[i]/R)**(n_ts[i]-1))     #BSR阶段成功竞争到RU的TS STA的数量
        N_contention[i] = N - N_ts_bsr[i]                #下一周期需要参与竞争的所有STA的数量
        r_fixed[i] = N_ts_bsr[i]
        r_succ1[i] = r_fixed[i]

        #计算实际占用的无线资源个数
        r_random[i] = R - r_fixed[i]
        [tau2[i],_] =tau(N_contention[i], r_random[i], CWOmin, CWOmax) 
        r_succ2[i] = N_contention[i]*tau2[i]*(1-tau2[i]/r_random[i])**(N_contention[i]-1)        #预计第二个周期参与竞争的STA需要的RU个数
        r_succ_ts[i] = (n_ts[i]-N_ts_bsr[i])/N_contention[i]*r_succ2[i]
        r_succ_nts[i] = (N-n_ts[i])/N_contention[i]*r_succ2[i]

        r[i] = r_succ1[i] + r_succ2[i]             #预计成功占用的RU个数，即预计成功传输到WiFi端的STA个数
        N_TS_total += n_ts[i]
        N_NTS_total += (N - n_ts[i])
        # g = math.ceil(r_succ1)+math.ceil(r_succ2)
        # N_SFU_max = int(math.floor(N_TU_total/g))
    Ut_wireless = sum(r)/(R*N_SFU)
    Ut_wireless_ts = (sum(r_fixed)+sum(r_succ_ts))/(R*N_SFU)
    Ut_wireless_nts = sum(r_succ_nts)/(R*N_SFU)
    SAP_ts = (sum(r_succ_ts)+sum(r_fixed))/N_TS_total
    SAP_nts = sum(r_succ_nts)/N_NTS_total
    SAP = sum(r)/(N*N_SFU)

    return Ut_wireless,Ut_wireless_ts,Ut_wireless_nts,SAP,SAP_ts,SAP_nts

# # #计算测试
# N_STA_Array=np.arange(3,30,3)
# N_RU=16
# N_TU_total = 170
# gama=[0.2]                          
# CWOmin=7
# CWOmax=63
# N_SFU = 1

# SAP_ts = np.zeros(len(N_STA_Array))
# add = np.zeros(len(N_STA_Array))
# for i in range (len(N_STA_Array)):
#     [_,_,_,_,SAP_ts[i],_]=analysis2(N_SFU,gama, N_STA_Array[i], N_RU, CWOmin, CWOmax,N_TU_total)
#     add[i] = N_STA_Array[i]*0.2*(1-SAP_ts[i])
# plt.figure(1)
# plt.subplot(121)
# plt.plot(N_STA_Array,SAP_ts)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('SAP_ts')
# plt.xlim(0,30)
# # plt.ylim(0,1)
# plt.grid(True)

# plt.subplot(122)
# plt.plot(N_STA_Array,add)
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('add')
# plt.xlim(0,30)
# # plt.ylim(0,1)
# plt.grid(True)
# plt.show()

# N = 30 
# R = 16
# CWOmin = 7
# CWOmax = 31
# t,alpha,r=tau(N, R, CWOmin, CWOmax)
# print('t=',t)
# print('alpha=',alpha)
# print('r=',r)