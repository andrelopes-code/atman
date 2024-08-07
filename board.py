from config import EMPTY, FRUIT, POINT, WALL


class Board(list):
    """Representa o tabuleiro do jogo."""

    def __init__(self, board_num=1):
        # Lê o tabuleiro de um arquivo
        # e calcula o número de pontos no tabuleiro.
        self._board = self.read_board_from_file(board_num)
        self.points_count = self._get_points_count()
        super().__init__(self._board)

    @staticmethod
    def read_board_from_file(board_num):
        """Lê o tabuleiro de um arquivo com um formato especifico."""
        match board_num:
            case 1:
                path = 'boards/board_01.txt'
            case 2:
                path = 'boards/board_02.txt'
            case _:
                path = 'boards/board_01.txt'

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            board = []

            for line in lines:
                chars_line = line
                row = []

                while chars_line:
                    char = chars_line[0]

                    if char == 'W':
                        row.append(WALL)
                    elif char == ' ':
                        row.append(POINT)
                    elif char == 'E':
                        row.append(EMPTY)
                    elif char == 'F':
                        row.append(FRUIT)

                    chars_line = chars_line[2:]

                board.append(row)

            return board

    def get_rows(self):
        return len(self)

    def get_columns(self):
        return len(self[0])

    def _get_points_count(self):
        points = 0
        for row in self._board:
            points += row.count(POINT)
        return points
