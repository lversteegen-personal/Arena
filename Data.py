import numpy as np
import itertools

PLAYER_NAMES = ["Alpha", "Beta", "Gamma", "Delta", "#"]

def PlayerString(id):

    return f"{PLAYER_NAMES[id]} (id: {id})"

NODE_NAMES = []
BOARD_WIDTH = 5
BOARD_HEIGHT = 5
size = BOARD_WIDTH * BOARD_HEIGHT
adjacency = np.zeros((BOARD_WIDTH, BOARD_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT), dtype=bool)
MAX_MOVES = 100
BASE_UNITS_PER_TURN = 2
UNITS_PER_TILE = 1/3+0.00001
LOG_ATK_DAMAGE_AVG_PER_UNIT = -0.7
LOG_ATK_DAMAGE_STDV_PER_UNIT = 0.4
LOG_DEF_DAMAGE_AVG_PER_UNIT = -0.4
LOG_DEF_DAMAGE_STDV_PER_UNIT = 0.2
COMBAT_WIDTH_RATIO = 5

for y, x in itertools.product(range(BOARD_HEIGHT), range(BOARD_WIDTH)):
    if x != 0:
        adjacency[x, y, x-1, y] = True
    if y != 0:
        adjacency[x, y, x, y-1] = True
    if x != BOARD_WIDTH-1:
        adjacency[x, y, x+1, y] = True
    if y != BOARD_HEIGHT-1:
        adjacency[x, y, x, y+1] = True
    
    NODE_NAMES.append(str((x,y)))

adjacency = adjacency.reshape(size, size)

neighborhoods = [[v for v in range(size) if adjacency[u,v]] for u in range(size)]

num_players = 2