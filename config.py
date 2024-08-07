import curses
from itertools import cycle

# Tipos de celula.
POINT = 1
WALL = 2
GHOST = 3
ATMAN = 4
EMPTY = 5
FRUIT = 6
COLLIDEABLE = {GHOST, WALL}
ATMAN_COLLIDEABLE = {WALL}
# Direções.
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4


# Define os caracteres correspondentes aos
# valores das celulas do tabuleiro.
CHARS = {
    ATMAN: '@',
    WALL: '/',
    POINT: '·',
    GHOST: 'A',
    EMPTY: ' ',
    FRUIT: '*',
}


# Define as teclas mapeadas para direções.
KEY_MAP = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
    ord('w'): UP,
    ord('W'): UP,
    ord('s'): DOWN,
    ord('S'): DOWN,
    ord('a'): LEFT,
    ord('A'): LEFT,
    ord('d'): RIGHT,
    ord('D'): RIGHT,
}

# Define o tempo de espera entre as renderizações.
SLEEP_TIME = 0.19  # (segundos)


# O valor de um ponto.
POINT_VALUE = 10


# Ciclo que define quando os Ghosts
# devem ou não se mover.
MOVE = 1
GHOST_MOVE_CICLE = cycle([0, MOVE])
ATMAN_RANGE_SIZE = 7
MAX_FRUIT_CYCLES = 75
GHOST_VALUE = 300
