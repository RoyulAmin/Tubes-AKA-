import copy
import random
from game.pyramid_board import new_deal
from game.moves import generate_moves, apply_move

    #Mencari Winning Deal menggunakan metode Monte Carlo (Random Playout)
def get_winning_deal(max_attempts=200, difficulty_limit=None):
    print("Mencari Winning Deal (Metode Monte Carlo)")
    
    for i in range(max_attempts):
        candidate_state = new_deal()
        is_winnable = False
        #coba jalanin random playout sebanyak 50 kali
        for _ in range(50): 
            if attempt_random_solve(candidate_state):
                is_winnable = True
                break
        
        if is_winnable:
            print(f"Winning Deal ditemukan pada percobaan deal ke-{i+1}!")
            return candidate_state
            
    print("Gagal menemukan Winning Deal (Monte Carlo), kembali ke Random Deal biasa.")
    return new_deal()

def attempt_random_solve(start_state):
    state = copy.deepcopy(start_state)
    
    steps = 0
    max_steps = 150
    
    while steps < max_steps:
        if state.is_goal():
            return True
            
        moves = generate_moves(state)
        if not moves:
            return False # Stuck (tidak ada gerakan yang bisa dilakukan)
            
        #Logika Pemilihan Gerakan 
        selected_move = None
        
        #Prioritas Hapus King
        for m in moves:
            if m[0] == 'remove' and len(m[1]) == 1: #Cek jika remove 1 kartu(King)
                selected_move = m
                break
        
        #Jika tidak ada king ambil acak
        if not selected_move:
            selected_move = random.choice(moves)
            
        state = apply_move(state, selected_move)
        steps += 1
        
    return False