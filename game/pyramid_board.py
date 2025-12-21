from .deck import full_deck, shuffle_deck, card_str, RANK_VALUE
from typing import List, Tuple, Optional

class PyramidState:
    def __init__(self, pyramid, removed, stock, stock_index, waste1, waste2, recycle=0):
        self.pyramid = tuple(pyramid)
        self.removed = tuple(removed)
        self.stock = tuple(stock)
        self.stock_index = int(stock_index)
        self.waste1: Optional[Tuple] = waste1 
        self.waste2 = tuple(waste2) 
        self.recycle = int(recycle)

    def is_exposed(self, idx: int) -> bool:
        if self.removed[idx]: return False
        s, row = 0, 0
        while s + row <= idx: s += row; row += 1
        row -= 1
        if row == 6: return True
        start = row*(row+1)//2
        pos = idx - start
        child_row = row+1
        child_start = child_row*(child_row+1)//2
        return self.removed[child_start + pos] and self.removed[child_start + pos + 1]

    def exposed_indexes(self):
        return [i for i in range(28) if self.is_exposed(i)]

    def remaining_pyramid_count(self):
        return sum(0 if r else 1 for r in self.removed)

    def is_goal(self):
        return all(self.removed)

    #Logic Draw dari Stock
    def draw_from_stock(self):
        if self.stock_index < len(self.stock):
            drawn_card = self.stock[self.stock_index]
            
            #Kartu baru masuk Slot 1
            new_waste1 = drawn_card
            
            #Kartu lama di Slot 1 pindah ke atas Slot 2
            new_waste2_list = list(self.waste2)
            if self.waste1 is not None:
                new_waste2_list.append(self.waste1)
                
            return PyramidState(self.pyramid, list(self.removed), list(self.stock), self.stock_index+1, new_waste1, tuple(new_waste2_list), self.recycle)
        else:
            #Recycle gabungkan Slot1 + Slot2 jadi Stock baru
            current_waste = list(self.waste2)
            if self.waste1 is not None:
                current_waste.append(self.waste1)
                
            if len(current_waste) > 0 and self.recycle < 2:
                new_stock = tuple(current_waste[::-1])
                return PyramidState(self.pyramid, list(self.removed), list(new_stock), 0, None, [], self.recycle+1)
            else:
                return None

    def remove_pair(self, removals):
        removed = list(self.removed)
        new_waste1 = self.waste1
        new_waste2 = list(self.waste2)
        
        for kind, v in removals:
            if kind == 'p':
                removed[v] = True
            elif kind == 'w1':
                if new_waste1 is None: return None 
                new_waste1 = None
            elif kind == 'w2':
                if not new_waste2: return None 
                new_waste2.pop()
            else:
                raise ValueError("Invalid kind")
                
        return PyramidState(self.pyramid, removed, list(self.stock), self.stock_index, new_waste1, tuple(new_waste2), self.recycle)

        #Hash berdasarkan status unik
    def __hash__(self):
        return hash((self.removed, self.stock_index, self.waste1, self.waste2, self.recycle))

    def __eq__(self, other):
        if not isinstance(other, PyramidState): return False
        return (self.removed, self.stock_index, self.waste1, self.waste2, self.recycle) == \
               (other.removed, other.stock_index, other.waste1, other.waste2, other.recycle)

def new_deal(seed=None):
    deck = full_deck()
    shuffle_deck(deck, seed=seed)
    pyramid = deck[:28]
    stock = deck[28:]
    removed = [False]*28
    return PyramidState(pyramid, removed, stock, 0, None, [], 0)