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


class HintComponent(UIComponent):
    def __init__(self):
        self._visible = True

    def toggle(self):
        self._visible = not self._visible

    @property
    def visible(self):
        return self._visible

    def render(self, context):
        if not self._visible:
            return []
        lines = [
            "可用指令：",
            "  start <gomoku|go> <大小>   开始新对局（大小 8-19）",
            "  place <行> <列>            在指定位置落子",
            "  pass                       虚着（仅围棋）",
            "  undo                       悔棋一步",
            "  resign                     投子认负",
            "  save <文件路径>            保存当前局面",
            "  load <文件路径>            读取存档",
            "  restart                    重新开始当前对局",
            "  hint                       隐藏/显示操作提示",
            "  quit                       退出程序",
        ]
        game = context.get("game")
        if game is not None:
            lines.insert(1, "  当前对局：{}".format(game.game_name()))
        return lines


class ScreenBuilder:
    def __init__(self):
        self._components = []

    def add(self, component):
        self._components.append(component)
        return self

    def build(self):
        return Screen(self._components)


class Screen:
    def __init__(self, components):
        self._components = components

    def render(self, context):
        lines = []
        for component in self._components:
            rendered = component.render(context)
            if rendered:
                lines.extend(rendered)
                lines.append("")
        return "\n".join(lines).rstrip()
