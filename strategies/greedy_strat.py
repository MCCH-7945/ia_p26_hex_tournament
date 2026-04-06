"""Greedy shortest-path strategy.

Picks the move that most reduces your distance to connecting your two
edges, while also considering blocking the opponent.

In dark mode, operates on the visible board only (ignores hidden
opponent stones). May collide occasionally.

Medium-difficulty baseline.
"""

from __future__ import annotations

import random

from strategy import Strategy, GameConfig
from hex_game import shortest_path_distance, empty_cells


class GreedyPathStrategy(Strategy):
    """Greedy heuristic: minimise own shortest-path distance while
    considering opponent blocking.

    Score for each empty cell:
        score = (opponent_dist_after - own_dist_after)

    Picks the cell with highest score (ties broken randomly).
    """

    @property
    def name(self) -> str:
        return "GreedyPath"

    def begin_game(self, config: GameConfig) -> None:
        self._size = config.board_size
        self._player = config.player
        self._opponent = config.opponent

    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        size = self._size
        player = self._player
        opponent = self._opponent

        best_score = float("-inf")
        best_moves: list[tuple[int, int]] = []

        b = [list(row) for row in board]

        for r in range(size):
            for c in range(size):
                if b[r][c] != 0:
                    continue

                b[r][c] = player
                own_dist = shortest_path_distance(b, size, player)
                b[r][c] = 0

                b[r][c] = opponent
                opp_dist = shortest_path_distance(b, size, opponent)
                b[r][c] = 0

                center = size / 2.0
                center_bonus = 1.0 - (abs(r - center) + abs(c - center)) / size
                score = (opp_dist - own_dist) + 0.1 * center_bonus

                if score > best_score:
                    best_score = score
                    best_moves = [(r, c)]
                elif score == best_score:
                    best_moves.append((r, c))

        return random.choice(best_moves)
