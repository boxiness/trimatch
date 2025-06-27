A deceptively simple 2-player logic game on a 3×3 grid — part NIM, part Tic-Tac-Toe, all puzzle.

# TriMatch

TriMatch is a two-player strategic tile-placement game on a 3×3 grid with a unique twist: forming three identical tiles in a row wins, but forming a mixed line of one Noble, one Knight, and one Mystic causes an instant loss. Two implementations accompany this repository:

* **trimatch.py** — a terminal-only version with text I/O
* **trimatch\_gui.py** — a Pygame-based GUI version

---

## Features

* Shared pool of three Nobles (N), three Knights (K), and three Mystics (M)
* Placement & replacement: place on empty squares or upgrade (replace) a weaker tile (M > K > N)
* **Win**: create a line of three identical ranks (N–N–N, K–K–K, or M–M–M)
* **Loss**: form a line containing exactly one of each rank (N, K, M)
* AI opponent: Minimax with adjustable depth (levels 1–10)
* Undo, history, difficulty, hint, and help commands

---

## Game Design Philosophy

Unlike traditional puzzle games that guarantee a solution, TriMatch embraces the idea that some positions are doomed from the start—just like in life. And because you’re playing against a perfect minimax AI, the game doesn’t ask you to beat it fairly. Instead, it dares you to exploit loopholes, restart ruthlessly, and search for winnable patterns in a landscape that offers no obvious feedback.

There’s no gradient of progress—only sudden cliffs. One misstep may doom you ten turns later, and you’ll never know it until it’s too late. The result? Every move becomes a quiet act of desperation or brilliance, with meaning only revealed in hindsight. TriMatch asks: What does it mean to win when the system is stacked against you?

It’s a “hot potato with bombs”—each player trying to avoid being the last to act when the board explodes. And in doing so, TriMatch becomes a metaphor for survival, strategy, and subversion in a rigged world.

TriMatch began as a brutally difficult game. At first, I felt it needed fixing. But then came a philosophical shift: what if the harshness is the point? TriMatch isn’t about fairness—it’s about confronting a system stacked against you, where the only path forward is to exploit, adapt, and outwit. It reflects a deeper truth: in life, you don’t always win by playing honorably—you win by surviving a rigged game using every tool available.

Modern games often over-coddle players—highlighting objectives, auto-scaling enemies, offering endless tips—removing the challenge and mystery that make games meaningful. This smoothing-over kills the satisfaction of discovery and learning through failure. Older games embraced discomfort, forcing players to think, explore, and fail. That struggle was the point—and the reward. Without it, modern games risk becoming hollow theme park rides instead of true tests of skill and curiosity.

---

## Installation

### Using Poetry (recommended)

1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Clone the repository:

   ```bash
   git clone https://github.com/boxiness/trimatch.git
   cd trimatch
   ```
3. Install dependencies:

   ```bash
   poetry install
   ```
4. Run the console version:

   ```bash
   python trimatch.py
   ```
5. Run the GUI version:

   ```bash
   poetry run python trimatch_gui.py
   ```

### Without Poetry

1. Clone the repository:

   ```bash
   git clone https://github.com/boxiness/trimatch.git
   cd trimatch
   ```
2. Install Pygame (for GUI):

   ```bash
   pip install pygame
   ```
3. Run:

   ```bash
   python trimatch.py
   python trimatch_gui.py
   ```

---

## Terminal Version (`trimatch.py`)

Controls:

* **Placing tiles**: e.g. `Nb2` places a Noble at b2 (case-insensitive)
* `n`, `n1`, `n2` — start a new game (choose who starts)
* `q` — quit
* `h` — hint (AI suggestion)
* `?` — show help text
* `u` — undo last one or two moves
* `m` — show move history
* `d#` — set AI search depth to `#`
* `d` — display current depth

Sample session:

```text
Player 1 > mb2
Player 2 > ma1
Player 1 > mc3
Player 1 wins with a three-of-a-kind line!
```

---

## GUI Version (`trimatch_gui.py`)

Launches a window with:

1. Left: buttons for New Game, Quit, History, Undo, Difficulty+/–, Hint, Help
2. Center: 3×3 board with clickable squares and labels a3–c1
3. Right: scrollable log of events and messages
4. Bottom: stacks of remaining tiles (rendered as images)

**Interaction**:

* Click a stack to pick up a tile, then click a board cell to place or upgrade
* Click outside to cancel selection
* AI moves are delayed by 500 ms for visibility
* Buttons invoke the same commands as the terminal version

---

## Contributing

Bug reports, feature requests, and pull requests are welcome. Please follow the existing style and update tests (if any).

---

## License

Released under the **GPL-3.0 License**. See [LICENSE](LICENSE) for details.
