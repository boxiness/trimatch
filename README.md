# trimatch
A deceptively simple 2-player logic game on a 3×3 grid — part NIM, part Tic-Tac-Toe, all puzzle.

TriMatch

TriMatch is a two-player strategic tile-placement game on a 3×3 grid with a unique twist: forming three identical tiles in a row wins, but forming a mixed line of one Noble, one Knight, and one Mystic causes an instant loss. Two implementations accompany this repository:
    •    trimatch.py — a terminal-only version with text I/O
    •    trimatch_gui.py — a Pygame-based GUI version

⸻

Features
    •    Shared pool of three Nobles (N), three Knights (K), and three Mystics (M)
    •    Placement & replacement: you may place on empty squares or upgrade (replace) a weaker tile (M > K > N)
    •    Win: create a line of three identical ranks (N–N–N, K–K–K, or M–M–M)
    •    Loss: accidentally form a line containing exactly one of each rank (N, K, M)
    •    AI opponent: Minimax with adjustable depth (levels 1–10)
    •    Undo, history, difficulty, hint, help commands

⸻

Installation

Using Poetry (recommended)
    1.    Ensure you have Poetry installed: https://python-poetry.org/docs/#installation
    2.    Clone the repository:

git clone https://github.com/boxiness/trimatch.git
cd trimatch


    3.    Install dependencies:

poetry install


    4.    Run the console version (no extra dependencies):

python trimatch.py


    5.    Run the GUI version:

poetry run python trimatch_gui.py



⸻

Terminal Version (trimatch.py)

Controls via text commands:
    •    Placing tiles: e.g. Nb2 places a Noble at b2 (case-insensitive)
    •    n, n1, n2 — start a new game (choose who starts)
    •    q — quit
    •    h — hint (AI suggestion)
    •    ? — show help text
    •    u — undo last one or two moves
    •    m — show move history
    •    d# — set AI search depth to #
    •    d — display current depth

Sample session:

Player 1 > mb2
Player 2 > ma1
Player 1 > mc3
Player 1 wins with a three-of-a-kind line!


⸻

GUI Version (trimatch_gui.py)

Launches a window with:
    1.    Left: buttons for New Game, Quit, History, Undo, Difficulty+/–, Hint, Help
    2.    Center: 3×3 board with clickable squares and labels a3–c1
    3.    Right: scrollable log of events and messages
    4.    Bottom: stacks of remaining tiles (rendered as images)

Interaction:
    •    Click a stack to pick up a tile, then click a board cell to place/upgrade
    •    Click outside to cancel selection
    •    AI moves are delayed by 500 ms for visibility
    •    Buttons invoke the same commands as the terminal version

⸻

Contributing

Bug reports, feature requests, and pull requests are welcome. Please follow the existing style and update tests (if any).

⸻

License

Released under the GPL-3.0 License. See LICENSE for details.
