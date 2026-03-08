import numpy as np
from scipy.optimize import minimize

# 定义目标函数：最大传输时间 T
def objective(m_flat, req_size, N_SFU, N_STA, a):
    m = m_flat.reshape((N_SFU, N_STA))
    t = np.divide(req_size, np.maximum(m * a, 1e-6))  # 加入常数 a，防止除以0
    T1 = np.max(t, axis=1)  # 每个设备的最大传输时间
    return np.max(T1)  # 返回所有设备中的最大传输时间

# 约束条件：子载波总数不超过N_sub
def constraint_total_m(m_flat, N_sub):
    return N_sub - np.sum(m_flat)

# 约束条件：每个用户分配的子载波数量至少为1（对于请求资源大于0的用户）
def constraint_min_m(m_flat, req_size):
    m = m_flat.reshape(req_size.shape)
    return m - (req_size > 0).astype(int)

def optimize_subcarriers(N_SFU, N_STA, N_sub, req_size, a):
    # 初始分配均匀分配
    initial_m = np.maximum(np.ones((N_SFU, N_STA)), N_sub // (N_SFU * N_STA) * np.ones((N_SFU, N_STA)))  # 初始值为均匀分配
    initial_m = initial_m.flatten()  # 将矩阵展平为向量

    # 设置约束条件
    constraints = [
        {'type': 'ineq', 'fun': constraint_total_m, 'args': (N_sub,)},  # 子载波总数不超过N_sub
        {'type': 'ineq', 'fun': lambda m_flat: constraint_min_m(m_flat, req_size).flatten()}  # 每个用户的最小分配
    ]
    
    min_result = None
    min_T = float('inf')

    def callback(xk):
        nonlocal min_result, min_T
        T = objective(xk, req_size, N_SFU, N_STA, a)
        if T < min_T:
            min_T = T
            min_result = xk

    try:
        # 进行优化，求解最优分配方案
        result = minimize(objective, initial_m, args=(req_size, N_SFU, N_STA, a), constraints=constraints, method='SLSQP', bounds=[(0, N_sub)] * (N_SFU * N_STA), callback=callback)
        
        if result.success:
            # 返回最优的子载波分配方案和最小的T值
            optimal_m = np.round(result.x).reshape((N_SFU, N_STA)).astype(int)
            min_T = objective(optimal_m.flatten(), req_size, N_SFU, N_STA, a)
            return optimal_m, min_T
        else:
            print("警告：优化失败，迭代次数达到上限。返回最小的迭代结果...")
            optimal_m = np.round(min_result).reshape((N_SFU, N_STA)).astype(int)
            return optimal_m, min_T
    
    except ValueError as e:
        raise e

# # 示例输入
# N_SFU = 4  # 设备数量
# N_STA = 20  # 每个设备支持的用户数量
# N_sub = 1024  # 总共的子载波数量

# # 初始化资源请求数量为0的矩阵
# req_size = np.zeros((N_SFU, N_STA))

# # 手动设置资源请求数量
# req_size[0, 0] = 10
# req_size[0, 1] = 20
# req_size[1, 2] = 5
# req_size[1, 0] = 15
# req_size[1, 1] = 25
# req_size[2, 3] = 30
# req_size[2, 4] = 40
# req_size[3, 5] = 50

# a = 2.5  # 常数a

# # 执行优化
# m_optimal, min_T = optimize_subcarriers(N_SFU, N_STA, N_sub, req_size, a)
# print("最优子载波分配:\n", m_optimal)
# print("最小传输时间 T:", min_T)