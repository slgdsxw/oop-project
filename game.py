from abc import ABC, abstractmethod

from board import Board, Stone


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
