"""平台后端门面：游戏工厂与对局控制"""

import json

from game import GomokuGame, GoGame


class GameFactory:
    """注册表式工厂：按类型字符串创建对应的对局对象"""

    _registry = {
        "gomoku": GomokuGame,
        "go": GoGame,
    }

    @classmethod
    def available_types(cls):
        return list(cls._registry.keys())

    @classmethod
    def create(cls, game_type, size):
        """创建指定类型的对局；统一校验类型与棋盘大小（8~19）"""
        cls._check_size(size)
        game_cls = cls._registry.get(game_type)
        if game_cls is None:
            raise ValueError("不支持的游戏类型：{}".format(game_type))
        return game_cls(size)

    @staticmethod
    def _check_size(size):
        if not isinstance(size, int) or size < 8 or size > 19:
            raise ValueError("棋盘大小必须在 8 到 19 之间")


class GameController:
    """客户端访问后端的唯一入口"""

    def __init__(self):
        self._game = None

    @property
    def game(self):
        return self._game

    def new_game(self, game_type, size):
        """开一局新游戏并覆盖当前对局"""
        self._game = GameFactory.create(game_type, size)
        return self._game

    def place(self, position):
        """在当前位置落子"""
        self._require_active_game()
        self._game.place(position)

    def pass_move(self):
        """虚着（仅围棋支持）"""
        self._require_active_game()
        self._game.pass_move()

    def undo(self):
        """悔棋一步"""
        self._require_game()
        self._game.undo()

    def resign(self, stone):
        """stone 方投子认负"""
        self._require_game()
        self._game.resign(stone)

    def save(self, path):
        """把当前局面快照写入 JSON 文件"""
        self._require_game()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._game.snapshot(), f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise RuntimeError("保存局面失败：{}".format(e))

    def load(self, path):
        """读取存档文件并覆盖当前局面，返回新的对局对象"""

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except OSError as e:
            raise RuntimeError("读取存档失败：{}".format(e))
        except json.JSONDecodeError:
            raise RuntimeError("存档文件格式不合法")
        # 按存档中的类名找到对应棋类
        game_cls = {c.__name__: c for c in (GomokuGame, GoGame)}.get(data.get("game"))
        if game_cls is None:
            raise ValueError("存档中游戏类型不合法")
        game = game_cls(data.get("size", 0))
        try:
            game.restore(data)
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError("存档数据不合法：{}".format(e))
        self._game = game
        return game

    def _require_game(self):

        if self._game is None:
            raise RuntimeError("当前没有对局，请先开始游戏")

    def _require_active_game(self):
        """操作前检查对局存在且尚未结束"""

        self._require_game()
        if self._game.finished:
            raise RuntimeError("对局已结束，请重新开始游戏")
