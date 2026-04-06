"""Strategy template — copy this directory to estudiantes/<your_team>/

Rename the class and the ``name`` property, then implement your logic
in the ``play`` method.
"""

from __future__ import annotations

import random

from strategy import Strategy, GameConfig
from hex_game import (
    get_neighbors,
    check_winner,
    shortest_path_distance,
    empty_cells,
)


class MyStrategy(Strategy):
    """Example strategy — replace with your own logic."""

    @property
    def name(self) -> str:
        # Convention: "StrategyName_teamname"
        return "MyStrategy_teamname"  # <-- CHANGE THIS

    def begin_game(self, config: GameConfig) -> None:
        """Called once at the start of each game.

        Available information in config:
          - config.board_size      (int)   — side length (default 11)
          - config.variant         (str)   — "classic" or "dark"
          - config.initial_board   (tuple) — starting board state (in dark: only your stones)
          - config.player          (int)   — your player number (1=Black, 2=White)
          - config.opponent        (int)   — opponent's number
          - config.time_limit      (float) — max seconds per move

        Player 1 (Black): connects top (row 0) to bottom (row N-1).
        Player 2 (White): connects left (col 0) to right (col N-1).

        Board cell values: 0=empty, 1=Black, 2=White.

        Dark mode (fog of war):
          - You only see your own stones + opponent stones discovered by collision.
          - last_move is always None (you don't know where the opponent played).
          - on_move_result(move, success) tells you if your move collided.
        """
        self._size = config.board_size
        self._player = config.player
        self._opponent = config.opponent
        self._variant = config.variant

    def on_move_result(
        self,
        move: tuple[int, int],
        success: bool,
    ) -> None:
        """Called after each play() with the result.

        Parameters
        ----------
        move : tuple[int, int]
            The move you just played.
        success : bool
            True if your stone was placed. False if collision (dark mode only):
            the cell had a hidden opponent stone — you lose your turn but now
            see that stone.
        """
        pass  # Track collisions here for dark mode

    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        """Return (row, col) where you want to place your stone.

        Parameters
        ----------
        board : tuple[tuple[int, ...], ...]
            Current board state.  board[r][c] is:
              0 = empty, 1 = Black, 2 = White.
            In dark mode: only shows your stones and collision-discovered
            opponent stones. Cells that appear empty may have hidden
            opponent stones.
        last_move : tuple[int, int] or None
            Opponent's last move (row, col), or None if you move first.
            Always None in dark mode.

        Returns
        -------
        tuple[int, int]
            (row, col) of the cell where you place your stone.
            Must be empty (board[r][c] == 0).

        Available utility functions:
          - get_neighbors(r, c, size) → list of valid neighbor cells
          - check_winner(board, size) → 0 (no winner), 1, or 2
          - shortest_path_distance(board, size, player) → int
          - empty_cells(board, size) → list of (r,c) empty cells
        """
        # -------------------------------------------------------
        # YOUR LOGIC HERE
        # Replace the line below with your strategy.
        # -------------------------------------------------------
        moves = empty_cells(board, self._size)
        return random.choice(moves)
