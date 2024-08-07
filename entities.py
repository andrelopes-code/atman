from collections import deque
from heapq import heappop, heappush
from random import choice

from bfs import BFS
from config import (
    ATMAN,
    ATMAN_COLLIDEABLE,
    ATMAN_RANGE_SIZE,
    COLLIDEABLE,
    DOWN,
    EMPTY,
    FRUIT,
    GHOST,
    GHOST_MOVE_CICLE,
    LEFT,
    MAX_FRUIT_CYCLES,
    MOVE,
    POINT,
    POINT_VALUE,
    RIGHT,
    UP,
)
from errors import AtmanDied


class Atman:
    def __init__(self, board: list[list[int]]):
        self.x = 1
        self.y = 1
        self.score = 0
        self.board = board
        self.direction = None
        self.fruit_active = False
        self.fruit_cycles = 0
        self.ghost_ated = None

    def move(self):
        """Move o Atman na direção indicada em `self.direction`."""

        if self.will_collide():
            return

        # Define as coordenadas temporárias.
        x, y = self.x, self.y

        if self.direction == UP:
            y -= 1
        elif self.direction == DOWN:
            y += 1
        elif self.direction == LEFT:
            x -= 1
        elif self.direction == RIGHT:
            x += 1

        if self.ate(POINT, x, y):
            self.score += POINT_VALUE

        if self.ate(FRUIT, x, y):
            self.fruit_active = True

        if self.ate(GHOST, x, y):
            if self.fruit_active:
                self.ghost_ated = (y, x)
            else:
                raise AtmanDied

        self.move_to(x, y)

    def move_to(self, x, y):
        """Move o Atman para as coordenadas (x, y)."""

        self.board[self.y][self.x] = EMPTY
        self.board[y][x] = ATMAN
        self.x, self.y = x, y

    def change_direction(self, direction):
        """Muda a direção do Atman para a direção fornecida."""

        # Verifica se a direção passada é um caminho livre.
        # Caso não seja, retorna e não altera a direção.
        if self.will_collide(direction):
            return

        self.direction = direction

    def will_collide(self, direction=None):
        """Verifica se o Atman vai colidir com algo."""

        direction = direction or self.direction

        if direction == UP:
            return self.board[self.y - 1][self.x] in ATMAN_COLLIDEABLE
        elif direction == DOWN:
            return self.board[self.y + 1][self.x] in ATMAN_COLLIDEABLE
        elif direction == LEFT:
            return self.board[self.y][self.x - 1] in ATMAN_COLLIDEABLE
        elif direction == RIGHT:
            return self.board[self.y][self.x + 1] in ATMAN_COLLIDEABLE

    def ate(self, value, x, y):
        """Verifica se o Atman vai comer uma celula com o valor em `value`."""

        if self.board[y][x] == value:
            return True
        return False


class Ghost:
    def __init__(self, board: list[list[int]], atman: Atman, x: int, y: int):
        self.atman = atman
        self.board = board
        self.x = x
        self.y = y
        self._prev_x = -1
        self._prev_y = -1
        self._original_x = x
        self._original_y = y
        self.path = deque()
        self.direction = None
        self.last_cell_value = EMPTY

        # Desenha o Ghost em sua posição inicial.
        self.board[self.y][self.x] = GHOST

    def move(self):
        """Move o Ghost."""

        if next(GHOST_MOVE_CICLE) == MOVE:
            if self.atman.fruit_active:
                # Caso a fruta tenha sido ativada começa a mover o
                # Ghost para longe do Atman.

                # Remove a direção anterior do Ghost caso a fruta
                # tenha acabado de ser ativada.
                if self.atman.fruit_cycles == 0:
                    self.direction = None

                # Desativa a fruta caso tenha atingido o limite de ciclos
                # (que vale como medida de tempo de vida da fruta).
                elif self.atman.fruit_cycles == MAX_FRUIT_CYCLES:
                    self.atman.fruit_active = False
                    self.atman.fruit_cycles = 0

                self.atman.fruit_cycles += 1
                self.move_away_from_atman()

            elif self.in_atman_range():
                if self.path:
                    # Caso tenha um caminho, move o Ghost.
                    self._follow_atman()
                else:
                    # Caso não tenha um caminho, obtem um
                    # novo caminho e move o Ghost.
                    self.get_new_path_to_atman()
                    self._follow_atman()

            else:
                # Caso não esteja no range, move o Ghost aleatóriamente.
                self.move_randomly()

    def in_atman_range(self, range_size=ATMAN_RANGE_SIZE):
        """Verifica se o Ghost está no range para seguir o atman."""

        delta_y = abs(self.y - self.atman.y)
        delta_x = abs(self.x - self.atman.x)

        return delta_y <= range_size and delta_x <= range_size

    def move_randomly(self):
        """Move o Ghost em uma direção aleatória."""

        # Caso o Ghost esteja parado, escolhe uma direção aleatória.
        # caso não tenha uma direção disponível, retorna e mantem o Ghost parado.
        if self.direction is None:
            has_direction = self.choose_and_set_random_available_direction()
            if has_direction is None:
                return

        self.change_direction_if_cornered()
        self.choose_and_set_random_available_direction()

        # Posições temporárias para o Ghost ser movido.
        x, y = self.x, self.y

        if self.direction == UP:
            y -= 1
        elif self.direction == DOWN:
            y += 1
        elif self.direction == LEFT:
            x -= 1
        elif self.direction == RIGHT:
            x += 1

        # ! Isso provavalmente não será necessário caso
        # ! o Ghost esteja perto do atman e comece a utilizar
        # ! o caminho para chegar ao atman.
        if self.is_the_atman(x, y):
            raise AtmanDied

        self.move_to(x, y)

    def move_away_from_atman(self):
        """Faz o Ghost se mover para a direção contraria ao Atman."""

        priority_directions = self._get_priority_directions()

        if priority_directions:
            _, direction = heappop(priority_directions)
            self.direction = direction

        # Posições temporárias para o Ghost ser movido.
        x, y = self.x, self.y

        if self.direction == UP:
            y -= 1
        elif self.direction == DOWN:
            y += 1
        elif self.direction == LEFT:
            x -= 1
        elif self.direction == RIGHT:
            x += 1

        self.move_to(x, y)

    def change_direction_if_cornered(self):
        """Verifica se o Ghost está encurralado em um final de caminho.
        Se estiver, altera a direção dele para a direção contraria.
        """

        available_directions = self._get_available_directions()

        # Caso o ghost esteja em um caminho com 0 direções disponíveis,
        # verifica se ele está seguindo um caminho sem saída, se estiver
        # altera a direção dele para a direção contraria.
        if len(available_directions) == 0:
            if self.direction == UP:
                self.direction = DOWN
            elif self.direction == DOWN:
                self.direction = UP
            elif self.direction == LEFT:
                self.direction = RIGHT
            elif self.direction == RIGHT:
                self.direction = LEFT

        return True

    def choose_and_set_random_available_direction(self):
        """Escolhe uma direção aleatória livre."""

        available_directions = self._get_available_directions()

        if not available_directions:
            return

        self.direction = choice(available_directions)

    def move_to(self, x, y):
        """Move o Ghost para as coordenadas (x, y)."""

        # Caso a celula (x, y) não esteja livre, retorna.
        if self.board[y][x] in COLLIDEABLE:
            return

        # Restaura o valor da celula anterior e salva
        # o valor da celula atual.
        self.board[self.y][self.x] = self.last_cell_value

        # Define o valor da celula anterior, evitando
        # a sobreposição de Ghosts.
        if self.board[y][x] == GHOST:
            self.last_cell_value = EMPTY
        else:
            self.last_cell_value = self.board[y][x]

        # Move o Ghost para as coordenadas (x, y).
        # e atualiza as coordenadas do Ghost
        self.board[y][x] = GHOST
        self._prev_x, self._prev_y = self.x, self.y
        self.x, self.y = x, y

    def direction_changed(self, x, y):
        """Verifica se a direção do Ghost foi alterada."""

        # Caso o Ghost não tenha uma celula anterior,
        # ele não deve mudar de direção.
        if self._prev_x == -1 and self._prev_y == -1:
            return False

        # Calcula a diferença entre as coordenadas
        # anterior < atual < próxima.
        d1 = (self.y - self._prev_y, self.x - self._prev_x)
        d2 = (y - self.y, x - self.x)

        # Se as diferencas forem iguais, significa
        # que está seguindo uma direção constante, ou seja
        # o Ghost não mudou de direção.
        if d1 == d2:
            return False

        return True

    def get_new_path_to_atman(self):
        """Atualiza o caminho mais curto para o Atman."""

        self.path = self._get_path_to_atman()

    def is_the_atman(self, x, y):
        """Verifica se o Ghost atingiu o Atman."""

        return self.board[y][x] == ATMAN

    def reset(self):
        self.x = self._original_x
        self.y = self._original_y
        self.atman.ghost_ated = None

    def _get_available_directions(self):
        """Retorna uma lista com as direções disponíveis para o Ghost."""

        available_directions = []

        position_up = self.board[self.y - 1][self.x]
        position_down = self.board[self.y + 1][self.x]
        position_left = self.board[self.y][self.x - 1]
        position_right = self.board[self.y][self.x + 1]

        if position_up not in COLLIDEABLE and self.direction != DOWN:
            available_directions.append(UP)
        elif position_down not in COLLIDEABLE and self.direction != UP:
            available_directions.append(DOWN)
        elif position_left not in COLLIDEABLE and self.direction != RIGHT:
            available_directions.append(LEFT)
        elif position_right not in COLLIDEABLE and self.direction != LEFT:
            available_directions.append(RIGHT)

        return available_directions

    def _get_priority_directions(self):
        """Retorna um min-heap com as direções disponíveis para o Ghost em ordem de prioridade."""

        available_directions = []

        position_up = self.board[self.y - 1][self.x]
        position_down = self.board[self.y + 1][self.x]
        position_left = self.board[self.y][self.x - 1]
        position_right = self.board[self.y][self.x + 1]

        # Define a prioridade de cada direção com base
        # na posição do Ghost para o Atman.
        up_priority = self.y - self.atman.y
        down_priority = self.atman.y - self.y
        left_priority = self.x - self.atman.x
        right_priority = self.atman.x - self.x

        if position_up not in COLLIDEABLE and self.direction != DOWN:
            heappush(available_directions, (up_priority, UP))
        if position_down not in COLLIDEABLE and self.direction != UP:
            heappush(available_directions, (down_priority, DOWN))
        if position_left not in COLLIDEABLE and self.direction != RIGHT:
            heappush(available_directions, (left_priority, LEFT))
        if position_right not in COLLIDEABLE and self.direction != LEFT:
            heappush(available_directions, (right_priority, RIGHT))

        # Caso não tenha neuma das direções disponíveis,
        # escolhe a direção contrária à anterior.
        if len(available_directions) == 0:
            if self.direction == UP:
                available_directions.append((up_priority, DOWN))
            elif self.direction == DOWN:
                available_directions.append((down_priority, UP))
            elif self.direction == LEFT:
                available_directions.append((left_priority, RIGHT))
            elif self.direction == RIGHT:
                available_directions.append((right_priority, LEFT))

        return available_directions

    def _get_path_to_atman(self):
        """Retorna um novo menor caminho para o Atman."""

        return BFS.search(self.board, (self.y, self.x), (self.atman.y, self.atman.x))

    def _follow_atman(self):
        """Move o Ghost para a proxima posição em direção ao Atman."""

        # Pega a proxima posição sem remove-la.
        y, x = self.path[-1]

        # Verifica se o Ghost atingiu o Atman.
        if self.is_the_atman(x, y):
            raise AtmanDied

        # Verifica se a direção do Ghost foi alterada.
        # Caso tenha sido, atualiza o caminho.
        if self.direction_changed(x, y):
            self.get_new_path_to_atman()

        # Pega a proxima posição do caminho e
        # move o Ghost para ela.
        y, x = self.path.pop()
        self.move_to(x, y)
