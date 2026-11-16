from abc import ABC, abstractmethod

from board import Stone


class UIComponent(ABC):
    @abstractmethod
    def render(self, context):
        pass


class TitleComponent(UIComponent):
    def __init__(self, text):
        self._text = text

    def render(self, context):
        return ["{}  {}".format(self._text, context.get("subtitle", ""))]


class StatusComponent(UIComponent):
    def render(self, context):
        game = context.get("game")
        if game is None:
            return ["当前没有对局"]
        if game.finished:
            return ["对局已结束：{}".format(game.result_text)]
        return [
            "轮到执{}方行棋（{}）".format(
                game.current_stone.symbol(),
                "黑" if game.current_stone is Stone.BLACK else "白",
            )
        ]


class BoardComponent(UIComponent):
    def render(self, context):
        game = context.get("game")
        if game is None:
            return []
        board = game.board
        lines = ["    " + " ".join("{:>2}".format(c + 1) for c in range(board.size))]
        for r in range(board.size):
            row = "{:>3} ".format(r + 1)
            row += " ".join(board.get(r, c).symbol() for c in range(board.size))
            lines.append(row)
        return lines
