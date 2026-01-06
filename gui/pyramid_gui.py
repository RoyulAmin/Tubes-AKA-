import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import copy

#IMPORT FILE GAME 
from game.pyramid_board import new_deal
from game.moves import generate_moves, apply_move
from solver.solver_dfs import solve_with_dfs 
from solver.solver_bfs import solve_with_bfs 
from game.deck import card_str

#IMPORT FILE EKSPERIMEN/ANALYSIS 
try:
    from experiment.benchmark import run_experiment
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False
    print("Warning: experiment/benchmark.py belum dibuat. Fitur Benchmark non-aktif.")

CARD_W = 64
CARD_H = 40

class PyramidGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyramid Solitaire Pro - Final Project Demo")
        
        # State Management
        self.state = new_deal()
        self.initial_state = copy.deepcopy(self.state) 
        
        self.selected = [] 
        self.playing = False
        self.current_solution = None 
        
        self.perf_data = {
            'DFS': {'status': '-', 'waktu': 0, 'nodes': 0, 'langkah': 0},
            'BFS': {'status': '-', 'waktu': 0, 'nodes': 0, 'langkah': 0}
        }

        #UI CONTROL FRAME 
        ctrl = tk.Frame(root)
        ctrl.pack(pady=6)
        
        #GAME BUTTONS
        tk.Button(ctrl, text="Random Deal", command=self.new_deal, bg='#dddddd').pack(side='left', padx=2)
        tk.Button(ctrl, text="Reset", command=self.reset_board, bg='#ffcccc').pack(side='left', padx=2)
        tk.Button(ctrl, text="Draw", command=self.draw, bg='#fffacd').pack(side='left', padx=2)
        tk.Frame(ctrl, width=10).pack(side='left') # Spasi
        
        #SOLVER BUTTONS
        tk.Button(ctrl, text="Solve DFS", command=self.run_dfs, bg='#e6e6fa').pack(side='left', padx=2)
        tk.Button(ctrl, text="Solve BFS", command=self.run_bfs, bg='#e6fae6').pack(side='left', padx=2)
        
        self.btn_autoplay = tk.Button(ctrl, text="Auto-Play", command=self.autoplay, state=tk.DISABLED, bg='gold')
        self.btn_autoplay.pack(side='left', padx=2)
        tk.Frame(ctrl, width=10).pack(side='left') # Spasi
        
        #ANALYSIS
        state_bm = tk.NORMAL if BENCHMARK_AVAILABLE else tk.DISABLED
        self.btn_bench = tk.Button(ctrl, text="Analysis", command=self.start_benchmark, bg='orange', fg='white', font=("Arial", 9, "bold"), state=state_bm)
        self.btn_bench.pack(side='left', padx=5)

        # Canvas Area
        self.canvas = tk.Canvas(root, width=860, height=600, bg='#2b2b2b')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.draw_board()

    #LOGIKA BENCHMARK  
    def start_benchmark(self):
        if self.playing: return
        max_node_input = simpledialog.askinteger("Benchmark Parameter", "Masukkan Batas MAX_NODE (Ukuran Input):\n(Rentang 1000-10000000)",parent=self.root, minvalue=1000, maxvalue=10000000)
        if not max_node_input: return 
        
        def run_bench_thread():
            self.root.config(cursor="wait")
            self.btn_bench.config(state=tk.DISABLED, text="Running...")
            
            def update_progress(msg): 
                self.btn_bench.config(text=msg)

            summary = run_experiment(max_nodes=max_node_input, progress_callback=update_progress)            
            self.root.after(0, lambda: self.show_benchmark_results(summary, max_node_input)) #Tampilkan Hasil

        threading.Thread(target=run_bench_thread, daemon=True).start()

    def show_benchmark_results(self, summary, max_nodes):
        self.root.config(cursor="")
        self.btn_bench.config(state=tk.NORMAL, text="Analysis")
        
        d, b = summary['DFS'], summary['BFS']
        
        txt = (f"HASIL EKSPERIMEN (Rata-rata dari 10 Deal)\n" f"Input Size (Max Node): {max_nodes:,}\n{'='*50}\n" f"DFS (Rekursif):\n" f" - Waktu Rata-rata : {d['avg_time']:.4f}s\n"f" - Node Rata-rata  : {d['avg_nodes']:,}\n"f" - Status          : {d['solved_count']} Solved, {d['cutoff_count']} Cutoff\n\n" f"BFS (Iteratif):\n" f" - Waktu Rata-rata : {b['avg_time']:.4f}s\n" f" - Node Rata-rata  : {b['avg_nodes']:,}\n" f" - Status          : {b['solved_count']} Solved, {b['cutoff_count']} Cutoff")
        top = tk.Toplevel(self.root)
        top.title(f"Benchmark Result - N={max_nodes}")
        tk.Label(top, text=txt, font=("Consolas", 11), justify="left", padx=20, pady=20, bg="#f0f0f0").pack()

    def apply_new_deal(self, new_state):
        self.state = new_state
        self.initial_state = copy.deepcopy(self.state)
        self.selected.clear()
        self.current_solution = None
        self.btn_autoplay.config(state=tk.DISABLED, text="Auto-Play")
        self.reset_perf_data()
        
        self.root.config(cursor="")
        self.draw_board()
        messagebox.showinfo("Ready", "Winning Deal dimuat!\nSolusi dijamin ada")

    #ATURAN GAME LOGIC 
    def new_deal(self):
        if self.playing: return
        self.state = new_deal()
        self.initial_state = copy.deepcopy(self.state)
        self.selected.clear()
        self.current_solution = None
        self.btn_autoplay.config(state=tk.DISABLED, text="Auto-Play")
        self.reset_perf_data()
        self.draw_board()

    def reset_perf_data(self):
        self.perf_data['DFS'] = {'status': '-', 'waktu': 0, 'nodes': 0, 'langkah': 0}
        self.perf_data['BFS'] = {'status': '-', 'waktu': 0, 'nodes': 0, 'langkah': 0}

    def reset_board(self):
        if self.playing: return
        self.state = copy.deepcopy(self.initial_state)
        self.selected.clear()
        self.draw_board()

    def draw(self):
        if self.playing: return
        res = self.state.draw_from_stock()
        if res:
            self.state = res
            self.selected.clear()
            self.draw_board()
        else:
            messagebox.showinfo("Info", "Stock Habis / Limit Recycle")
    
    def get_card_rank(self, card_obj):
        if card_obj is None: return 0
        try:
            val = card_obj[0]
            ranks = {'A': 1, 'J': 11, 'Q': 12, 'K': 13}
            if str(val).upper() in ranks: return ranks[str(val).upper()]
            return int(val)
        except: return 0

    def draw_board(self):
        self.canvas.delete("all")
        s = self.state
        self._hitboxes = []
        
        idx = 0
        for row in range(7):
            row_len = row + 1
            total_width = row_len * CARD_W + (row_len-1)*8
            x0 = 430 - total_width/2
            y = 30 + row * (CARD_H + 10)
            for pos in range(row_len):
                x = x0 + pos * (CARD_W + 8)
                self._draw_card(x, y, idx)
                idx += 1
        
        total_bottom_w = 3 * CARD_W + 40
        sx = 430 - total_bottom_w / 2
        wx1 = sx + CARD_W + 20
        wx2 = wx1 + CARD_W + 20
        sy, wy = 450, 450
        
        #Stock
        if len(s.stock) > s.stock_index:
            self.canvas.create_rectangle(sx, sy, sx+CARD_W, sy+CARD_H, fill='#444', outline='white', tags="stock")
            self.canvas.create_text(sx+CARD_W/2, sy+CARD_H/2, text=f"Stock\n{len(s.stock)-s.stock_index}", fill='white', tags="stock")
            self.canvas.tag_bind("stock", "<Button-1>", lambda e: self.draw())
        else:
            self.canvas.create_rectangle(sx, sy, sx+CARD_W, sy+CARD_H, fill='#111', outline='#333')
            lbl = "Recycle" if s.recycle < 2 else "Habis"
            self.canvas.create_text(sx+CARD_W/2, sy+CARD_H/2, text=lbl, fill='gray')

        # Slot Draw 1
        if s.waste1:
            outline = 'green' if 'w1' in self.selected else 'black'
            width = 3 if 'w1' in self.selected else 1
            self.canvas.create_rectangle(wx1, wy, wx1+CARD_W, wy+CARD_H, fill='white', outline=outline, width=width)
            c = card_str(s.waste1)
            col = 'red' if c[-1] in '♥♦' else 'black'
            self.canvas.create_text(wx1+CARD_W/2, wy+CARD_H/2, text=c, fill=col, font=("Arial", 10, "bold"))
        else:
            self.canvas.create_rectangle(wx1, wy, wx1+CARD_W, wy+CARD_H, fill='#222', outline='#444', dash=(2,2))

        # Slot Draw 2
        if s.waste2:
            outline = 'green' if 'w2' in self.selected else 'black'
            width = 3 if 'w2' in self.selected else 1
            self.canvas.create_rectangle(wx2, wy, wx2+CARD_W, wy+CARD_H, fill='white', outline=outline, width=width)
            c = card_str(s.waste2[-1])
            col = 'red' if c[-1] in '♥♦' else 'black'
            self.canvas.create_text(wx2+CARD_W/2, wy+CARD_H/2, text=c, fill=col, font=("Arial", 10, "bold"))
        else:
            self.canvas.create_rectangle(wx2, wy, wx2+CARD_W, wy+CARD_H, fill='#222', outline='#444', dash=(2,2))

        info = f"Recycles: {2-s.recycle} | Sisa Piramida: {s.remaining_pyramid_count()}"
        self.canvas.create_text(430, 550, text=info, fill='#888')

    def _draw_card(self, x, y, idx):
        s = self.state
        if s.removed[idx]:
            self.canvas.create_rectangle(x, y, x+CARD_W, y+CARD_H, fill='#2b2b2b', outline='#2b2b2b')
        else:
            exposed = s.is_exposed(idx)
            fill = 'white' if exposed else '#ddd'
            outline, width = ('green', 3) if idx in self.selected else ('black', 1)
            self.canvas.create_rectangle(x, y, x+CARD_W, y+CARD_H, fill=fill, outline=outline, width=width)
            c = card_str(s.pyramid[idx])
            col = 'red' if c[-1] in '♥♦' else 'black'
            self.canvas.create_text(x+CARD_W/2, y+CARD_H/2, text=c, fill=col)
            if exposed: self._hitboxes.append((x, y, x+CARD_W, y+CARD_H, idx))

    #INTERAKSI PENGGUNA
    def on_click(self, event):
        if self.playing: return

        for x1, y1, x2, y2, idx in reversed(self._hitboxes):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if self.state.removed[idx] or not self.state.is_exposed(idx): return
                if idx in self.selected: self.selected.remove(idx)
                else: self.selected.append(idx)
                self.draw_board(); self.check_move(); return

        total_bottom_w = 3 * CARD_W + 40
        sx = 430 - total_bottom_w / 2
        wx1 = sx + CARD_W + 20
        wx2 = wx1 + CARD_W + 20
        wy = 450

        if sx <= event.x <= sx+CARD_W and wy <= event.y <= wy+CARD_H: self.draw(); return
        if wx1 <= event.x <= wx1+CARD_W and wy <= event.y <= wy+CARD_H:
            if self.state.waste1 is None: return
            if 'w1' in self.selected: self.selected.remove('w1')
            else: self.selected.append('w1')
            self.draw_board(); self.check_move(); return
        if wx2 <= event.x <= wx2+CARD_W and wy <= event.y <= wy+CARD_H:
            if not self.state.waste2: return
            if 'w2' in self.selected: self.selected.remove('w2')
            else: self.selected.append('w2')
            self.draw_board(); self.check_move(); return

    def check_move(self):
        total_rank = 0
        for s in self.selected:
            if s == 'w1': card = self.state.waste1
            elif s == 'w2': card = self.state.waste2[-1]
            else: card = self.state.pyramid[s]
            total_rank += self.get_card_rank(card)

        if total_rank == 13: self.root.after(50, self.execute_logic_remove)
        elif len(self.selected) >= 2: self.root.after(200, lambda: [self.selected.clear(), self.draw_board()])

    def execute_logic_remove(self):
        if not self.selected: return
        kinds = []
        for s in self.selected:
            if s == 'w1': kinds.append(('w1', None))
            elif s == 'w2': kinds.append(('w2', None))
            else: kinds.append(('p', s))
        
        kinds.sort(key=lambda k: 0 if k[0]=='p' else (1 if k[0]=='w1' else 2))
        move = ('remove', kinds)
        
        if move in generate_moves(self.state):
            self.state = apply_move(self.state, move)
            if self.state.is_goal(): messagebox.showinfo("Menang!", "Piramida Bersih!")
        
        self.selected.clear()
        self.draw_board()

    # SOLVER CONFIGURATION 
    def run_dfs(self): self._run_solver(solve_with_dfs, 'DFS')
    def run_bfs(self): self._run_solver(solve_with_bfs, 'BFS')

    def _run_solver(self, func, name):
        if self.playing: return
        solve_state = copy.deepcopy(self.initial_state)
        def run():
            self.root.config(cursor="watch")
            start = time.time()
            sol, nodes = func(solve_state, node_limit=3000000)
            durasi = f"{round(time.time() - start, 3)}s"
            status = 'SUCCESS' if sol else 'FAIL'
            if sol: self.current_solution = sol
            self.perf_data[name] = {'status': status, 'waktu': durasi, 'nodes': nodes, 'langkah': len(sol) if sol else 0}
            self.root.after(0, lambda: self.on_solver_finish(name, sol))
        threading.Thread(target=run, daemon=True).start()

    def on_solver_finish(self, name, sol):
        self.root.config(cursor="")
        if sol: self.btn_autoplay.config(state=tk.NORMAL, text=f"Auto-Play ({name})")
        self.show_comparison_popup()

    def autoplay(self):
        if not self.current_solution: return
        self.state = copy.deepcopy(self.initial_state)
        self.selected.clear()
        self.draw_board()
        self.playing = True
        def play():
            for mv in self.current_solution:
                if not self.playing: break
                time.sleep(0.2)
                self.state = apply_move(self.state, mv)
                self.root.after(0, self.draw_board)
            self.playing = False
            self.root.after(0, lambda: messagebox.showinfo("Selesai", "Replay Selesai."))
        threading.Thread(target=play, daemon=True).start()

    def show_comparison_popup(self):
        d, b = self.perf_data['DFS'], self.perf_data['BFS']
        header = f"{'TABEL':<12} | {'DFS':<14} | {'BFS':<14}"
        div    = "-" * 46
        row1   = f"{'Status':<12} | {str(d['status']):<14} | {str(b['status']):<14}"
        row2   = f"{'Waktu':<12} | {str(d['waktu']):<14} | {str(b['waktu']):<14}"
        row3   = f"{'Nodes':<12} | {str(d['nodes']):<14} | {str(b['nodes']):<14}"
        row4   = f"{'Langkah':<12} | {str(d['langkah']):<14} | {str(b['langkah']):<14}"
        final_text = f"{header}\n{div}\n{row1}\n{row2}\n{row3}\n{row4}"
        top = tk.Toplevel(self.root)
        top.title("Hasil Solver")
        tk.Label(top, text=final_text, font=("Consolas", 11), justify="left", padx=20, pady=20, bg="#f0f0f0").pack()
