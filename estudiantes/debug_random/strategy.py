"""Debug strategy: random moves. Used to verify auto-discovery works."""

from __future__ import annotations

import random

from strategy import Strategy, GameConfig
from hex_game import empty_cells


class DebugRandomStrategy(Strategy):

    @property
    def name(self) -> str:
        return "DebugRandom_debug"

    def begin_game(self, config: GameConfig) -> None:
        self._size = config.board_size

    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        moves = empty_cells(board, self._size)
        return random.choice(moves)
