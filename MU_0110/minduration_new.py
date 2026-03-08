import pulp
import numpy as np

def minimize_trans(N,Nc,R,a,slot):
    prob = pulp.LpProblem("Minimize_Transmission_Time",pulp.LpMinimize)
    A = pulp.LpVariable.dicts("A",(range(N),range(Nc)),lowBound = 0,cat = 'Integer')
    T = pulp.LpVariable("T",lowBound=0,cat='Continuous')
    prob += T,"Total_Transmission_Time"

    #添加约束条件
    for i in range (N):
        trans_data = pulp.lpSum([A[i][t]*a*slot for t in range(Nc)])
        prob += trans_data>=R[i],f"User_{i}_data_completon"
    
    for t in range (Nc):
        prob += pulp.lpSum([A[i][t] for i in range(N)]) <=Nc,f"Subcarrier_limit_at_time_{t}"

    for i in range (N):
        trans_time = pulp.lpSum([slot*A[i][t] for t in range(Nc)])
        prob += T>= trans_time,f"Max_Timer_User{i}"
    
    prob.solve()
    optimal_T = pulp.value(T)

    allocation = [[pulp.value(A[i][t]) for t in range(Nc)] for i in range (N)]
    allocation_per_slot = []
    for t in range (Nc):
        slot_allocation = []
        for i in range (N):
            if pulp.value(A[i][t])>0:
                slot_allocation.append((i,int(pulp.value(A[i][t]))))
        allocation_per_slot.append(slot_allocation)
    return optimal_T,allocation,allocation_per_slot
# # 示例输入
N = 4       #用户个数
Nc = 1024      #子载波总数
a = 9.76  # 示例常数a
R = np.array([73440, 85680, 36720, 61200])    #用户需求资源数
slot = 40

# # 执行优化
optimal_T,allocation,allocation_per_slot = minimize_trans(N,Nc,R,a,slot)
print("最优子载波分配:", optimal_T)
# print("最小传输时间 T:", min_T)