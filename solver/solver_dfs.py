from game.moves import generate_moves, apply_move
import sys

sys.setrecursionlimit(200000)

def score_move(move, state):
    m_type = move[0]
    if m_type == 'draw': #Draw jika tidak ada jalan lain
        return 0 
    
    removals = move[1]
    
    #Prioritas tinggi hapus king
    if len(removals) == 1: 
        return 1000 
    
    #Cek jumlah kartu piramida
    p_count = sum(1 for x in removals if x[0] == 'p')
    
    if p_count == 2: return 500 #Hapus 2 kartu piramida
    if p_count == 1: return 100 #Hapus 1 kartu piramida + Slot Draw
    
    return 10 #Hapus king di waste

def dfs_recursive(start_state, max_depth=2000, max_nodes=3000000):
    visited = set()
    path = []
    stats = {'nodes': 0}
    result = {'path': None}

    def dfs(state, depth):
        if result['path'] is not None: return True

        stats['nodes'] += 1
        
        if stats['nodes'] % 50000 == 0:
            print(f"[DFS] Nodes: {stats['nodes']}, Depth: {depth}")
        
        if stats['nodes'] > max_nodes or depth > max_depth:
            return False

        if state.is_goal():
            result['path'] = list(path)
            return True

        if state in visited: return False
        visited.add(state)

        moves = generate_moves(state)
        
        moves.sort(key=lambda m: score_move(m, state), reverse=True)

        for mv in moves:
            child = apply_move(state, mv)
            if child is None: continue
            
            path.append(mv)
            if dfs(child, depth + 1): return True
            path.pop()

        return False

    print(f"Starting DFS... Limit: {max_nodes}")
    dfs(start_state, 0)
    
    return result['path'], stats['nodes']

def solve_with_dfs(state, depth_limit=2000, node_limit=3000000):
    return dfs_recursive(state, max_depth=depth_limit, max_nodes=node_limit)