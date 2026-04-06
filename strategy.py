"""Abstract base class for Hex strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """All information a strategy receives at the start of each game.

    Attributes
    ----------
    board_size : int
        Side length of the hex board (default 11).
    variant : str
        Game variant: ``"classic"`` (full information) or ``"dark"``
        (fog of war — you only see your own stones and opponent
        stones discovered via collisions).
    initial_board : tuple[tuple[int, ...], ...]
        Board state at the start of the game from YOUR perspective.
        In classic mode, this is the full empty board.
        In dark mode, this is your initial view (all zeros).
        Cell values: 0 = empty (or hidden), 1 = Black, 2 = White.
    player : int
        Your player number: 1 (Black) or 2 (White).
        - Black connects top (row 0) to bottom (row N-1).
        - White connects left (col 0) to right (col N-1).
    opponent : int
        Opponent's player number (3 - player).
    time_limit : float
        Maximum seconds allowed per move (strict).
    """

    board_size: int
    variant: str
    initial_board: tuple[tuple[int, ...], ...]
    player: int
    opponent: int
    time_limit: float


class Strategy(ABC):
    """Interface that every Hex strategy must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name (used in reports)."""
        ...

    def begin_game(self, config: GameConfig) -> None:
        """Called at the start of each game.

        Use this for precomputation (e.g. building data structures).
        The *config* object provides full game information: board size,
        variant, initial board state, your player number, and time limit.

        The default implementation does nothing.
        """

    @abstractmethod
    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        """Return the (row, col) where you want to place your stone.

        Parameters
        ----------
        board : tuple[tuple[int, ...], ...]
            Current board state from YOUR perspective.
            - Classic mode: full board (``board[r][c]`` is 0, 1, or 2).
            - Dark mode: only your stones and collision-discovered
              opponent stones are visible.  Hidden opponent stones
              appear as 0 (empty).
        last_move : tuple[int, int] or None
            - Classic mode: opponent's last move ``(row, col)``, or
              ``None`` if you move first.
            - Dark mode: always ``None`` (you cannot see opponent moves).

        Returns
        -------
        tuple[int, int]
            ``(row, col)`` of the cell where you place your stone.
            Must appear empty in YOUR view (``board[r][c] == 0``).
            In dark mode, if the cell is secretly occupied by the
            opponent, a **collision** occurs: your turn is consumed
            (no stone placed) and ``on_move_result`` is called with
            ``success=False``.
        """
        ...

    def on_move_result(
        self,
        move: tuple[int, int],
        success: bool,
    ) -> None:
        """Called after ``play()`` to report the outcome of your move.

        Parameters
        ----------
        move : tuple[int, int]
            The ``(row, col)`` you returned from ``play()``.
        success : bool
            - ``True``: your stone was placed successfully.
            - ``False``: **collision** — an opponent stone was already
              on that cell (dark mode only).  Your turn is consumed.
              The next call to ``play()`` will show the opponent stone
              at this cell in your board view.

        In classic mode, this is always called with ``success=True``
        (invalid moves cause forfeit before this is called).

        The default implementation does nothing.
        """

    def end_game(
        self,
        board: tuple[tuple[int, ...], ...],
        winner: int,
        your_player: int,
    ) -> None:
        """Called at the end of each game.

        Parameters
        ----------
        board : tuple[tuple[int, ...], ...]
            The FULL final board (both players' stones visible),
            regardless of variant.
        winner : int
            1 (Black won) or 2 (White won).
        your_player : int
            Your player number.

        The default implementation does nothing.
        """
