from game import GomokuGame, GoGame


class GameFactory:
    _registry = {
        "gomoku": GomokuGame,
        "go": GoGame,
    }

    @classmethod
    def available_types(cls):
        return list(cls._registry.keys())

    @classmethod
    def create(cls, game_type, size):
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
    def __init__(self):
        self._game = None

    @property
    def game(self):
        return self._game

    def new_game(self, game_type, size):
        self._game = GameFactory.create(game_type, size)
        return self._game

    def place(self, position):
        self._require_active_game()
        self._game.place(position)

    def pass_move(self):
        self._require_active_game()
        self._game.pass_move()

    def undo(self):
        self._require_game()
        self._game.undo()

    def resign(self, stone):
        self._require_game()
        self._game.resign(stone)

    def _require_game(self):
        if self._game is None:
            raise RuntimeError("当前没有对局，请先开始游戏")

    def _require_active_game(self):
        self._require_game()
        if self._game.finished:
            raise RuntimeError("对局已结束，请重新开始游戏")
