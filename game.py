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

    def pass_move(self):
        if self._finished:
            raise RuntimeError("对局已结束，无法虚着")
        if not self.allow_pass():
            raise RuntimeError("当前棋类不支持虚着")
        self._history.append(MoveRecord(self._current_stone))
        self._switch_turn()
        self._after_pass()

    def undo(self):
        if self._finished:
            raise RuntimeError("对局已结束，无法悔棋")
        if not self._history:
            raise RuntimeError("无棋可悔")
        record = self._history.pop()
        if record.position is not None:
            self._board.set(record.position.row, record.position.col, Stone.EMPTY)
        for r, c in record.captured:
            self._board.set(r, c, record.stone.opposite())
        self._current_stone = record.stone

    def resign(self, stone):
        if self._finished:
            raise RuntimeError("对局已结束")
        self._finish(stone.opposite(), "执{}方投子认负".format(stone.symbol()))

    def _after_pass(self):
        pass

    def snapshot(self):
        return {
            "game": type(self).__name__,
            "size": self._board.size,
            "current": self._current_stone.name,
            "board": [[cell.name for cell in row] for row in self._board._grid],
            "history": [
                {
                    "stone": m.stone.name,
                    "pos": None if m.position is None else [m.position.row, m.position.col],
                    "captured": [list(p) for p in m.captured],
                }
                for m in self._history
            ],
        }

    def restore(self, data):
        size = data["size"]
        if not isinstance(size, int) or size < 8 or size > 19:
            raise ValueError("存档中棋盘大小不合法")
        grid = [[Stone[cell] for cell in row] for row in data["board"]]
        if len(grid) != size or any(len(row) != size for row in grid):
            raise ValueError("存档棋盘数据不合法")
        self._board = Board(size)
        self._board.load_grid(grid)
        self._current_stone = Stone[data["current"]]
        self._history = []
        for m in data["history"]:
            pos = None if m["pos"] is None else Position(m["pos"][0], m["pos"][1])
            captured = [tuple(p) for p in m["captured"]]
            self._history.append(MoveRecord(Stone[m["stone"]], pos, captured))
        self._finished = False
        self._winner = None
        self._result_text = ""

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


class GoGame(Game):
    def __init__(self, size):
        super().__init__(size)
        self._position_history = {self._board.key()}

    def game_name(self):
        return "围棋"

    def allow_pass(self):
        return True

    def try_place(self, position):
        r, c = position.row, position.col
        if not self._board.in_bounds(r, c):
            raise ValueError("落子位置超出棋盘范围")
        if self._board.get(r, c) is not Stone.EMPTY:
            raise ValueError("该位置已有棋子")
        stone = self._current_stone
        opponent = stone.opposite()
        self._board.set(r, c, stone)
        captured = self._capture_groups(opponent)
        if not captured and self._group_liberty(r, c) == 0:
            self._board.set(r, c, Stone.EMPTY)
            raise ValueError("落子后己方棋子无气，不允许自杀")
        new_key = self._board.key()
        if new_key in self._position_history:
            for rr, cc in captured:
                self._board.set(rr, cc, opponent)
            self._board.set(r, c, Stone.EMPTY)
            raise ValueError("落子违反打劫规则（禁止全局同形）")
        self._position_history.add(new_key)
        self._history.append(MoveRecord(stone, position, captured))
        if self._board.is_full():
            self._score_and_finish()

    def _after_pass(self):
        if len(self._history) >= 2 and \
                self._history[-1].position is None and \
                self._history[-2].position is None:
            self._score_and_finish()

    def _neighbors(self, r, c):
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if self._board.in_bounds(nr, nc):
                yield nr, nc

    def _collect_group(self, r, c):
        color = self._board.get(r, c)
        group = {(r, c)}
        frontier = [(r, c)]
        while frontier:
            cr, cc = frontier.pop()
            for nr, nc in self._neighbors(cr, cc):
                if (nr, nc) not in group and self._board.get(nr, nc) is color:
                    group.add((nr, nc))
                    frontier.append((nr, nc))
        return group

    def _group_liberty(self, r, c):
        color = self._board.get(r, c)
        liberties = set()
        for gr, gc in self._collect_group(r, c):
            for nr, nc in self._neighbors(gr, gc):
                if self._board.get(nr, nc) is Stone.EMPTY:
                    liberties.add((nr, nc))
        return len(liberties)

    def _capture_groups(self, color):
        captured = []
        seen = set()
        for r, c in list(self._board.occupied()):
            if self._board.get(r, c) is not color or (r, c) in seen:
                continue
            group = self._collect_group(r, c)
            seen |= group
            has_liberty = False
            for gr, gc in group:
                for nr, nc in self._neighbors(gr, gc):
                    if self._board.get(nr, nc) is Stone.EMPTY:
                        has_liberty = True
                        break
                if has_liberty:
                    break
            if not has_liberty:
                for gr, gc in group:
                    self._board.set(gr, gc, Stone.EMPTY)
                captured.extend(sorted(group))
        return captured

    def _score_and_finish(self):
        black = self._board.count(Stone.BLACK)
        white = self._board.count(Stone.WHITE)
        visited = set()
        for r in range(self._board.size):
            for c in range(self._board.size):
                if self._board.get(r, c) is not Stone.EMPTY or (r, c) in visited:
                    continue
                region = {(r, c)}
                frontier = [(r, c)]
                borders = set()
                while frontier:
                    cr, cc = frontier.pop()
                    for nr, nc in self._neighbors(cr, cc):
                        cell = self._board.get(nr, nc)
                        if cell is Stone.EMPTY:
                            if (nr, nc) not in region:
                                region.add((nr, nc))
                                frontier.append((nr, nc))
                        else:
                            borders.add(cell)
                visited |= region
                if borders == {Stone.BLACK}:
                    black += len(region)
                elif borders == {Stone.WHITE}:
                    white += len(region)
        komi = 7.5
        if black > white + komi:
            self._finish(Stone.BLACK, "黑{} 白{}（贴{}目），黑胜".format(black, white, komi))
        elif white + komi > black:
            self._finish(Stone.WHITE, "黑{} 白{}（贴{}目），白胜".format(black, white, komi))
        else:
            self._finish(None, "黑{} 白{}（贴{}目），平局".format(black, white, komi))
