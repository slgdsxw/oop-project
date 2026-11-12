from enum import Enum


class Stone(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opposite(self):
        if self is Stone.EMPTY:
            return Stone.EMPTY
        return Stone.BLACK if self is Stone.WHITE else Stone.WHITE

    def symbol(self):
        return {Stone.EMPTY: ".", Stone.BLACK: "X", Stone.WHITE: "O"}[self]


class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return isinstance(other, Position) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return "Position({},{})".format(self.row, self.col)

    @classmethod
    def parse(cls, text):
        parts = text.replace("，", ",").split(",")
        if len(parts) != 2:
            raise ValueError("坐标格式应为 行,列")
        try:
            row = int(parts[0].strip())
            col = int(parts[1].strip())
        except ValueError:
            raise ValueError("坐标必须是整数")
        if row < 1 or col < 1:
            raise ValueError("坐标必须从 1 开始")
        return cls(row - 1, col - 1)
