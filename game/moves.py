from .pyramid_board import PyramidState
from .deck import RANK_VALUE

def card_value(card):
    if card is None: return 0
    return RANK_VALUE[card[0]]

def generate_moves(state: PyramidState):
    moves = []
    exposed = state.exposed_indexes()
    
    #Pasangan sesama piramida
    for i in range(len(exposed)):
        for j in range(i+1, len(exposed)):
            if card_value(state.pyramid[exposed[i]]) + card_value(state.pyramid[exposed[j]]) == 13:
                moves.append(('remove', [('p', exposed[i]), ('p', exposed[j])]))
                
    #Piramida + Slot Draw 1
    if state.waste1 is not None:
        w1_val = card_value(state.waste1)
        for idx in exposed:
            if card_value(state.pyramid[idx]) + w1_val == 13:
                moves.append(('remove', [('p', idx), ('w1', None)]))
                
    #Piramida + Slot Draw 2
    if state.waste2:
        w2_val = card_value(state.waste2[-1])
        for idx in exposed:
            if card_value(state.pyramid[idx]) + w2_val == 13:
                moves.append(('remove', [('p', idx), ('w2', None)]))

    #Cek apakah Slot Draw 1 + Slot Draw 2 jumlahnya 13
    if state.waste1 is not None and state.waste2:
        if card_value(state.waste1) + card_value(state.waste2[-1]) == 13:
            moves.append(('remove', [('w1', None), ('w2', None)]))

    #King di piramida
    for idx in exposed:
        if card_value(state.pyramid[idx]) == 13:
            moves.append(('remove', [('p', idx)]))
            
    #King di Slot Draw 1
    if state.waste1 is not None and card_value(state.waste1) == 13:
        moves.append(('remove', [('w1', None)]))

    #King di Slot Draw 2
    if state.waste2 and card_value(state.waste2[-1]) == 13:
        moves.append(('remove', [('w2', None)]))
            
    #Draw kartu dari stock
    draw_state = state.draw_from_stock()
    if draw_state is not None:
        moves.append(('draw',))
        
    return moves

def apply_move(state: PyramidState, move):
    typ = move[0]
    if typ == 'draw':
        return state.draw_from_stock()
    elif typ == 'remove':
        return state.remove_pair(move[1])
    else:
        raise ValueError("Unknown move")