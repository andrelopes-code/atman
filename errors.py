class AtmanDied(Exception):
    def __init__(self) -> None:
        super().__init__('Atman foi morto!')
