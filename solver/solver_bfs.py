from collections import deque
from game.moves import generate_moves, apply_move
import sys

def reconstruct_path(came_from, current_state):
    path = []
    while current_state in came_from:
        parent, move = came_from[current_state]
        if move is None: break
        path.append(move)
        current_state = parent
    path.reverse()
    return path

def bfs_iterative(start_state, max_nodes=2000000): #nodes 2jt
    queue = deque()
    queue.append(start_state)
    
    came_from = {start_state: (None, None)}
    
    nodes_visited = 0
    
    print(f"Starting BFS (Unlimited Memory Mode)... Max Nodes Limit: {max_nodes}")

    while len(queue) > 0:
        current_state = queue.popleft()
        nodes_visited += 1
        
        #Print Log progress
        if nodes_visited % 50000 == 0:
            print(f"[BFS] Nodes: {nodes_visited}, Q: {len(queue)}, Saved States: {len(came_from)}")
            
        #Cek limit iterasi
        if nodes_visited > max_nodes:
            print(f"!!! BFS ITERATION LIMIT REACHED ({nodes_visited}) !!!")
            return None, nodes_visited

        if current_state.is_goal():
            print(f"Solusi BFS ditemukan! Nodes visited: {nodes_visited}")
            return reconstruct_path(came_from, current_state), nodes_visited

        possible_moves = generate_moves(current_state)
        
        for move in possible_moves:
            next_state = apply_move(current_state, move)
            if next_state is None: continue
                
            if next_state not in came_from:  
                came_from[next_state] = (current_state, move)
                queue.append(next_state)

    print(f"Queue kosong. Tidak ada solusi. Nodes: {nodes_visited}")
    return None, nodes_visited

def solve_with_bfs(state, node_limit=2000000):
    return bfs_iterative(state, max_nodes=node_limit)