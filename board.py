"""棋盘基础数据模型：棋子、坐标与棋盘"""

from enum import Enum


class Stone(Enum):
    """棋子颜色枚举"""

    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opposite(self):
        if self is Stone.EMPTY:
            return Stone.EMPTY
        return Stone.BLACK if self is Stone.WHITE else Stone.WHITE

    def symbol(self):
        """控制台显示符号：空 . 黑 X 白 O"""
        return {Stone.EMPTY: ".", Stone.BLACK: "X", Stone.WHITE: "O"}[self]


class Position:
    """棋盘坐标内部使用 0 为起点，界面输入输出使用 1 为起点"""

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
    def parse(cls, text, size=None):
        """把 "行,列" 文本解析为坐标；给定 size 时同时校验是否越界"""
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
        if size is not None and (row > size or col > size):
            raise ValueError("坐标超出棋盘范围")
        return cls(row - 1, col - 1)


class Board:
    """N×N 棋盘，只负责存储与查询，不含任何行棋规则"""

    def __init__(self, size):
        self._size = size
        self._grid = [[Stone.EMPTY for _ in range(size)] for _ in range(size)]

    @property
    def size(self):
        return self._size

    def in_bounds(self, row, col):
        """坐标是否在棋盘范围内"""
        return 0 <= row < self._size and 0 <= col < self._size

    def get(self, row, col):
        return self._grid[row][col]

    def set(self, row, col, stone):
        self._grid[row][col] = stone

    def is_full(self):
        """棋盘是否已无空点"""
        return all(self.get(r, c) is not Stone.EMPTY
                   for r in range(self._size)
                   for c in range(self._size))

    def count(self, stone):
        """统计某种棋子的总数"""
        return sum(1 for r in range(self._size) for c in range(self._size)
                   if self.get(r, c) is stone)

    def occupied(self):
        """依次产出所有有子位置的坐标 (row, col)"""
        for r in range(self._size):
            for c in range(self._size):
                if self.get(r, c) is not Stone.EMPTY:
                    yield r, c

    def key(self):
        """当前局面的可哈希指纹，供围棋禁全局同形（打劫）判断使用"""
        return tuple(tuple(row) for row in self._grid)

    def load_grid(self, grid):
        """用外部网格覆盖棋盘内容"""
        self._grid = [row[:] for row in grid]
