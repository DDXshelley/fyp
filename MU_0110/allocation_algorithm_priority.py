import math
import numpy as np

def allocation(RU_TS, RU_NTS,demands,Set_TS):
    # Step 1: 计算总需求和各需求比例
    demands_ts = 0
    demands_nts = 0
    for i in range (len(demands)):
        if i in Set_TS:
            demands_ts += demands[i]
        else:
            demands_nts += demands[i]


    targets = np.zeros(len(demands),dtype=int)
    diff = np.zeros(len(demands),dtype=int)
    
    for i in range (len(demands)):
        if demands[i] > 0:
            if i in Set_TS:
                targets[i] = int(max(math.floor(demands[i]/demands_ts * RU_TS),1))        #预期分配的目标值
            else:
                targets[i] = int(max(math.floor(demands[i]/demands_nts * RU_NTS),1))

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

    sum_alloc = sum(allocations)
    for i in range (len(demands)):
        diff[i] = targets[i] - allocations[i]

    #重新排分配的顺序，先TS，后NTS
    # 将数组按照组TS的索引和组NTS的索引分开
    group_ts = [(diff[i],i) for i in Set_TS]
    group_nts = [(diff[i],i) for i in range(len(diff)) if i not in Set_TS]

    # 对组A和组B进行降序排序
    group_ts_sorted = sorted(group_ts, key=lambda x: x[0], reverse=True)
    group_nts_sorted = sorted(group_nts, key=lambda x: x[0], reverse=True)

    #合并
    sorted_diff_indices = group_ts_sorted + group_nts_sorted

    #获取原索引
    sorted_diff = [item[0] for item in sorted_diff_indices]
    original_indices = [item[1] for item in sorted_diff_indices]


    # Step 3: 若 sum_alloc < total_num，则优先满足优先级高的个体
    # 按需分配增量，直到 sum_alloc == total_num
    if sum_alloc < (RU_TS+RU_NTS):
        for i in original_indices:
            if sum_alloc >= (RU_TS+RU_NTS):
                break
            next_power = allocations[i] * 2
            if sum_alloc + next_power - allocations[i] <= (RU_TS+RU_NTS):  # 检查是否超出总量
                sum_alloc += next_power - allocations[i]
                allocations[i] = next_power
    for i in range (len(demands)):
        allocations[i] = min(allocations[i],32)
    return allocations


# # # # 示例使用
# RU_TS = 10
# RU_NTS = 16
# demands = [3,1,2,4,5,6,7,8,5]
# Set_TS = [0,1,7]
# allocation = allocation(RU_TS, RU_NTS,demands,Set_TS)
# print("最终分配:", result)
# print("速率",rate)



