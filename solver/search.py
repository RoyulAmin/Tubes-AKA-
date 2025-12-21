from .solver_dfs import solve_with_dfs

def find_solution(state, depth_limit=1000, node_limit=500000):
    return solve_with_dfs(state, depth_limit, node_limit)