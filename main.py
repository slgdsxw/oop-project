"""客户端：控制台命令循环、指令分发与程序入口。"""

from board import Position
from console_ui import BoardComponent, HintComponent, ScreenBuilder, StatusComponent, TitleComponent
from controller import GameController


class ConsoleClient:

    def __init__(self, controller):
        self.controller = controller
        self.hint = HintComponent()
        # 界面"先设计后建造"：逐个添加组件后 build
        self.screen = (ScreenBuilder()
                       .add(TitleComponent("=== 棋类对战平台 ==="))
                       .add(StatusComponent())
                       .add(BoardComponent())
                       .add(self.hint)
                       .build())
        self._running = False

    def run(self):
        """主循环：逐行读取并处理指令，异常输入统一转为错误提示。"""
        self._running = True
        print(self._render())
        while self._running:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            try:
                message = self.handle(line)
            except (ValueError, RuntimeError) as e:
                print("[错误] {}".format(e))
                continue
            if message:
                print(message)
            print(self._render())

    def stop(self):
        """退出主循环。"""
        self._running = False

    def handle(self, line):
        parts = line.split()
        if not parts:
            raise ValueError("请输入指令")
        name = parts[0].lower()
        handlers = {
            "start": self._cmd_start,
            "place": self._cmd_place,
            "pass": self._cmd_pass,
            "undo": self._cmd_undo,
            "resign": self._cmd_resign,
            "save": self._cmd_save,
            "load": self._cmd_load,
            "restart": self._cmd_restart,
            "hint": self._cmd_hint,
            "quit": self._cmd_quit,
        }
        handler = handlers.get(name)
        if handler is None:
            raise ValueError("无法识别的指令：{}（输入 hint 查看帮助）".format(name))
        return handler(parts[1:])

    def _cmd_start(self, args):
        """开始新对局：start <gomoku|go> <大小>。"""
        if len(args) != 2:
            raise ValueError("用法：start <gomoku|go> <大小>")
        game_type = args[0].lower()
        try:
            size = int(args[1])
        except ValueError:
            raise ValueError("棋盘大小必须是整数")
        game = self.controller.new_game(game_type, size)
        return "已开始{}对局，棋盘 {}x{}".format(game.game_name(), size, size)

    def _cmd_place(self, args):
        """落子：place <行> <列>。"""
        if len(args) != 2:
            raise ValueError("用法：place <行> <列>")
        game = self.controller.game
        size = game.board.size if game else None
        pos = Position.parse(args[0] + "," + args[1], size)
        self.controller.place(pos)
        return "落子成功：{} {}".format(args[0], args[1])

    def _cmd_pass(self, args):
        """虚着（仅围棋）。"""
        self.controller.pass_move()
        return "已虚着，轮到对方行棋"

    def _cmd_undo(self, args):
        """悔棋一步。"""
        self.controller.undo()
        return "已悔棋一步"

    def _cmd_resign(self, args):
        """当前行棋方投子认负。"""
        game = self.controller.game
        stone = game.current_stone
        self.controller.resign(stone)
        return "执{}方投子认负，对局结束".format(stone.symbol())

    def _cmd_save(self, args):
        """保存当前局面：save <文件路径>。"""
        if len(args) != 1:
            raise ValueError("用法：save <文件路径>")
        self.controller.save(args[0])
        return "局面已保存到 {}".format(args[0])

    def _cmd_load(self, args):
        """读取存档覆盖当前局面：load <文件路径>。"""
        if len(args) != 1:
            raise ValueError("用法：load <文件路径>")
        game = self.controller.load(args[0])
        return "已读取存档：{}".format(game.game_name())

    def _cmd_restart(self, args):
        """以相同类型和棋盘大小重新开始当前对局。"""
        game = self.controller.game
        if game is None:
            raise RuntimeError("当前没有对局")
        game_type = type(game).__name__
        game_type = "gomoku" if game_type == "GomokuGame" else "go"
        self.controller.new_game(game_type, game.board.size)
        return "已重新开始对局"

    def _cmd_hint(self, args):
        self.hint.toggle()
        if self.hint.visible:
            return "操作提示已显示"
        return "操作提示已隐藏，输入 hint 可重新显示"

    def _cmd_quit(self, args):
        self.stop()
        return "再见"

    def _render(self):
        return self.screen.render({"game": self.controller.game})


def main():
    """程序入口：组装后端控制器并启动客户端。"""
    ConsoleClient(GameController()).run()


if __name__ == "__main__":
    main()
