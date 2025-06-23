import copy
import random
from functools import lru_cache

AI_LEVEL = 1
AI_MAX_DEPTH = 1
MAX_GAME_DEPTH = 15

# Mapping piece characters to values and back
tile_map = {'n': 1, 'k': 2, 'm': 3}
rev_map = {v: k.upper() for k, v in tile_map.items()}

# Initialize a new game state
def new_game(start_player=1):
    board = [[None]*3 for _ in range(3)]
    history = []          # list of (player, move_str)
    undo_stack = []       # stack of (board, history, player)
    return board, history, undo_stack, start_player, False

# Display the board
def print_board(board):
    print("   a   b   c")
    print(" +---+---+---+")
    for r in range(3):
        row_label = 3 - r
        row_vals = []
        for c in range(3):
            val = board[r][c]
            row_vals.append(rev_map[val] if val else ' ')
        print(f"{row_label}| {row_vals[0]} | {row_vals[1]} | {row_vals[2]} |")
        print(" +---+---+---+")

# Check for win, loss, or draw
def check_outcome(board):
    lines = []
    for i in range(3):
        lines.append(board[i])
        lines.append([board[r][i] for r in range(3)])
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2-i] for i in range(3)])
    # Loss: any 1-2-3 line
    for line in lines:
        if None not in line and set(line) == {1,2,3}:
            return 'loss'
    # Win: three identical
    for line in lines:
        if None not in line and line[0] == line[1] == line[2]:
            return 'win'
    # Draw: full board
    if all(board[r][c] is not None for r in range(3) for c in range(3)):
        return 'draw'
    return None

# Count how many tiles of a given type are on board
def count_tile(board, val):
    return sum(cell == val for row in board for cell in row)

# Generate all legal moves given a board state
def get_possible_moves(board):
    moves = []
    for r in range(3):
        for c in range(3):
            target = board[r][c]
            col_char = chr(ord('a') + c)
            row_char = str(3 - r)
            for piece_char, val in tile_map.items():
                if target is None:
                    if count_tile(board, val) < 3:
                        moves.append(f"{piece_char}{col_char}{row_char}")
                else:
                    if val > target and count_tile(board, val) < 3:
                        moves.append(f"{piece_char}{col_char}{row_char}")
    return moves

# Apply a move to a board and return new board
def apply_move(board, move_str):
    piece_char, col_char, row_char = move_str[0], move_str[1], move_str[2]
    val = tile_map[piece_char]
    c = ord(col_char) - ord('a')
    r = 3 - int(row_char)
    new_board = [row.copy() for row in board]
    new_board[r][c] = val
    return new_board

# Helpers to convert board to a cacheable key
def board_to_key(board):
    return tuple(tuple(row) for row in board)

def key_to_board(key):
    return [list(row) for row in key]

# Minimax scoring with LRU cache
def evaluate_terminal(board_key, current_player):
    board = key_to_board(board_key)
    result = check_outcome(board)
    if not result:
        return None
    last_player = 3 - current_player
    if result == 'win':
        return 1 if last_player == 1 else -1
    if result == 'loss':
        return -1 if last_player == 1 else 1
    return 0  # draw

@lru_cache(maxsize=None)
def minimax_score(board_key, current_player, depth=0):
    if AI_MAX_DEPTH is not None and depth >= AI_MAX_DEPTH:
    # at max depth, fall back to a flat heuristic: 0 for “unknown/draw”
        return 0
    terminal = evaluate_terminal(board_key, current_player)
    if terminal is not None:
        # earlier wins/losses are more extreme
        return terminal * (MAX_GAME_DEPTH - depth)
    board = key_to_board(board_key)
    moves = get_possible_moves(board)
    if current_player == 1:
        best = -float('inf')
        for m in moves:
            new_key = board_to_key(apply_move(board, m))
            score = minimax_score(new_key, 2, depth+1)
            if score > best:
                best = score
                if best == 1:
                    break
        return best
    else:
        worst = float('inf')
        for m in moves:
            new_key = board_to_key(apply_move(board, m))
            score = minimax_score(new_key, 1, depth+1)
            if score < worst:
                worst = score
                if worst == -1:
                    break
        return worst

# Choose the best move for AI (player 1)
def get_best_move(board, history):
    if not history:
        return random.choice(get_possible_moves(board))
    best = -float('inf')
    best_move = None
    moves = get_possible_moves(board)
    random.shuffle(moves)
    for m in moves:
        score = minimax_score(board_to_key(apply_move(board, m)), 2)
        if score > best:
            best = score
            best_move = m
    return best_move

def level_up():
    global AI_LEVEL, AI_MAX_DEPTH
    if AI_LEVEL < 10:
        AI_LEVEL += 1
        AI_MAX_DEPTH = AI_LEVEL
        print(f"You leveled up! AI is now at depth {AI_LEVEL}.")
    else:
        print("🎉 Congratulations! You’ve beaten TriMatch at the highest level! 🎉")

# Main game loop
def main():
    global AI_MAX_DEPTH
    board, history, undo_stack, current_player, game_over = new_game(1)
    while True:
        print_board(board)
        if not game_over and current_player == 1:
            cmd = get_best_move(board, history)
            print(f"Player 1 (Computer) > {cmd.upper()}")
        else:
            cmd = input(f"Player {current_player} > ").strip().lower()

        # Handle quit/new/history/undo/helper commands
        if cmd == '?':
            print("")
        if cmd == 'q':
            print("Quitting game.")
            break
        if cmd in ('n', 'n1', 'n2'):
            starter = 1 if cmd != 'n2' else 2
            board, history, undo_stack, current_player, game_over = new_game(starter)
            continue
        if cmd == 'm':
            if not history:
                print("No moves made yet.")
            else:
                for i, (pl, mv) in enumerate(history, start=1):
                    print(f"{i}. Player {pl}: {mv.upper()}")
            continue
        if cmd == 'u':
            if len(undo_stack) < 2:
                print("Nothing to undo.")
            else:
                # pop twice: AI move + your last move
                for _ in range(2):
                    board, history, current_player = undo_stack.pop()
                game_over = False
                print("Last two moves undone; back to your turn.")
            continue
        if cmd == 'd':
            print(f"AI difficulty set to depth {AI_MAX_DEPTH}")
            continue
        # Adjust difficulty
        if cmd.startswith('d') and cmd[1:].isdigit():
            AI_MAX_DEPTH = int(cmd[1:])
            print(f"AI difficulty set to depth {AI_MAX_DEPTH}")
            continue
        # AI‐helper command
        if cmd == 'h':
            if current_player != 2 or game_over:
                print("Help is only available on your (Player 2’s) turn in an ongoing game.")
            else:
                # temporarily disable depth limit
                old_max = AI_MAX_DEPTH
                AI_MAX_DEPTH = None
                # Evaluate each legal human move by “what minimax would score it for the AI next turn”
                suggestions = []
                for m in get_possible_moves(board):
                    next_key = board_to_key(apply_move(board, m))
                    # After I move, it's AI's turn (player 1)
                    score = minimax_score(next_key, 1)
                    # score == 1 → AI wins, 0 → draw, -1 → AI loses
                    suggestions.append((m.upper(), score))
                # restore depth limit
                AI_MAX_DEPTH = old_max
                # Find the best outcome from human’s POV (minimize AI’s score)
                best_score = min(s for _, s in suggestions)
                best_moves = [mv for mv, s in suggestions if s == best_score]
                if best_score < 0:
                    print("You can force a win with move(s):", ' '.join(best_moves))
                elif best_score == 0:
                    print("You can force at least a draw with move(s):", ' '.join(best_moves))
                else:
                    print("No matter what, AI can force a win. Best you can do:", ' '.join(best_moves))
            continue
        # Show full help text
        if cmd == '?':
            print("""
TriMatch Help
=============
Game Rules:
  • 3×3 grid, cols a-b-c, rows 1-2-3
  • Tiles: N=Noble, K=Knight, M=Mystic; there are 3 of each
  • On your turn, place on empty or replace a lower rank tile (e.g., Mb2)
  • Win by making three of the same in a line (e.g., N-N-N)
  • Lose immediately if you make an N-K-M (any order) line

Commands:
  q     Quit game
  n, n1 New game (Player 1 starts)
  n2    New game (Player 2 starts)
  m     Show move history
  u     Undo last two moves (AI + your last)
  d     Show current AI difficulty
  d#    Set AI difficulty to lookahead depth #
  h     Hint for best human move (AI‐helper)
  ?     Show this help text
""")
            continue
            
        # Move input handling
        if game_over:
            print("Game over. Enter 'n' to start a new game.")
            continue
        if len(cmd) == 3 and cmd[0] in tile_map and cmd[1] in 'abc' and cmd[2] in '123':
            piece_val = tile_map[cmd[0]]
            col = ord(cmd[1]) - ord('a')
            row = 3 - int(cmd[2])
            target = board[row][col]
            # Validate move
            if target is None:
                if count_tile(board, piece_val) >= 3:
                    print("Invalid move: no more of that tile available.")
                    continue
            else:
                if piece_val <= target or count_tile(board, piece_val) >= 3:
                    print("Invalid move: can only replace with a higher tile and within pool limits.")
                    continue
            # Save for undo
            undo_stack.append((copy.deepcopy(board), history.copy(), current_player))
            board = apply_move(board, cmd)
            history.append((current_player, cmd))
            # Check outcome
            result = check_outcome(board)
            if result == 'loss':
                print_board(board)
                if current_player == 1:
                    # AI just lost
                    print("Computer loses by forming an N-K-M line! You win!")
                    level_up()
                else:
                    # Human just lost
                    print("You lose by forming an N-K-M line! Computer wins!")
                game_over = True
            elif result == 'win':
                print_board(board)
                if current_player == 1:
                    # AI just won
                    print("Computer wins with a three-of-a-kind! You lose!")
                else:
                    # Human just won
                    print("You win with a three-of-a-kind! Computer loses!")
                    level_up()
                game_over = True
            elif result == 'draw':
                print_board(board)
                print("Game ends in a draw. This should never happen!")
                game_over = True
            else:
                current_player = 3 - current_player
        else:
            print("Invalid input: enter a move like 'Mb2' or a command (q, n, n1, n2, m, h, u, d, d#, ?).")

if __name__ == '__main__':
    main()
