import time
import random
import copy
from game.pyramid_board import new_deal
from solver.solver_dfs import solve_with_dfs 
from solver.solver_bfs import solve_with_bfs 

def generate_fixed_deals(n=10, seed=42):
    #Menghasilkan 10 deal yang persis setiap kali dijalankan Tujuannya agar perbandingan DFS dan BFS adil
    saved_state = random.getstate() #simpan state random saat ini agar tidak merusak game utama
    
    random.seed(seed) # Kunci seed
    deals = []
    print(f"--- Generating {n} Fixed Deals (Seed {seed}) ---")
    for i in range(n):
        d = new_deal()
        deals.append(d)
    
    random.setstate(saved_state)
    return deals

    #Menjalankan eksperimen pada 10 deal tetap
def run_experiment(max_nodes, progress_callback=None):
    deals = generate_fixed_deals(10)
    results = {
        'DFS': {'total_time': 0, 'total_nodes': 0, 'solved': 0, 'cutoff': 0},
        'BFS': {'total_time': 0, 'total_nodes': 0, 'solved': 0, 'cutoff': 0}
    }
    
    total_deals = len(deals)
    
    print(f"\n=== MULAI EKSPERIMEN (MAX_NODE = {max_nodes}) ===")

    for i, deal in enumerate(deals):
        if progress_callback:
            progress_callback(f"Deal {i+1}/{total_deals}...")

        #Uji DFS rekursif
        state_dfs = copy.deepcopy(deal)
        start = time.time()
        sol_dfs, nodes_dfs = solve_with_dfs(state_dfs, node_limit=max_nodes) 
        dur_dfs = time.time() - start
        
        #Catat Data DFS rekursif
        results['DFS']['total_time'] += dur_dfs
        results['DFS']['total_nodes'] += nodes_dfs
        if sol_dfs: results['DFS']['solved'] += 1
        else: results['DFS']['cutoff'] += 1

        #Uji BFS Iteratif
        state_bfs = copy.deepcopy(deal)
        start = time.time()
        sol_bfs, nodes_bfs = solve_with_bfs(state_bfs, node_limit=max_nodes)
        dur_bfs = time.time() - start
        
        results['BFS']['total_time'] += dur_bfs
        results['BFS']['total_nodes'] += nodes_bfs
        if sol_bfs: results['BFS']['solved'] += 1
        else: results['BFS']['cutoff'] += 1
        print(f"Deal {i+1}: DFS({nodes_dfs} nodes) | BFS({nodes_bfs} nodes)")

    #Hitung Rata-rata
    summary = {}
    for algo in ['DFS', 'BFS']:
        summary[algo] = {
            'avg_time': results[algo]['total_time'] / total_deals,
            'avg_nodes': int(results[algo]['total_nodes'] / total_deals),
            'solved_count': results[algo]['solved'],
            'cutoff_count': results[algo]['cutoff']
        }
        
    return summary