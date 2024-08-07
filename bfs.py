from collections import deque

from config import WALL

# Direções (esquerda, direita, acima, abaixo).
DIRECTIONS = ((0, -1), (0, 1), (-1, 0), (1, 0))


class BFS:
    """Breadth-First Search"""

    @staticmethod
    def search(
        board: list[list[int]],
        start_position: tuple[int, int],
        target_position: tuple[int, int],
    ):
        """Retorna o menor caminho para a posição alvo.
        As coordenadas usadas devem ser passadas e serão
        retornadas invertidas, ou seja, (y, x)."""

        pending_positions = deque([start_position])
        visited_posotions = {start_position}
        previous_position = {start_position: tuple()}

        board_height = len(board)
        board_width = len(board[0])

        while pending_positions:
            # Obtém a proxima posição na fila e verifica
            # se é a posição alvo.
            current_position = pending_positions.popleft()
            if current_position == target_position:
                break

            # Percorre todos os vizinhos possiveis da posição atual,
            # acima, abaixo e para a esquerda e para a direita.
            for delta_y, delta_x in DIRECTIONS:
                neighbor_position = (
                    current_position[0] + delta_y,
                    current_position[1] + delta_x,
                )

                if (
                    # Verifica se as coordenadas do vizinho estão dentro do tabuleiro.
                    0 <= neighbor_position[0] < board_height
                    and 0 <= neighbor_position[1] < board_width
                    # Verifica se o vizinho é um caminho livre.
                    and board[neighbor_position[0]][neighbor_position[1]] != WALL
                    # Verifica se o vizinho ainda não foi visitado.
                    and neighbor_position not in visited_posotions
                ):
                    visited_posotions.add(neighbor_position)
                    pending_positions.append(neighbor_position)
                    previous_position[neighbor_position] = current_position

        # Cria um caminho da posição inicial para a posição do alvo.
        path = deque([target_position])
        current_position = target_position

        while current_position:
            current_position = previous_position[current_position]
            path.append(current_position)

        # Remove o `None` adicionado no final do caminho
        # e remove o caminho da posição inicial.
        path.pop()
        path.pop()

        return path
