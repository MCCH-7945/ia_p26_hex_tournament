"""MCTS strategy with UCT selection.

Strong baseline that uses Monte Carlo Tree Search to choose moves.
Uses the full time budget allocated per move.

In dark mode, uses **determinization**: before each MCTS iteration,
randomly places estimated hidden opponent stones on the board, then
runs the iteration on that "possible world".  This is a standard
technique for imperfect-information games.
"""

from __future__ import annotations

import math
import random
import time
from typing import Sequence

from strategy import Strategy, GameConfig
from hex_game import (
    check_winner,
    empty_cells,
    get_neighbors,
    make_board,
    NEIGHBORS,
)


class _MCTSNode:
    __slots__ = (
        "parent", "move", "player", "children",
        "unexpanded", "N", "Q",
    )

    def __init__(
        self,
        parent: _MCTSNode | None,
        move: tuple[int, int] | None,
        player: int,
        unexpanded: list[tuple[int, int]],
    ):
        self.parent = parent
        self.move = move
        self.player = player
        self.children: list[_MCTSNode] = []
        self.unexpanded = unexpanded
        self.N = 0
        self.Q = 0.0


def _uct_value(child: _MCTSNode, parent_N: int, c: float) -> float:
    if child.N == 0:
        return float("inf")
    return child.Q / child.N + c * math.sqrt(math.log(parent_N) / child.N)


class MCTSStrategy(Strategy):
    """MCTS with UCT selection. Uses available time budget for iterations.

    Classic mode: standard MCTS on the full board.
    Dark mode: determinized MCTS — estimates hidden opponent stones,
    randomly places them before each iteration, then runs MCTS on the
    resulting "possible world".
    """

    @property
    def name(self) -> str:
        return "MCTS_Default"

    def begin_game(self, config: GameConfig) -> None:
        self._size = config.board_size
        self._player = config.player
        self._opponent = config.opponent
        self._time_limit = config.time_limit
        self._c = 1.41
        self._dark = config.variant == "dark"
        # Dark-mode tracking
        self._my_turn_count = 0
        self._known_opponent: set[tuple[int, int]] = set()

    def on_move_result(
        self,
        move: tuple[int, int],
        success: bool,
    ) -> None:
        self._my_turn_count += 1
        if not success:
            self._known_opponent.add(move)

    def play(
        self,
        board: tuple[tuple[int, ...], ...],
        last_move: tuple[int, int] | None,
    ) -> tuple[int, int]:
        size = self._size
        player = self._player

        visible_empty = [
            (r, c) for r in range(size) for c in range(size)
            if board[r][c] == 0
        ]

        if not visible_empty:
            raise RuntimeError("No legal moves")
        if len(visible_empty) == 1:
            return visible_empty[0]

        if self._dark:
            return self._play_dark(board, visible_empty)
        else:
            return self._play_classic(board, visible_empty)

    def _play_classic(
        self,
        board: tuple[tuple[int, ...], ...],
        moves: list[tuple[int, int]],
    ) -> tuple[int, int]:
        """Standard MCTS on full-information board."""
        b = [list(row) for row in board]
        player = self._player

        root = _MCTSNode(
            parent=None, move=None, player=3 - player,
            unexpanded=list(moves),
        )

        t0 = time.monotonic()
        budget = self._time_limit * 0.85

        while time.monotonic() - t0 < budget:
            node = root
            sim_board = [row[:] for row in b]
            sim_moves = set(moves)

            # Selection
            while not node.unexpanded and node.children:
                node = max(
                    node.children,
                    key=lambda ch: _uct_value(ch, node.N, self._c),
                )
                sim_board[node.move[0]][node.move[1]] = node.player
                sim_moves.discard(node.move)

            # Expansion
            if node.unexpanded:
                random.shuffle(node.unexpanded)
                move = node.unexpanded.pop()
                next_player = 1 if node.player == 2 else 2
                remaining = [m for m in sim_moves if m != move]
                child = _MCTSNode(
                    parent=node, move=move, player=next_player,
                    unexpanded=remaining,
                )
                node.children.append(child)
                sim_board[move[0]][move[1]] = next_player
                sim_moves.discard(move)
                node = child

            # Simulation (random rollout)
            result = self._rollout(sim_board, self._size, node.player, sim_moves)

            # Backpropagation
            reward = 1.0 if result == player else 0.0
            while node is not None:
                node.N += 1
                node.Q += reward
                node = node.parent

        if not root.children:
            return random.choice(moves)
        return max(root.children, key=lambda ch: ch.N).move

    def _play_dark(
        self,
        board: tuple[tuple[int, ...], ...],
        visible_empty: list[tuple[int, int]],
    ) -> tuple[int, int]:
        """Determinized MCTS for dark (fog-of-war) mode.

        Before each MCTS iteration:
        1. Estimate how many hidden opponent stones exist.
        2. Randomly place them on cells that appear empty.
        3. Run one MCTS iteration on the resulting board.

        This is called "root determinization" — a standard technique
        for imperfect-information games.
        """
        size = self._size
        player = self._player
        opponent = self._opponent

        # Estimate hidden opponent stones
        # Opponent has had about as many turns as us (±1).
        # Known opponent stones = collisions we've had.
        # Hidden = estimated_opponent_turns - known
        if player == 1:
            est_opponent_turns = self._my_turn_count
        else:
            est_opponent_turns = self._my_turn_count + 1
        known = len(self._known_opponent)
        est_hidden = max(0, est_opponent_turns - known)

        # Build base board from our view
        base = [list(row) for row in board]

        # Cells where we can place hidden opponent stones
        # (appear empty to us but might have opponent stones)
        placeable = [
            (r, c) for r, c in visible_empty
            if base[r][c] == 0
        ]

        # Aggregate visit counts across determinizations
        visit_counts: dict[tuple[int, int], int] = {}
        win_counts: dict[tuple[int, int], float] = {}
        for m in visible_empty:
            visit_counts[m] = 0
            win_counts[m] = 0.0

        t0 = time.monotonic()
        budget = self._time_limit * 0.85
        iterations = 0

        while time.monotonic() - t0 < budget:
            # Determinize: create a possible world
            det_board = [row[:] for row in base]
            if est_hidden > 0 and len(placeable) >= est_hidden:
                hidden_cells = random.sample(placeable, est_hidden)
                for hr, hc in hidden_cells:
                    det_board[hr][hc] = opponent

            # Available moves in this determinization
            det_moves = [
                (r, c) for r in range(size) for c in range(size)
                if det_board[r][c] == 0
            ]
            if not det_moves:
                break

            # One MCTS iteration: pick a move, simulate, record
            move = random.choice(det_moves)
            det_board[move[0]][move[1]] = player
            remaining = set(det_moves) - {move}
            result = self._rollout(
                det_board, size, player, remaining,
            )
            det_board[move[0]][move[1]] = 0  # undo

            if move in visit_counts:
                visit_counts[move] += 1
                win_counts[move] += 1.0 if result == player else 0.0

            iterations += 1

            # Every 200 iterations, do a smarter pass with UCB-like selection
            if iterations % 200 == 0 and iterations > 0:
                # Do a batch of focused simulations on top moves
                top_moves = sorted(
                    visible_empty,
                    key=lambda m: (
                        win_counts[m] / max(visit_counts[m], 1)
                        + 1.41 * math.sqrt(math.log(iterations + 1) / max(visit_counts[m], 1))
                    ),
                    reverse=True,
                )[:10]

                for focus_move in top_moves:
                    det_board2 = [row[:] for row in base]
                    if est_hidden > 0 and len(placeable) >= est_hidden:
                        hidden2 = random.sample(placeable, est_hidden)
                        for hr, hc in hidden2:
                            det_board2[hr][hc] = opponent

                    if det_board2[focus_move[0]][focus_move[1]] != 0:
                        continue

                    det_board2[focus_move[0]][focus_move[1]] = player
                    rem2 = set(
                        (r, c) for r in range(size) for c in range(size)
                        if det_board2[r][c] == 0
                    )
                    res2 = self._rollout(det_board2, size, player, rem2)
                    det_board2[focus_move[0]][focus_move[1]] = 0

                    visit_counts[focus_move] += 1
                    win_counts[focus_move] += 1.0 if res2 == player else 0.0

        # Pick move with best win rate (with enough visits)
        min_visits = max(1, iterations // 50)
        candidates = [
            m for m in visible_empty
            if visit_counts.get(m, 0) >= min_visits
        ]
        if not candidates:
            candidates = visible_empty

        best = max(
            candidates,
            key=lambda m: win_counts.get(m, 0) / max(visit_counts.get(m, 0), 1),
        )
        return best

    def _rollout(
        self,
        board: list[list[int]],
        size: int,
        last_player: int,
        remaining_moves: set[tuple[int, int]],
    ) -> int:
        """Random playout to terminal state. Returns winner (1 or 2)."""
        moves = list(remaining_moves)
        random.shuffle(moves)
        current = 1 if last_player == 2 else 2
        idx = 0

        for move in moves:
            board[move[0]][move[1]] = current
            current = 3 - current
            idx += 1

        winner = check_winner(board, size)

        for move in moves[:idx]:
            board[move[0]][move[1]] = 0

        return winner
