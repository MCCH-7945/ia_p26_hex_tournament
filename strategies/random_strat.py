"""Random strategy: pick a random empty cell from the visible board."""

from __future__ import annotations

import random

from strategy import Strategy, GameConfig
from hex_game import empty_cells


class RandomStrategy(Strategy):
    """Place a stone on a random cell that appears empty. Weakest baseline.

    Works identically in classic and dark mode — just picks from what
    it can see. In dark mode, may occasionally collide with hidden
    opponent stones (and lose the turn).
    """

    @property
    def name(self) -> str:
        return "Random"

    def begin_game(self, config: GameConfig) -> None:
        self._size = config.board_size

    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        moves = empty_cells(board, self._size)
        return random.choice(moves)
