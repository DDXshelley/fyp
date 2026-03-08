import numpy as np
import random

def EDCA_1(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list):                    #考虑AIFS,不考虑虚拟碰撞,考虑AP也竞争的情况
#进行指数退避过程
    SIFS = 16
    slot = 9
    flag = 3
    contention = np.zeros(Total_num)
    Set_success = Total_num + 1
    timer = SIFS + 2 * slot

    if sum(tosend) != 0:                #有数据要发
        while True:
            if 0 in BEB_count:
                for i in range (Total_num):
                    if BEB_count[i] == 0:
                        contention[i] = 1        
                break
            else:               
                for i in range (Total_num):
                    if tosend[i] == 1:
                        if timer > AIFS[i]:
                            BEB_count[i]-= 1
                timer += slot
        
        #找出哪些STA的计数值减到0，判断有几个STA同时减到0
        if sum(contention) == 1:            #只有一个STA的AC退避到0
            if contention[Total_num-1] == 1:
                flag = 0                    #AP竞争成功 flag为0
                CW[Total_num-1] = CWmin_list[Total_num-1]
                BEB_count[Total_num-1] = random.randint(1,CW[Total_num-1]) 
            else:
                flag = 1                    #STA竞争成功，flag为1
                for i in range (Total_num-1):
                    if contention[i] == 1:
                        Set_success = i 
                        CW[i] = CWmin_list[i]              
                        BEB_count[i] = random.randint(1,CW[i])                

        elif sum(contention) >= 2:                                    #有多个STA同时退避到0
            #判断外部是否发生碰撞
            for i in range (Total_num):
                if contention[i] == 1:
                    CW[i] = (CW[i] + 1) * 2 - 1
                    if CW[i] > CWmax_list[i]:                                                    
                        CW[i] = CWmin_list[i]                                
                    BEB_count[i] = random.randint(1,CW[i]) 
            flag = 2                                               #碰撞               

    return flag, Set_success,CW,BEB_count,timer


def EDCA_2(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list):                    #不考虑AP竞争的情况
#进行指数退避过程
    SIFS = 16
    slot = 9
    flag = 3
    contention = np.zeros(Total_num)
    Set_success = Total_num + 1
    timer = SIFS + 2 * slot

    if sum(tosend) != 0:                #有数据要发
        while True:
            if 0 in BEB_count:
                for i in range (Total_num):
                    if BEB_count[i] == 0:
                        contention[i] = 1        
                break
            else:               
                for i in range (Total_num):
                    if tosend[i] == 1:
                        if timer > AIFS[i]:
                            BEB_count[i]-= 1
                timer += slot
        
        #找出哪些STA的计数值减到0，判断有几个STA同时减到0
        if sum(contention) == 1:            #只有一个STA的AC退避到0
            flag = 0

            for i in range (Total_num):
                if contention[i] == 1:
                    Set_success = i 
                    CW[i] = CWmin_list[i]              
                    BEB_count[i] = random.randint(1,CW[i])                

        elif sum(contention) >= 2:                                    #有多个STA同时退避到0
            #判断外部是否发生碰撞
            for i in range (Total_num):
                if contention[i] == 1:
                    CW[i] = (CW[i] + 1) * 2 - 1
                    if CW[i] > CWmax_list[i]:                                                    
                        CW[i] = CWmin_list[i]                                
                        BEB_count[i] = random.randint(1,CW[i]) 
                flag = 2                                               #碰撞               
        else:
            flag = 3
    return flag, Set_success,CW,BEB_count,timer

def EDCA_3(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list,timer_sta,timer_ap):                    #考虑AIFS,不考虑虚拟碰撞,考虑AP也竞争的情况
#进行指数退避过程
    SIFS = 16
    slot = 9
    flag = 3
    contention = np.zeros(Total_num)
    Set_success = Total_num + 1
    timer = SIFS + 2 * slot
    timer_sta += SIFS + 2 * slot
    mark_ap = 0

    if sum(tosend) != 0:                #有数据要发
        while True:
            if 0 in BEB_count:
                for i in range (Total_num):
                    if BEB_count[i] == 0:
                        contention[i] = 1        
                break
            else:
                if mark_ap == 1:                   #AP加入退避
                    for i in range (Total_num):
                        if tosend[i] == 1:
                            if timer > AIFS[i]:
                                BEB_count[i]-= 1
                    timer += slot
                    timer_sta += slot
                    timer_ap += slot
                else:                              #AP未加入退避
                    for i in range (Total_num-1):
                        if tosend[i] == 1:
                            if timer > AIFS[i]:
                                BEB_count[i]-= 1
                    timer += slot
                    timer_sta += slot
                    if timer_sta >= timer_ap:
                        mark_ap = 1
                        timer_ap += slot

        
        #找出哪些STA的计数值减到0，判断有几个STA同时减到0
        if sum(contention) == 1:            #只有一个STA的AC退避到0
            if contention[Total_num-1] == 1:
                flag = 0                    #AP竞争成功 flag为0
                CW[Total_num-1] = CWmin_list[Total_num-1]
                BEB_count[Total_num-1] = random.randint(1,CW[Total_num-1]) 
            else:
                flag = 1                    #STA竞争成功，flag为1
                for i in range (Total_num-1):
                    if contention[i] == 1:
                        Set_success = i 
                        CW[i] = CWmin_list[i]              
                        BEB_count[i] = random.randint(1,CW[i])                

        elif sum(contention) >= 2:                                    #有多个STA同时退避到0
            #判断外部是否发生碰撞
            for i in range (Total_num):
                if contention[i] == 1:
                    CW[i] = (CW[i] + 1) * 2 - 1
                    if CW[i] > CWmax_list[i]:                                                    
                        CW[i] = CWmin_list[i]                                
                    BEB_count[i] = random.randint(1,CW[i]) 
            flag = 2                                               #碰撞               

    return flag, Set_success,CW,BEB_count,timer,timer_sta,timer_ap,mark_ap

def EDCA_cycle(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list):                    #考虑AIFS,不考虑虚拟碰撞,考虑AP也竞争的情况
#进行指数退避过程

    def cycle(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list):
        SIFS = 16
        slot = 9
        contention = np.zeros(Total_num)
        Set_success = Total_num + 1
        timer = SIFS + 2 * slot
        while True:
            if 0 in BEB_count:
                for i in range (Total_num):
                    if tosend[i] != 0:
                        if BEB_count[i] == 0:
                            contention[i] = 1        
                break
            else:               
                for i in range (Total_num):
                    if tosend[i] == 1:
                        if timer > AIFS[i]:
                            BEB_count[i]-= 1
                timer += slot
        
        #找出哪些STA的计数值减到0，判断有几个STA同时减到0
        if sum(contention) == 1:            #只有一个STA的AC退避到0
            for i in range (Total_num):
                if contention[i] == 1:
                    Set_success = i 
                    CW[i] = CWmin_list[i]              
                    BEB_count[i] = random.randint(1,CW[i])                

        elif sum(contention) >= 2:                                    #有多个STA同时退避到0
            #判断外部是否发生碰撞
            for i in range (Total_num):
                if contention[i] == 1:
                    CW[i] = (CW[i] + 1) * 2 - 1
                    if CW[i] > CWmax_list[i]:                                                    
                        CW[i] = CWmin_list[i]                                
                    BEB_count[i] = random.randint(1,CW[i])                                         #碰撞
        return CW,BEB_count,Set_success

    if sum(tosend) != 0:                #有数据要发
        CW,BEB_count,Set_success = cycle(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list)
        while True:
            if Set_success != Total_num + 1:
                break
            else:
                CW,BEB_count,Set_success = cycle(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list)
                               

    return Set_success

# Total_num = 4
# tosend=[0,0,0,1]
# CW = [15,15,7,7]
# BEB_count =[4,4,2,2]
# AIFS=[3,3,3,3]
# CWmax_list=[1023,1023,1023,1023]
# CWmin_list=[7,7,7,7]
# Set_success = EDCA_cycle(Total_num,tosend,CW,BEB_count,AIFS,CWmax_list,CWmin_list)
# print(Set_success)