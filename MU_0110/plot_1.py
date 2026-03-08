from numpy import *
import numpy as np
import matplotlib.pyplot as plt
import chapter4_copy
import xlwt

N_SFU = 4
N_STA = np.arange(2,32,2)
N_RU = 64
duration = 1000000
gama = [0.1,0.2,0.3,0.4]    #房间内TS业务的比例 
BSRP_NTS = [8,16,32,48]

CWOmin = [7,7]
CWOmax = [31,31]
tTXOP = 2000
N_TU_total = 170
N_RU2 = 16

iteration = 20
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

ave_delay_ts4 = np.zeros(iteration)
ave_delay_nts4 = np.zeros(iteration)
ave_jitter_ts4 = np.zeros(iteration)
ave_jitter_nts4 = np.zeros(iteration)
ave_SAP_ts4 = np.zeros(iteration)                 #成功接入概率
ave_SAP_nts4 = np.zeros(iteration)
ave_resuti_ts4 = np.zeros(iteration)              #资源利用率
ave_resuti_nts4 = np.zeros(iteration)
ave_rueffi_ts4 = np.zeros(iteration)              #单个RU利用效率
ave_rueffi_nts4 = np.zeros(iteration)

mean_delay_ts4 = np.zeros(len(N_STA))
mean_delay_nts4 = np.zeros(len(N_STA))
mean_jitter_ts4 = np.zeros(len(N_STA))
mean_jitter_nts4 = np.zeros(len(N_STA))
mean_SAP_ts4 = np.zeros(len(N_STA))
mean_SAP_nts4 = np.zeros(len(N_STA))
mean_resuti_ts4 = np.zeros(len(N_STA))
mean_resuti_nts4 = np.zeros(len(N_STA))
mean_rueffi_ts4 = np.zeros(len(N_STA))
mean_rueffi_nts4 = np.zeros(len(N_STA))

for i in range (len(N_STA)):
    for j in range (iteration):
        ave_delay_ts1[j],ave_delay_nts1[j],ave_jitter_ts1[j],ave_jitter_nts1[j],ave_SAP_ts1[j],ave_SAP_nts1[j],ave_resuti_ts1[j],ave_resuti_nts1[j],ave_rueffi_ts1[j],ave_rueffi_nts1[j] = chapter4_copy.transmission_ul_flexible(N_SFU,N_STA[i],N_RU,duration,gama,BSRP_NTS[0])
        ave_delay_ts2[j],ave_delay_nts2[j],ave_jitter_ts2[j],ave_jitter_nts2[j],ave_SAP_ts2[j],ave_SAP_nts2[j],ave_resuti_ts2[j],ave_resuti_nts2[j],ave_rueffi_ts2[j],ave_rueffi_nts2[j] = chapter4_copy.transmission_ul_flexible(N_SFU,N_STA[i],N_RU,duration,gama,BSRP_NTS[1])
        ave_delay_ts3[j],ave_delay_nts3[j],ave_jitter_ts3[j],ave_jitter_nts3[j],ave_SAP_ts3[j],ave_SAP_nts3[j],ave_resuti_ts3[j],ave_resuti_nts3[j],ave_rueffi_ts3[j],ave_rueffi_nts3[j] = chapter4_copy.transmission_ul_flexible(N_SFU,N_STA[i],N_RU,duration,gama,BSRP_NTS[2])
        ave_delay_ts4[j],ave_delay_nts4[j],ave_jitter_ts4[j],ave_jitter_nts4[j],ave_SAP_ts4[j],ave_SAP_nts4[j],ave_resuti_ts4[j],ave_resuti_nts4[j],ave_rueffi_ts4[j],ave_rueffi_nts4[j] = chapter4_copy.transmission_ul_flexible(N_SFU,N_STA[i],N_RU,duration,gama,BSRP_NTS[3])

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

    mean_delay_ts2[i] = mean(ave_delay_ts2)
    mean_delay_nts2[i] = mean(ave_delay_nts2)
    mean_jitter_ts2[i] = mean(ave_jitter_ts2)
    mean_jitter_nts2[i] = mean(ave_jitter_nts2)
    mean_SAP_ts2[i] = mean(ave_SAP_ts2)*100
    mean_SAP_nts2[i] = mean(ave_SAP_nts2)*100
    mean_resuti_ts2[i] = mean(ave_resuti_ts2)*100
    mean_resuti_nts2[i] = mean(ave_resuti_nts2)*100
    mean_rueffi_ts2[i] = mean(ave_rueffi_ts2)*100
    mean_rueffi_nts2[i] = mean(ave_rueffi_nts2)*100

    mean_delay_ts3[i] = mean(ave_delay_ts3)
    mean_delay_nts3[i] = mean(ave_delay_nts3)
    mean_jitter_ts3[i] = mean(ave_jitter_ts3)
    mean_jitter_nts3[i] = mean(ave_jitter_nts3)
    mean_SAP_ts3[i] = mean(ave_SAP_ts3)*100
    mean_SAP_nts3[i] = mean(ave_SAP_nts3)*100
    mean_resuti_ts3[i] = mean(ave_resuti_ts3)*100
    mean_resuti_nts3[i] = mean(ave_resuti_nts3)*100
    mean_rueffi_ts3[i] = mean(ave_rueffi_ts3)*100
    mean_rueffi_nts3[i] = mean(ave_rueffi_nts3)*100

    mean_delay_ts4[i] = mean(ave_delay_ts4)
    mean_delay_nts4[i] = mean(ave_delay_nts4)
    mean_jitter_ts4[i] = mean(ave_jitter_ts4)
    mean_jitter_nts4[i] = mean(ave_jitter_nts4)
    mean_SAP_ts4[i] = mean(ave_SAP_ts4)*100
    mean_SAP_nts4[i] = mean(ave_SAP_nts4)*100
    mean_resuti_ts4[i] = mean(ave_resuti_ts4)*100
    mean_resuti_nts4[i] = mean(ave_resuti_nts4)*100
    mean_rueffi_ts4[i] = mean(ave_rueffi_ts4)*100
    mean_rueffi_nts4[i] = mean(ave_rueffi_nts4)*100

#存入execl
work_book = xlwt.Workbook(encoding='utf-8')
sheet_data = work_book.add_sheet('sheet1')
sheet_data.write(0,0,'delay-TS')
sheet_data.write(1,0,'8-TS')
sheet_data.write(1,1,'16-TS')
sheet_data.write(1,2,'32-TS')
sheet_data.write(1,3,'48-TS')

sheet_data.write(0,5,'delay-NTS')
sheet_data.write(1,5,'8-NTS')
sheet_data.write(1,6,'16-NTS')
sheet_data.write(1,7,'32-NTS')
sheet_data.write(1,8,'48-NTS')

sheet_data.write(0,10,'jitter-TS')
sheet_data.write(1,10,'8-TS')
sheet_data.write(1,11,'16-TS')
sheet_data.write(1,12,'32-TS')
sheet_data.write(1,13,'48-TS')

sheet_data.write(0,15,'jitter-NTS')
sheet_data.write(1,15,'8-NTS')
sheet_data.write(1,16,'16-NTS')
sheet_data.write(1,17,'32-NTS')
sheet_data.write(1,18,'48-NTS')

sheet_data.write(0,20,'SAP-TS')
sheet_data.write(1,20,'8-TS')
sheet_data.write(1,21,'16-TS')
sheet_data.write(1,22,'32-TS')
sheet_data.write(1,23,'48-TS')

sheet_data.write(0,25,'SAP-NTS')
sheet_data.write(1,25,'8-NTS')
sheet_data.write(1,26,'16-NTS')
sheet_data.write(1,27,'32-NTS')
sheet_data.write(1,28,'48-NTS')



for i in range (0,len(N_STA)):
    sheet_data.write(i+2,0,mean_delay_ts1[i])
    sheet_data.write(i+2,1,mean_delay_ts2[i])
    sheet_data.write(i+2,2,mean_delay_ts3[i])
    sheet_data.write(i+2,3,mean_delay_ts4[i])

    sheet_data.write(i+2,5,mean_delay_nts1[i])
    sheet_data.write(i+2,6,mean_delay_nts2[i])
    sheet_data.write(i+2,7,mean_delay_nts3[i])
    sheet_data.write(i+2,8,mean_delay_nts4[i])

    sheet_data.write(i+2,10,mean_jitter_ts1[i])
    sheet_data.write(i+2,11,mean_jitter_ts2[i])
    sheet_data.write(i+2,12,mean_jitter_ts3[i])
    sheet_data.write(i+2,13,mean_jitter_ts4[i])

    sheet_data.write(i+2,15,mean_jitter_nts1[i])
    sheet_data.write(i+2,16,mean_jitter_nts2[i])
    sheet_data.write(i+2,17,mean_jitter_nts3[i])
    sheet_data.write(i+2,18,mean_jitter_nts4[i])

    sheet_data.write(i+2,20,mean_SAP_ts1[i])
    sheet_data.write(i+2,21,mean_SAP_ts2[i])
    sheet_data.write(i+2,22,mean_SAP_ts3[i])
    sheet_data.write(i+2,23,mean_SAP_ts4[i])

    sheet_data.write(i+2,25,mean_SAP_nts1[i])
    sheet_data.write(i+2,26,mean_SAP_nts2[i])
    sheet_data.write(i+2,27,mean_SAP_nts3[i])
    sheet_data.write(i+2,28,mean_SAP_nts4[i])
work_book.save('a0226.xls')

plt.figure(1)
plt.subplot(2,3,1)
plt.plot(N_STA,mean_delay_ts1,label='TS-8',marker='o')           #semilogy
plt.plot(N_STA,mean_delay_nts1,label='NTS-8',marker='^')
plt.plot(N_STA,mean_delay_ts2,label='TS-16',marker='s')           #semilogy
plt.plot(N_STA,mean_delay_nts2,label='NTS-16',marker='d')
plt.plot(N_STA,mean_delay_ts3,label='TS-32',marker='x')           #semilogy
plt.plot(N_STA,mean_delay_nts3,label='NTS-32',marker='*')
plt.plot(N_STA,mean_delay_ts4,label='TS-48',marker='x')           #semilogy
plt.plot(N_STA,mean_delay_nts4,label='NTS-48',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('Access Delay (ms)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,2)
plt.plot(N_STA,mean_jitter_ts1,label='TS-8',marker='o')           #semilogy
plt.plot(N_STA,mean_jitter_nts1,label='NTS-8',marker='^')
plt.plot(N_STA,mean_jitter_ts2,label='TS-16',marker='s')           #semilogy
plt.plot(N_STA,mean_jitter_nts2,label='NTS-16',marker='d')
plt.plot(N_STA,mean_jitter_ts3,label='TS-32',marker='x')           #semilogy
plt.plot(N_STA,mean_jitter_nts3,label='NTS-32',marker='*')
plt.plot(N_STA,mean_jitter_ts4,label='TS-48',marker='x')           #semilogy
plt.plot(N_STA,mean_jitter_nts4,label='NTS-48',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('Jitter (ms)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,3)
plt.plot(N_STA,mean_SAP_ts1,label='TS-8',marker='o')           #semilogy
plt.plot(N_STA,mean_SAP_nts1,label='NTS-8',marker='^')
plt.plot(N_STA,mean_SAP_ts2,label='TS-16',marker='s')           #semilogy
plt.plot(N_STA,mean_SAP_nts2,label='NTS-16',marker='d')
plt.plot(N_STA,mean_SAP_ts3,label='TS-32',marker='x')           #semilogy
plt.plot(N_STA,mean_SAP_nts3,label='NTS-32',marker='*')
plt.plot(N_STA,mean_SAP_ts4,label='TS-48',marker='x')           #semilogy
plt.plot(N_STA,mean_SAP_nts4,label='NTS-48',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('SAP (100%)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,4)
plt.plot(N_STA,mean_resuti_ts1,label='TS-8',marker='o')           #semilogy
plt.plot(N_STA,mean_resuti_nts1,label='NTS-8',marker='^')
plt.plot(N_STA,mean_resuti_ts2,label='TS-16',marker='s')           #semilogy
plt.plot(N_STA,mean_resuti_nts2,label='NTS-16',marker='d')
plt.plot(N_STA,mean_resuti_ts3,label='TS-32',marker='x')           #semilogy
plt.plot(N_STA,mean_resuti_nts3,label='NTS-32',marker='*')
plt.plot(N_STA,mean_resuti_ts4,label='TS-48',marker='x')           #semilogy
plt.plot(N_STA,mean_resuti_nts4,label='NTS-48',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('Resource utilization (100%)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()

plt.subplot(2,3,5)
plt.plot(N_STA,mean_rueffi_ts1,label='TS-8',marker='o')           #semilogy
plt.plot(N_STA,mean_rueffi_nts1,label='NTS-8',marker='^')
plt.plot(N_STA,mean_rueffi_ts2,label='TS-16',marker='s')           #semilogy
plt.plot(N_STA,mean_rueffi_nts2,label='NTS-16',marker='d')
plt.plot(N_STA,mean_rueffi_ts3,label='TS-32',marker='x')           #semilogy
plt.plot(N_STA,mean_rueffi_nts3,label='NTS-32',marker='*')
plt.plot(N_STA,mean_rueffi_ts4,label='TS-48',marker='x')           #semilogy
plt.plot(N_STA,mean_rueffi_nts4,label='NTS-48',marker='*')
plt.xlabel('Number of STAs per SFU')
plt.ylabel('RU efficiency (100%)')
plt.xticks(range(0,32,2))
# plt.yticks(range(0,110,20))
plt.grid(True)
plt.legend()
plt.show()





