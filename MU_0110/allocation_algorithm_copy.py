import math
import numpy as np

def allocation(RU_TS, RU_NTS,demands,Set_TS):
    # Step 1: 计算总需求和各需求比例
    total_demand = sum(demands)               #demand中有0
    targets = np.zeros(len(demands))
    ratios = [d / total_demand for d in demands]
    for i in range (len(demands)):
        if demands[i] > 0:
            targets[i] = max(math.floor(ratios[i] * (RU_TS+RU_NTS)),1)

    # Step 2: 初始分配为小于等于 target 的最大 2 的幂次
    def largest_power_of_two(x):
        if x>0:
            power = 1
            while power * 2 <= x:
                power *= 2
            return power
        elif x== 0:
            power = 0
            return power

    allocations = [largest_power_of_two(target) for target in targets]
    for i in range (len(demands)):
        allocations[i] = min(allocations[i],32)
    sum_alloc = sum(allocations)

    # Step 3: 若 sum_alloc < total_num，则优先满足需求高的个体
    # 按需分配增量，直到 sum_alloc == total_num
    if sum_alloc < (RU_TS+RU_NTS):
        demand_with_indices = sorted(enumerate(demands), key=lambda x: -x[1])  # 按需求从大到小排序
        for i, _ in demand_with_indices:
            if sum_alloc >= (RU_TS+RU_NTS):
                break
            next_power = allocations[i] * 2
            if sum_alloc + next_power - allocations[i] <= (RU_TS+RU_NTS) and allocations[i]<32:  # 检查是否超出总量
                sum_alloc += next_power - allocations[i]
                allocations[i] = next_power

    # # Step 4: 返回最终分配结果
    # #计算RU的速率
    # rate = np.zeros(len(allocations))
    # for i in range(len(allocations)):
    #     rate[i] = 11.1*allocations[i]
    return allocations

def request_RU_size(number):
    i = 1
    while (i < 6):
        if 2**i <= number:
            i += 1
        else:
            break
    a = 2**(i-1)
    return a

# # # 示例使用
# total_apples = 64
# demands = [2,30,1,28,3,4,1,29,2]
# Set_TS = [1,3,7]
# result,rate = allocation(total_apples, demands)
# print("最终分配:", result)
# print("速率",rate)



