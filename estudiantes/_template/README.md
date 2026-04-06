# Team Template

Copy this directory to create your team workspace:

```bash
cp -r estudiantes/_template estudiantes/your_team_name
```

## Directory Structure

```
estudiantes/your_team_name/
    strategy.py          # YOUR STRATEGY (this is what gets submitted)
    results/             # Auto-created: experiment and tournament outputs
    ...                  # Anything else you want (notebooks, scripts, data)
```

## Quick Start

1. **Edit** `strategy.py` — change the class name, the `name` property, and implement `play()`.

2. **Test** your strategy against Random:
   ```bash
   python experiment.py --black "YourName_teamname" --white "Random" --num-games 5 --verbose
   ```

3. **Compare** against all defaults (Random, GreedyPath, MCTS_Default):
   ```bash
   python tournament.py --team your_team_name --num-games 5
   ```

4. **Run specific configurations:**
   ```bash
   # Dark variant (fog of war)
   python experiment.py --black "YourName_teamname" --white "MCTS_Default" --variant dark --verbose

   # Full local tournament (both variants)
   python tournament.py --team your_team_name --official --num-games 5
   ```

## Rules

- Your strategy must work for **both** variants: `classic` and `dark` (fog of war).
- **10 seconds** max per move (strict timeout — exceeding it = forfeit that game).
- **2 CPU cores** during tournament.
- **4 GB** memory limit per match.
- Only `numpy` + standard library allowed (no extra dependencies).
- No ML/RL pre-trained models. MCTS, minimax, heuristics, simulations are all allowed.
- The `name` property must be unique: `"StrategyName_teamname"`.

## Useful Utilities

```python
from hex_game import (
    get_neighbors,          # (r, c, size) -> list of neighbor cells
    check_winner,           # (board, size) -> 0, 1, or 2
    shortest_path_distance, # (board, size, player) -> int (Dijkstra)
    empty_cells,            # (board, size) -> list of (r, c)
    render_board,           # (board, size) -> str (text visualization)
    NEIGHBORS,              # [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
)
```
