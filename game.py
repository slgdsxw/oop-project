from abc import ABC, abstractmethod

from board import Board, Position, Stone


class MoveRecord:
    def __init__(self, stone, position=None, captured=None):
        self.stone = stone
        self.position = position
        self.captured = captured or []


class Game(ABC):
    def __init__(self, size):
        self._board = Board(size)
        self._current_stone = Stone.BLACK
        self._history = []
        self._finished = False
        self._winner = None
        self._result_text = ""

    @property
    def board(self):
        return self._board

    @property
    def current_stone(self):
        return self._current_stone

    @property
    def finished(self):
        return self._finished

    @property
    def winner(self):
        return self._winner

    @property
    def result_text(self):
        return self._result_text

    @property
    def history(self):
        return list(self._history)

    @abstractmethod
    def game_name(self):
        pass

    @abstractmethod
    def allow_pass(self):
        pass

    @abstractmethod
    def try_place(self, position):
        pass

    def place(self, position):
        if self._finished:
            raise RuntimeError("对局已结束，无法落子")
        self.try_place(position)
        self._switch_turn()

    def _switch_turn(self):
        self._current_stone = self._current_stone.opposite()

    def _finish(self, winner, text):
        self._finished = True
        self._winner = winner
        self._result_text = text


class GomokuGame(Game):
    def game_name(self):
        return "五子棋"

    def allow_pass(self):
        return False

    def try_place(self, position):
        r, c = position.row, position.col
        if not self._board.in_bounds(r, c):
            raise ValueError("落子位置超出棋盘范围")
        if self._board.get(r, c) is not Stone.EMPTY:
            raise ValueError("该位置已有棋子")
        stone = self._current_stone
        self._board.set(r, c, stone)
        self._history.append(MoveRecord(stone, position))
        if self._has_five(r, c, stone):
            self._finish(stone, "执{}方连成五子获胜".format(stone.symbol()))
        elif self._board.is_full():
            self._finish(None, "棋盘已满，平局")

    def _has_five(self, row, col, stone):
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            count = 1
            for sign in (1, -1):
                r, c = row + sign * dr, col + sign * dc
                while self._board.in_bounds(r, c) and self._board.get(r, c) is stone:
                    count += 1
                    r += sign * dr
                    c += sign * dc
            if count >= 5:
                return True
        return False
