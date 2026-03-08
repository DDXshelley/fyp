from scipy.optimize import minimize
import numpy as np

# 定义目标函数：最大传输时间
def objective(m, x, a):
    # 确保 m 中的值至少为一个非常小的正数以防止除以零
    m = np.maximum(m, 1e-6)
    t = np.divide(x, m * a)  # 加入常数 a
    return np.max(t)  # 返回最大传输时间

# 约束条件：子载波总数为M
def constraint_total_m(m, M):
    return M - np.sum(m)

# 约束条件：每个用户分配的子载波数量至少为1（对于请求资源大于0的用户）
def constraint_min_m(m, x):
    return m - (x > 0).astype(int)

def generate_fallback_solution(x, M, a):
    # 生成一个简单的备选方案：均匀分配子载波
    non_zero_users = (x > 0).sum()  # 统计请求资源大于0的用户数
    m_fallback = np.zeros_like(x)
    
    if non_zero_users > 0:
        m_fallback[x > 0] = M // non_zero_users  # 初始均匀分配子载波
        remaining_m = M - np.sum(m_fallback)
        
        # 将剩余的子载波分配给请求资源最多的用户
        for i in np.argsort(-x):
            if remaining_m == 0:
                break
            if x[i] > 0:
                m_fallback[i] += 1
                remaining_m -= 1
    
    min_T_fallback = objective(m_fallback, x, a)
    return m_fallback, min_T_fallback

def optimize_subcarriers(N, M, x, a):
    # 初始分配均匀分配
    initial_m = np.maximum(np.ones(N), M // N * np.ones(N))  # 初始值为均匀分配

    # 设置约束条件
    constraints = [
        {'type': 'eq', 'fun': constraint_total_m, 'args': (M,)},  # 子载波总数不超过M
        {'type': 'ineq', 'fun': constraint_min_m, 'args': (x,)}   # 每个用户的最小分配
    ]
    
    try:
        # 进行优化，求解最优分配方案
        result = minimize(objective, initial_m, args=(x, a), constraints=constraints, method='SLSQP', bounds=[(0, M)] * N)
        
        if result.success:
            # 返回最优的子载波分配方案和最小的T值
            optimal_m = np.round(result.x).astype(int)
            min_T = objective(optimal_m, x, a)
            return optimal_m, min_T
        else:
            raise ValueError(result.message)
    
    except ValueError as e:
        if "Iteration limit reached" in str(e):
            print("警告：优化失败，迭代次数达到上限。生成备选方案...")
            return generate_fallback_solution(x, M, a)
        else:
            raise e

# 示例输入
N = 4       #用户个数
M = 1024      #子载波总数
a = 9.76  # 示例常数a
x = np.array([73440, 85680, 36720, 61200])    #用户需求资源数

# 执行优化
m_optimal, min_T = optimize_subcarriers(N, M, x, a)
print("最优子载波分配:", m_optimal)
print("最小传输时间 T:", min_T)