# Torneo de Hex — IA Primavera 2026 ITAM

Torneo de estrategias de Hex.
Tu equipo implementa **una sola** estrategia que juega Hex en un tablero de **11x11** en dos variantes: **classic** y **dark** (fog of war).
El framework descubre todas las estrategias, las enfrenta contra los defaults, y genera resultados con calificaciones.

---

## Reglas de Hex

Hex se juega en un tablero romboidal de hexagonos. Dos jugadores se alternan colocando piedras:

- **Negro (Player 1)**: conecta el borde superior (fila 0) con el borde inferior (fila N-1).
- **Blanco (Player 2)**: conecta el borde izquierdo (columna 0) con el borde derecho (columna N-1).

**Reglas:**
- No hay capturas — las piedras son permanentes.
- El primer jugador en conectar sus dos bordes gana.
- **No hay empates** en Hex (la geometria hexagonal lo garantiza).
- Cada celda tiene **6 vecinos**: `(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)`.

**Tablero 11x11**: 121 celdas. Espacio de estados enorme — minimax es inviable. Necesitas MCTS, heuristicas, o tecnicas avanzadas.

---

## Dos variantes

### Classic Hex
Tablero vacio al inicio. El juego standard.

### Hex Oscuro (Dark Hex) — Fog of War
Cada jugador **solo ve sus propias piedras** y las piedras del oponente que ha descubierto por **colision**. Una colision ocurre cuando intentas colocar una piedra en una celda que ya tiene una piedra oculta del oponente — pierdes tu turno pero descubres esa piedra.

**Mecanica de colision:**
- Intentas jugar en `(r, c)` que ya tiene una piedra oculta del oponente → **pierdes tu turno**, pero ahora puedes ver esa piedra.
- `on_move_result(move, success)` te informa: `success=True` (se coloco tu piedra) o `success=False` (colision, perdiste el turno).
- `last_move` siempre es `None` en dark mode (no sabes donde jugo el oponente).

Esto:
- Introduce **informacion imperfecta** — debes razonar sobre lo que no puedes ver
- Requiere tecnicas como **determinizacion** o **Information Set MCTS**
- Hace que las colisiones sean un recurso estrategico (exploracion vs explotacion)
- Penaliza estrategias que no manejan la incertidumbre

---

## Setup

```bash
# 1. Forkea el repo en GitHub y clona tu fork
git clone https://github.com/<tu-usuario>/ia_p26_hex_tournament.git
cd ia_p26_hex_tournament

# 2. Instala dependencias (solo numpy y matplotlib)
pip install -r requirements.txt

# 3. Corre un torneo rapido de prueba
python3 run_all.py
```

---

## Que tienes que hacer (estudiantes)

### 1. Crea tu branch y copia el template

```bash
git checkout -b mi_equipo
cp -r estudiantes/_template estudiantes/mi_equipo
```

### 2. Edita `estudiantes/mi_equipo/strategy.py`

```python
from strategy import Strategy, GameConfig
from hex_game import get_neighbors, check_winner, shortest_path_distance, empty_cells

class MiEstrategia(Strategy):
    @property
    def name(self) -> str:
        return "MiEstrategia_mi_equipo"   # <-- nombre unico

    def begin_game(self, config: GameConfig) -> None:
        self._size = config.board_size
        self._player = config.player
        self._opponent = config.opponent
        self._time_limit = config.time_limit

    def on_move_result(self, move, success):
        # Llamado despues de cada play().
        # success=True: tu piedra se coloco. success=False: colision (dark mode).
        pass

    def play(self, board, last_move):
        # ----- TU LOGICA AQUI -----
        # board[r][c]: 0=vacio, 1=Negro, 2=Blanco
        # last_move: (row, col) del oponente, o None (siempre None en dark mode)
        # Debes devolver (row, col) de una celda vacia
        moves = empty_cells(board, self._size)
        return moves[0]  # placeholder — reemplaza con tu logica
```

**Tu estrategia debe funcionar para ambas variantes (classic y dark).**

### 3. Prueba localmente

```bash
# Prueba rapida contra Random (verbose = ves el tablero cada turno)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "Random" --num-games 5 --verbose

# Contra GreedyPath
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "GreedyPath" --num-games 5 --verbose

# Contra MCTS_Default (el mas fuerte)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "MCTS_Default" --num-games 3 --verbose

# Variante dark (fog of war)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "GreedyPath" --variant dark --verbose

# Torneo local rapido (tu estrategia vs todos los defaults)
python3 tournament.py --team mi_equipo --num-games 3

# Torneo local completo (ambas variantes)
python3 tournament.py --team mi_equipo --official --num-games 5
```

### 4. Entrega: abre un Pull Request

```bash
git add estudiantes/mi_equipo/strategy.py
git commit -m "add strategy mi_equipo"
git push origin mi_equipo
```

Luego ve a GitHub y abre un **Pull Request** de tu branch `mi_equipo` hacia `main`.

**Que debe tener tu PR:**
- El archivo `estudiantes/<tu_equipo>/strategy.py` — esto es lo **unico obligatorio**
- Opcionalmente puedes incluir otros archivos en tu directorio (notebooks, scripts, datos) pero no seran evaluados

**Que NO debes incluir en tu PR:**
- Cambios a archivos fuera de `estudiantes/<tu_equipo>/`
- Archivos grandes (`.pkl`, `.npy`, modelos)
- Resultados (`results/`)

---

## Que se evalua y que no

**Solo se ejecuta `estudiantes/<equipo>/strategy.py`** — ese es el unico archivo que el framework importa durante el torneo. Todo tu codigo de estrategia debe estar en ese archivo (una sola clase que hereda de `Strategy`).

Puedes tener otros archivos en tu directorio para desarrollo local:
- Notebooks de analisis y experimentacion
- Scripts auxiliares
- Tablas precomputadas, graficas, resultados locales

Pero **nada de eso sera accesible durante la evaluacion**. El framework solo importa `strategy.py` y ejecuta tu clase. Si necesitas funciones auxiliares, definilas dentro del mismo archivo.

---

## Que informacion recibe tu estrategia

Al inicio de cada juego se llama `begin_game(config)` con un `GameConfig`:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `config.board_size` | `int` | Tamaño del lado del tablero (11) |
| `config.variant` | `str` | `"classic"` o `"dark"` |
| `config.initial_board` | `tuple[tuple[int,...],...]` | Tablero inicial (en dark mode, solo muestra tus piedras) |
| `config.player` | `int` | Tu numero de jugador: 1 (Negro) o 2 (Blanco) |
| `config.opponent` | `int` | Numero del oponente |
| `config.time_limit` | `float` | Segundos maximos por jugada |

En cada turno se llama `play(board, last_move)`:
- `board[r][c]`: 0=vacio, 1=Negro, 2=Blanco
- `last_move`: `(row, col)` del ultimo movimiento del oponente, o `None` si eres el primero (en dark mode siempre es `None`)
- Debes devolver `(row, col)` de una celda vacia

Despues de cada turno se llama `on_move_result(move, success)`:
- `success=True`: tu piedra se coloco correctamente
- `success=False`: colision — la celda ya tenia una piedra oculta del oponente (solo en dark mode)

---

## Calificacion

### Defaults (3 niveles de dificultad)

| Estrategia | Que hace | Dificultad |
|-----------|----------|------------|
| **Random** | Elige una celda vacia al azar | Facil |
| **GreedyPath** | Minimiza su distancia al camino mas corto (Dijkstra) | Media |
| **MCTS_Default** | Monte Carlo Tree Search con UCT (usa todo el presupuesto de tiempo) | Dificil |

### Scoring (basado en umbrales)

Tu estrategia juega **5 partidas** contra cada default por variante (alternando colores). Para "ganar" contra un default necesitas ganar la **mayoria** de las partidas (>=3 de 5).

| Resultado | Puntos |
|-----------|--------|
| No ganas contra ningun default | **0** |
| Ganas contra Random | **6** |
| Ganas contra Random + GreedyPath | **8** |
| Ganas contra Random + GreedyPath + MCTS_Default | **10** |

**Tu calificacion es el umbral mas alto que alcanzas.**

Los **top 3** estudiantes (por total de partidas ganadas) reciben **puntos extra**.

### Torneo oficial

El torneo oficial corre ambas variantes (classic + dark). La calificacion se computa sobre los resultados combinados.

---

## Restricciones de recursos

| Recurso | Limite | Detalle |
|---------|--------|---------|
| **Tiempo** | **10 segundos por jugada** | Estricto via `signal.SIGALRM`. Exceder = pierdes esa partida. |
| **CPU** | **2 cores** | Enforzado via Docker (en evaluacion local puedes usar mas) |
| **Memoria** | **4 GB** | Enforzado via `resource.setrlimit` |
| **Dependencias** | Solo `numpy` + stdlib | No instales ni importes nada mas |

**Presupuesto de tiempo:**
- `begin_game()` **NO** consume tu presupuesto — solo se mide `play()`.
- Tienes 10 segundos **por cada movimiento**. Un juego de ~60 movimientos (~30 por jugador) = ~5 minutos maximo por partida.
- Si haces MCTS, usa `time.monotonic()` para respetar el presupuesto.

---

## Errores comunes y como evitarlos

### Tu estrategia no aparece en el torneo
- Verifica que tu archivo se llame exactamente `strategy.py` y este en `estudiantes/<tu_equipo>/strategy.py`.
- Tu clase debe heredar de `Strategy` (importada de `strategy.py` en la raiz).
- El directorio de tu equipo **no** debe empezar con `_`.

### Timeout (10 segundos por jugada)
- El timeout es **estricto**: si tu `play()` tarda mas de 10 segundos, pierdes esa partida.
- Si usas MCTS, controla el numero de iteraciones con `time.monotonic()`:
  ```python
  import time
  t0 = time.monotonic()
  while time.monotonic() - t0 < self._time_limit * 0.9:
      # una iteracion de MCTS
      ...
  ```

### Movimiento invalido
- `play()` debe devolver `(row, col)` de una celda vacia (`board[r][c] == 0`).
- Si devuelves una celda ocupada o fuera de rango, pierdes la partida.
- Siempre verifica que tu movimiento es legal antes de devolverlo.

### Tu estrategia funciona en classic pero falla en dark
- En la variante `dark`, **solo ves tus propias piedras** y las del oponente descubiertas por colision.
- `last_move` siempre es `None` — no sabes donde jugo el oponente.
- Implementa `on_move_result(move, success)` para rastrear colisiones.
- Las celdas que parecen vacias pueden tener piedras ocultas del oponente.
- Prueba ambas variantes antes de entregar.

### ImportError o ModuleNotFoundError
- Solo puedes usar `numpy` + stdlib. No importes `scipy`, `pandas`, `sklearn`, etc.
- Puedes importar: `from strategy import Strategy, GameConfig` y funciones de `hex_game`.

---

## Comandos

### Un solo comando (recomendado)

```bash
# Prueba rapida (classic, 3 games/pair)
python3 run_all.py

# Torneo oficial (ambas variantes, 5 games/pair)
python3 run_all.py --official

# Solo tu equipo vs defaults
python3 run_all.py --team mi_equipo

# Evaluacion real (10 games/pair, ambas variantes)
python3 run_all.py --real
```

### Evaluacion real (profesor)

```bash
# Torneo de evaluacion: todos los estudiantes vs defaults, 10 games/pair
python3 run_all.py --real

# Custom
python3 run_all.py --real --num-games 20 --seed 42

# Via Docker
docker compose up real-tournament
```

### Torneo (granular)

```bash
# Torneo rapido, solo classic
python3 tournament.py --num-games 5

# Torneo con variante dark (fog of war)
python3 tournament.py --variant dark --num-games 5

# Torneo oficial (ambas variantes)
python3 tournament.py --official --num-games 5

# Solo tu equipo
python3 tournament.py --team mi_equipo --official --num-games 5
```

### Experimento individual

```bash
# Tu estrategia contra Random (verbose: muestra tablero cada turno)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "Random" --verbose

# Contra MCTS
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "MCTS_Default" --num-games 3 --verbose

# Variante dark (fog of war)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "GreedyPath" --variant dark --verbose

# Cambiar timeout (para debug)
python3 experiment.py --black "MiEstrategia_mi_equipo" --white "Random" --move-timeout 30 --verbose
```

---

## Utilidades para tu estrategia

```python
from hex_game import (
    get_neighbors,          # (r, c, size) -> [(nr, nc), ...]
    check_winner,           # (board, size) -> 0, 1, or 2
    shortest_path_distance, # (board, size, player) -> int (Dijkstra)
    empty_cells,            # (board, size) -> [(r, c), ...]
    render_board,           # (board, size) -> str
    NEIGHBORS,              # [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
)

# Ejemplo: distancia del jugador 1 para conectar
dist = shortest_path_distance(board, 11, player=1)

# Ejemplo: vecinos de la celda (3, 5)
nbrs = get_neighbors(3, 5, 11)  # -> [(2,5), (2,6), (3,4), (3,6), (4,4), (4,5)]

# Ejemplo: verificar si alguien gano
winner = check_winner(board, 11)  # 0=nadie, 1=Negro, 2=Blanco
```

---

## Ideas para tu estrategia

1. **MCTS basico**: Implementa Monte Carlo Tree Search con UCT (visto en clase). Usa `time.monotonic()` para respetar el limite de tiempo.

2. **MCTS + heuristica de rollout**: En vez de rollouts puramente aleatorios, sesga los movimientos random hacia celdas que reducen la distancia mas corta.

3. **Heuristica de distancia**: Usa `shortest_path_distance()` para evaluar posiciones. Combina distancia propia y del oponente.

4. **Puentes virtuales**: Detecta patrones de "puente" (dos piedras separadas por un gap que el oponente no puede bloquear) y prioriza completarlos.

5. **MCTS + evaluacion de posicion**: En vez de hacer rollout hasta el final, corta a profundidad fija y evalua con heuristica de distancia.

6. **Transposition table**: Guarda posiciones evaluadas para reutilizar entre iteraciones de MCTS.

7. **Determinizacion (dark mode)**: Antes de cada iteracion MCTS, estima cuantas piedras ocultas tiene el oponente y colocalas aleatoriamente. Corre MCTS sobre ese "mundo posible". Repite con diferentes determinizaciones y agrega resultados.

8. **Information Set MCTS (dark mode)**: En vez de determinizacion simple, mantén un arbol sobre *conjuntos de informacion* — estados que son indistinguibles desde tu perspectiva.

9. **Exploracion estrategica de colisiones (dark mode)**: Colisionar revela informacion. Puedes deliberadamente jugar en celdas donde sospechas que hay piedras ocultas para mapear la posicion del oponente.

---

## Docker (todo en contenedor)

```bash
docker compose up tournament           # torneo oficial (ambas variantes)
docker compose up real-tournament      # evaluacion real
docker compose up experiment           # experimento individual

# Experimento custom
BLACK=MiEstrategia_mi_equipo WHITE=MCTS_Default docker compose up experiment

# Tu equipo
TEAM=mi_equipo docker compose up team-tournament
```

---

## Estructura del repositorio

```
ia_p26_hex_tournament/
├── run_all.py            # Un comando para todo
├── strategy.py           # Clase base (Strategy) + GameConfig
├── hex_game.py           # Motor del juego (tablero, BFS, Dijkstra)
├── tournament.py         # Torneo paralelo (oficial y custom)
├── experiment.py         # Pruebas individuales con output detallado
├── strategies/           # Defaults: Random, GreedyPath, MCTS_Default
├── estudiantes/          # <-- AQUI VA TU ESTRATEGIA
│   ├── _template/        #     Template para copiar
│   └── <tu-equipo>/
│       └── strategy.py   #     Tu estrategia (UNICO archivo evaluado)
├── results/              # Salidas del torneo
│   ├── runs/             #     Historial: results/runs/<timestamp>/
│   └── latest.json       #     Ultimo torneo
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

---

## Outputs

| Archivo | Que es |
|---------|--------|
| `results/runs/<timestamp>/tournament_results.json` | Datos completos del torneo |
| `results/latest.json` | Copia del ultimo torneo ejecutado |
| `results/tournament_official.csv` | CSV: resultados partida por partida |
| `estudiantes/<equipo>/results/` | Resultados locales de tu equipo |
