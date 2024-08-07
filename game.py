import curses
from random import choice
from time import sleep

from board import Board
from config import (
    ATMAN,
    CHARS,
    EMPTY,
    FRUIT,
    GHOST,
    GHOST_VALUE,
    KEY_MAP,
    MAX_FRUIT_CYCLES,
    POINT,
    SLEEP_TIME,
    WALL,
)
from entities import Atman, Ghost


class Game:
    def __init__(self, win: curses.window, board: Board, atman: Atman):
        self.win = win
        self.board = board
        self.atman = atman
        self.setup_window()

        mid_x = (self.board.get_columns() // 2, self.board.get_rows() // 2)

        self.ghosts = (
            Ghost(self.board, self.atman, mid_x[0] - 1, 11),
            Ghost(self.board, self.atman, mid_x[0] + 1, 11),
            Ghost(self.board, self.atman, mid_x[0], 11),
        )

        self.xsize = self.board.get_columns()  # Numero de colunas do tabuleiro.
        self.ysize = self.board.get_rows()  # Numero de linhas do tabuleiro.

    def start(self):
        """Inicia o jogo."""

        # Inicializa as configurações gerais.d
        self.setup_config()

        while True:
            key = self.get_last_key_pressed()

            if key in KEY_MAP:
                # Muda a direção do Atman caso a tecla pressionada
                # seja uma das teclas de direção mapeadas.
                self.atman.change_direction(KEY_MAP[key])

            self.update_entities_positions()

            # Percorre todas as celulas do tabuleiro
            # e renderiza o caractere correspondente ao
            # valor da celula.
            for y in range(self.ysize):
                for x in range(self.xsize):
                    cell = self.board[y][x]

                    if cell == EMPTY:
                        self.win.addch(y, x * 2, CHARS[EMPTY], curses.color_pair(EMPTY))
                    elif cell == ATMAN:
                        self.win.addch(y, x * 2, CHARS[ATMAN], curses.color_pair(ATMAN))
                    elif cell == POINT:
                        self.win.addch(y, x * 2, CHARS[POINT], curses.color_pair(POINT))
                    elif cell == FRUIT:
                        self.win.addch(y, x * 2, CHARS[FRUIT], curses.color_pair(FRUIT))
                    elif cell == GHOST:
                        if self.atman.fruit_active:
                            self.win.addch(y, x * 2, choice('ᾸĀÄ'), curses.color_pair(GHOST))
                        else:
                            self.win.addch(y, x * 2, CHARS[GHOST], curses.color_pair(GHOST))
                    elif cell == WALL:
                        self.win.addch(y, x * 2, CHARS[WALL], curses.color_pair(WALL))
                        # Verificação para preencher os espaços deixados entre
                        # as celulas caso a celula seja uma parede na horizontal.
                        peeked_char = chr(self.win.inch(y, x * 2 - 2) & 0xFF)
                        if peeked_char == CHARS[WALL]:
                            self.win.addstr(
                                y,
                                x * 2 - 1,
                                CHARS[WALL],
                                curses.color_pair(WALL),
                            )

            self.render_footer()

            # Atualiza a tela de jogo
            # e aguarda o tempo de `SLEEP_TIME`.
            self.win.refresh()
            sleep(SLEEP_TIME)

    def update_entities_positions(self):
        """Atualiza as posicoes dos Ghosts e o Atman."""

        self.atman.move()

        if self.atman.ghost_ated:
            for ghost in self.ghosts:
                if (ghost.y, ghost.x) == self.atman.ghost_ated:
                    self.atman.score += GHOST_VALUE
                    ghost.reset()
        else:
            for ghost in self.ghosts:
                ghost.move()

    def render_footer(self):
        """Renderiza o rodapé da tela."""

        footer_size = self.xsize * 2 - 1
        self.win.addstr(
            self.ysize,
            0,
            f'Score: {self.atman.score}'.center(footer_size),
        )

        footer_size = self.xsize * 2 - 1
        self.win.addstr(
            self.ysize + 1,
            0,
            ' ' * footer_size,
        )

        if self.atman.fruit_active:
            progress = self.atman.fruit_cycles / MAX_FRUIT_CYCLES
            filled = int(progress * footer_size)
            chars = '█' * filled
            self.win.addstr(
                self.ysize + 1,
                0,
                chars,
            )

    def get_last_key_pressed(self):
        """Retorna a ultima tecla pressionada."""

        key = self.win.getch()
        if key == -1:
            return key

        while True:
            new_key = self.win.getch()
            if new_key == -1:
                break
            key = new_key

        return key

    def setup_config(self):
        # Inicializa as configurações gerais.
        curses.curs_set(0)
        curses.cbreak(True)
        self.win.keypad(True)
        self.win.nodelay(True)

        # Inicializa os pares de cores.
        curses.init_color(10, 144, 256, 610)
        curses.init_color(11, 194, 296, 810)
        curses.init_pair(WALL, 11, 10)

        curses.init_pair(POINT, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(GHOST, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(FRUIT, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ATMAN, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def setup_window(self):
        """Define as dimensões da janela e centraliza."""
        max_y, max_x = self.win.getmaxyx()

        h = self.board.get_rows()
        w = self.board.get_columns()

        start_y = (max_y - h) // 2
        start_x = (max_x - w * 2) // 2

        self.win = curses.newwin(max_y, max_x, start_y, start_x)


if __name__ == '__main__':

    def main(win: curses.window):
        board = Board(1)
        atman = Atman(board)
        game = Game(win, board, atman)

        game.start()

    curses.wrapper(main)
