import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
RANK_VALUE = {r: i+1 for i, r in enumerate(RANKS)}  #A=1 J=11 Q =12 K=13

def full_deck():
    return [(r, s) for s in SUITS for r in RANKS]

def card_str(card):
    r, s = card
    return f"{r}{s}"

def shuffle_deck(deck, seed=None):
    if seed is None:
        random.shuffle(deck)
    else:
        rnd = random.Random(seed)
        rnd.shuffle(deck)
    return deck
