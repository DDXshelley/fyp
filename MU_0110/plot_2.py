from numpy import *
import numpy as np
import matplotlib.pyplot as plt
import chapter4_copy
import chapter3_copy
import OECCscheme
import xlwt

N_SFU = 4
N_STA = np.arange(2,32,2)
N_RU = 64
duration = 1000000
gama = [0.1,0.2,0.3,0.4]    #房间内TS业务的比例 
BSRP_NTS = 16

CWOmin = [7,7]
CWOmax = [31,31]
tTXOP = 1500
N_TU_total = 170
N_RU2 = 16

iteration = 3
ave_delay_ts1 = np.zeros(iteration)
ave_delay_nts1 = np.zeros(iteration)
ave_jitter_ts1 = np.zeros(iteration)
ave_jitter_nts1 = np.zeros(iteration)
ave_SAP_ts1 = np.zeros(iteration)                 #成功接入概率
ave_SAP_nts1 = np.zeros(iteration)
ave_resuti_ts1 = np.zeros(iteration)              #资源利用率
ave_resuti_nts1 = np.zeros(iteration)
ave_rueffi_ts1 = np.zeros(iteration)              #单个RU利用效率
ave_rueffi_nts1 = np.zeros(iteration)

mean_delay_ts1 = np.zeros(len(N_STA))
mean_delay_nts1 = np.zeros(len(N_STA))
mean_jitter_ts1 = np.zeros(len(N_STA))
mean_jitter_nts1 = np.zeros(len(N_STA))
mean_SAP_ts1 = np.zeros(len(N_STA))
mean_SAP_nts1 = np.zeros(len(N_STA))
mean_resuti_ts1 = np.zeros(len(N_STA))
mean_resuti_nts1 = np.zeros(len(N_STA))
mean_rueffi_ts1 = np.zeros(len(N_STA))
mean_rueffi_nts1 = np.zeros(len(N_STA))

ave_delay_ts2 = np.zeros(iteration)
ave_delay_nts2 = np.zeros(iteration)
ave_jitter_ts2 = np.zeros(iteration)
ave_jitter_nts2 = np.zeros(iteration)
ave_SAP_ts2 = np.zeros(iteration)                 #成功接入概率
ave_SAP_nts2 = np.zeros(iteration)
ave_resuti_ts2 = np.zeros(iteration)              #资源利用率
ave_resuti_nts2 = np.zeros(iteration)
ave_rueffi_ts2 = np.zeros(iteration)              #单个RU利用效率
ave_rueffi_nts2 = np.zeros(iteration)

mean_delay_ts2 = np.zeros(len(N_STA))
mean_delay_nts2 = np.zeros(len(N_STA))
mean_jitter_ts2 = np.zeros(len(N_STA))
mean_jitter_nts2 = np.zeros(len(N_STA))
mean_SAP_ts2 = np.zeros(len(N_STA))
mean_SAP_nts2 = np.zeros(len(N_STA))
mean_resuti_ts2 = np.zeros(len(N_STA))
mean_resuti_nts2 = np.zeros(len(N_STA))
mean_rueffi_ts2 = np.zeros(len(N_STA))
mean_rueffi_nts2 = np.zeros(len(N_STA))

ave_delay_ts3 = np.zeros(iteration)
ave_delay_nts3 = np.zeros(iteration)
ave_jitter_ts3 = np.zeros(iteration)
ave_jitter_nts3 = np.zeros(iteration)
ave_SAP_ts3 = np.zeros(iteration)                 #成功接入概率
ave_SAP_nts3 = np.zeros(iteration)
ave_resuti_ts3 = np.zeros(iteration)              #资源利用率
ave_resuti_nts3 = np.zeros(iteration)
ave_rueffi_ts3 = np.zeros(iteration)              #单个RU利用效率
ave_rueffi_nts3 = np.zeros(iteration)

mean_delay_ts3 = np.zeros(len(N_STA))
mean_delay_nts3 = np.zeros(len(N_STA))
mean_jitter_ts3 = np.zeros(len(N_STA))
mean_jitter_nts3 = np.zeros(len(N_STA))
mean_SAP_ts3 = np.zeros(len(N_STA))
mean_SAP_nts3 = np.zeros(len(N_STA))
mean_resuti_ts3 = np.zeros(len(N_STA))
mean_resuti_nts3 = np.zeros(len(N_STA))
mean_rueffi_ts3 = np.zeros(len(N_STA))
mean_rueffi_nts3 = np.zeros(len(N_STA))

for i in range (len(N_STA)):
    for j in range (iteration):
        #chapter4
        ave_delay_ts1[j],ave_delay_nts1[j],ave_jitter_ts1[j],ave_jitter_nts1[j],ave_SAP_ts1[j],ave_SAP_nts1[j],ave_resuti_ts1[j],ave_resuti_nts1[j],ave_rueffi_ts1[j],ave_rueffi_nts1[j] = chapter4_copy.transmission_ul_flexible(N_SFU,N_STA[i],N_RU,duration,gama,BSRP_NTS)
        #OECC-benchmark-A
        ave_delay_ts2[j],ave_delay_nts2[j],ave_jitter_ts2[j],ave_jitter_nts2[j],ave_SAP_ts2[j],ave_SAP_nts2[j],ave_resuti_ts2[j],ave_resuti_nts2[j],ave_rueffi_ts2[j],ave_rueffi_nts2[j]= OECCscheme.transmission(N_SFU,N_STA[i],gama,N_RU2,N_TU_total,CWOmax,CWOmin,duration,tTXOP)  
        #chapter3-benchmark-B
        ave_delay_ts3[j],ave_delay_nts3[j],ave_jitter_ts3[j],ave_jitter_nts3[j],ave_SAP_ts3[j],ave_SAP_nts3[j],ave_resuti_ts3[j],ave_resuti_nts3[j],ave_rueffi_ts3[j],ave_rueffi_nts3[j] = chapter3_copy.transmission(N_SFU,N_STA[i],gama,N_RU2,N_TU_total,CWOmax,CWOmin,duration,tTXOP)
        

    mean_delay_ts1[i] = mean(ave_delay_ts1)
    mean_delay_nts1[i] = mean(ave_delay_nts1)
    mean_jitter_ts1[i] = mean(ave_jitter_ts1)
    mean_jitter_nts1[i] = mean(ave_jitter_nts1)
    mean_SAP_ts1[i] = mean(ave_SAP_ts1)*100
    mean_SAP_nts1[i] = mean(ave_SAP_nts1)*100
    mean_resuti_ts1[i] = mean(ave_resuti_ts1)*100
    mean_resuti_nts1[i] = mean(ave_resuti_nts1)*100
    mean_rueffi_ts1[i] = mean(ave_rueffi_ts1)*100
    mean_rueffi_nts1[i] = mean(ave_rueffi_nts1)*100

    mean_delay_ts2[i] = mean(ave_delay_ts2)/1000
    mean_delay_nts2[i] = mean(ave_delay_nts2)/1000
    mean_jitter_ts2[i] = mean(ave_jitter_ts2)/1000
    mean_jitter_nts2[i] = mean(ave_jitter_nts2)/1000
    mean_SAP_ts2[i] = mean(ave_SAP_ts2)*100
    mean_SAP_nts2[i] = mean(ave_SAP_nts2)*100
    mean_resuti_ts2[i] = mean(ave_resuti_ts2)*100
    mean_resuti_nts2[i] = mean(ave_resuti_nts2)*100
    mean_rueffi_ts2[i] = mean(ave_rueffi_ts2)*100
    mean_rueffi_nts2[i] = mean(ave_rueffi_nts2)*100

    mean_delay_ts3[i] = mean(ave_delay_ts3)/1000
    mean_delay_nts3[i] = mean(ave_delay_nts3)/1000
    mean_jitter_ts3[i] = mean(ave_jitter_ts3)/1000
    mean_jitter_nts3[i] = mean(ave_jitter_nts3)/1000
    mean_SAP_ts3[i] = mean(ave_SAP_ts3)*100
    mean_SAP_nts3[i] = mean(ave_SAP_nts3)*100
    mean_resuti_ts3[i] = mean(ave_resuti_ts3)*100
    mean_resuti_nts3[i] = mean(ave_resuti_nts3)*100
    mean_rueffi_ts3[i] = mean(ave_rueffi_ts3)*100
    mean_rueffi_nts3[i] = mean(ave_rueffi_nts3)*100
# #存入execl
# work_book = xlwt.Workbook(encoding='utf-8')
# sheet_data = work_book.add_sheet('sheet1')
# sheet_data.write(0,0,'delay-TS')
# sheet_data.write(1,0,'Proposed-TS')
# sheet_data.write(1,1,'BenchmarkA-TS')
# sheet_data.write(1,2,'BenchmarkB-TS')

# sheet_data.write(0,4,'delay-NTS')
# sheet_data.write(1,4,'Proposed-NTS')
# sheet_data.write(1,5,'BenchmarkA-NTS')
# sheet_data.write(1,6,'BenchmarkB-NTS')

# sheet_data.write(0,8,'jitter-TS')
# sheet_data.write(1,8,'Proposed-TS')
# sheet_data.write(1,9,'BenchmarkA-TS')
# sheet_data.write(1,10,'BenchmarkB-TS')

# sheet_data.write(0,12,'jitter-NTS')
# sheet_data.write(1,12,'Proposed-NTS')
# sheet_data.write(1,13,'BenchmarkA-NTS')
# sheet_data.write(1,14,'BenchmarkB-NTS')

# sheet_data.write(0,16,'SAP-TS')
# sheet_data.write(1,16,'Proposed-TS')
# sheet_data.write(1,17,'BenchmarkA-TS')
# sheet_data.write(1,18,'BenchmarkB-TS')

# sheet_data.write(0,20,'SAP-NTS')
# sheet_data.write(1,20,'Proposed-NTS')
# sheet_data.write(1,21,'BenchmarkA-NTS')
# sheet_data.write(1,22,'BenchmarkB-NTS')

# sheet_data.write(0,24,'resource uti-TS')
# sheet_data.write(1,24,'Proposed-TS')
# sheet_data.write(1,25,'BenchmarkA-TS')
# sheet_data.write(1,26,'BenchmarkB-TS')

# sheet_data.write(0,28,'resource uti-NTS')
# sheet_data.write(1,28,'Proposed-NTS')
# sheet_data.write(1,29,'BenchmarkA-NTS')
# sheet_data.write(1,30,'BenchmarkB-NTS')

# sheet_data.write(0,32,'RU efficiency-TS')
# sheet_data.write(1,32,'Proposed-TS')
# sheet_data.write(1,33,'BenchmarkA-TS')
# sheet_data.write(1,34,'BenchmarkB-TS')

# sheet_data.write(0,36,'RU efficiency-NTS')
# sheet_data.write(1,36,'Proposed-NTS')
# sheet_data.write(1,37,'BenchmarkA-NTS')
# sheet_data.write(1,38,'BenchmarkB-NTS')

# for i in range (0,len(N_STA)):
#     sheet_data.write(i+2,0,mean_delay_ts1[i])
#     sheet_data.write(i+2,1,mean_delay_ts2[i])
#     sheet_data.write(i+2,2,mean_delay_ts3[i])

#     sheet_data.write(i+2,4,mean_delay_nts1[i])
#     sheet_data.write(i+2,5,mean_delay_nts2[i])
#     sheet_data.write(i+2,6,mean_delay_nts3[i])

#     sheet_data.write(i+2,8,mean_jitter_ts1[i])
#     sheet_data.write(i+2,9,mean_jitter_ts2[i])
#     sheet_data.write(i+2,10,mean_jitter_ts3[i])

#     sheet_data.write(i+2,12,mean_jitter_nts1[i])
#     sheet_data.write(i+2,13,mean_jitter_nts2[i])
#     sheet_data.write(i+2,14,mean_jitter_nts3[i])

#     sheet_data.write(i+2,16,mean_SAP_ts1[i])
#     sheet_data.write(i+2,17,mean_SAP_ts2[i])
#     sheet_data.write(i+2,18,mean_SAP_ts3[i])

#     sheet_data.write(i+2,20,mean_SAP_nts1[i])
#     sheet_data.write(i+2,21,mean_SAP_nts2[i])
#     sheet_data.write(i+2,22,mean_SAP_nts3[i])

#     sheet_data.write(i+2,24,mean_resuti_ts1[i])
#     sheet_data.write(i+2,25,mean_resuti_ts2[i])
#     sheet_data.write(i+2,26,mean_resuti_ts3[i])

#     sheet_data.write(i+2,28,mean_resuti_nts1[i])
#     sheet_data.write(i+2,29,mean_resuti_nts2[i])
#     sheet_data.write(i+2,30,mean_resuti_nts3[i])

#     sheet_data.write(i+2,32,mean_rueffi_ts1[i])
#     sheet_data.write(i+2,33,mean_rueffi_ts2[i])
#     sheet_data.write(i+2,34,mean_rueffi_ts3[i])

#     sheet_data.write(i+2,36,mean_rueffi_nts1[i])
#     sheet_data.write(i+2,37,mean_rueffi_nts2[i])
#     sheet_data.write(i+2,38,mean_rueffi_nts3[i])

# work_book.save('comparison0113.xls')

plt.figure(1)
plt.subplot(2,3,1)
plt.plot(N_STA,mean_delay_ts1,label='proposed-TS',marker='o')           #semilogy
plt.plot(N_STA,mean_delay_nts1,label='proposed-NTS',marker='^')
plt.plot(N_STA,mean_delay_ts2,label='BenchmarkA-TS',marker='s')           #semilogy
plt.plot(N_STA,mean_delay_nts2,label='BenchmarkA-NTS',marker='d')
plt.plot(N_STA,mean_delay_ts3,label='BenchmarkB-TS',marker='x')           #semilogy
plt.plot(N_STA,mean_delay_nts3,label='BenchmarkB-NTS',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('Access Delay (ms)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,2)
plt.plot(N_STA,mean_jitter_ts1,label='proposed-TS',marker='o')           #semilogy
plt.plot(N_STA,mean_jitter_nts1,label='proposed-NTS',marker='^')
plt.plot(N_STA,mean_jitter_ts2,label='BenchmarkA-TS',marker='s')           #semilogy
plt.plot(N_STA,mean_jitter_nts2,label='BenchmarkA-NTS',marker='d')
plt.plot(N_STA,mean_jitter_ts3,label='BenchmarkB-TS',marker='x')           #semilogy
plt.plot(N_STA,mean_jitter_nts3,label='BenchmarkB-NTS',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('Jitter (ms)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,3)
plt.plot(N_STA,mean_SAP_ts1,label='proposed-TS',marker='o')           #semilogy
plt.plot(N_STA,mean_SAP_nts1,label='proposed-NTS',marker='^')
plt.plot(N_STA,mean_SAP_ts2,label='BenchmarkA-TS',marker='s')           #semilogy
plt.plot(N_STA,mean_SAP_nts2,label='BenchmarkA-NTS',marker='d')
plt.plot(N_STA,mean_SAP_ts3,label='BenchmarkB-TS',marker='x')           #semilogy
plt.plot(N_STA,mean_SAP_nts3,label='BenchmarkB-NTS',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('SAP (100%)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

# plt.subplot(2,3,4)
# plt.plot(N_STA,mean_resuti_ts1,label='proposed-TS',marker='o')           #semilogy
# # plt.plot(N_STA,mean_resuti_nts1,label='proposed-NTS',marker='^')
# plt.plot(N_STA,mean_resuti_ts3,label='BenchmarkA-TS',marker='s')           #semilogy
# # plt.plot(N_STA,mean_resuti_nts3,label='BenchmarkA-NTS',marker='d')
# plt.plot(N_STA,mean_resuti_ts2,label='BenchmarkB-TS',marker='x')           #semilogy
# # plt.plot(N_STA,mean_resuti_nts2,label='BenchmarkB-NTS',marker='*')
# plt.xlabel('Number of STAs per SFU')
# plt.ylabel('Resource utilization (100%)')
# plt.xticks(range(0,32,2))
# # plt.yticks(range(0,110,20))
# plt.grid(True)
# plt.legend()

plt.subplot(2,3,5)
plt.plot(N_STA,mean_rueffi_ts1,label='proposed-TS',marker='o')           #semilogy
plt.plot(N_STA,mean_rueffi_nts1,label='proposed-NTS',marker='^')
plt.plot(N_STA,mean_rueffi_ts2,label='BenchmarkA-TS',marker='s')           #semilogy
plt.plot(N_STA,mean_rueffi_nts2,label='BenchmarkA-NTS',marker='d')
plt.plot(N_STA,mean_rueffi_ts3,label='BenchmarkB-TS',marker='x')           #semilogy
plt.plot(N_STA,mean_rueffi_nts3,label='BenchmarkB-NTS',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('RU efficiency (100%)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()
plt.show()





