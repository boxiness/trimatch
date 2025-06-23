import pygame
import sys
import copy
import random
import math
import textwrap
from functools import lru_cache

# --- Game logic functions ---
tile_map = {'n': 1, 'k': 2, 'm': 3}
rev_map = {v: k.upper() for k, v in tile_map.items()}
MAX_GAME_DEPTH = 15
AI_LEVEL = 1
AI_MAX_DEPTH = 1

# Game state variables
board = []
history = []
undo_stack = []
current_player = 1
game_over = False
held_tile = None  # 'n','k','m'
ai_timer = None

# Initialize a new game state
def new_game(start_player=1):
    global board, history, undo_stack, current_player, game_over, held_tile, ai_timer
    board = [[None]*3 for _ in range(3)]
    history = []
    undo_stack = []
    current_player = start_player
    game_over = False
    held_tile = None
    ai_timer = None
    log(f"New game started. Player {current_player} to move.")
    log(f"Current difficulty level is {AI_LEVEL}.")

# Check for win, loss, or draw
def check_outcome(bd):
    lines = []
    for i in range(3):
        lines.append(bd[i])
        lines.append([bd[r][i] for r in range(3)])
    lines.append([bd[i][i] for i in range(3)])
    lines.append([bd[i][2-i] for i in range(3)])
    for line in lines:
        if None not in line and set(line) == {1,2,3}:
            return 'loss'
    for line in lines:
        if None not in line and line[0] == line[1] == line[2]:
            return 'win'
    if all(bd[r][c] is not None for r in range(3) for c in range(3)):
        return 'draw'
    return None

# Count how many tiles of type on board
def count_tile(bd, val):
    return sum(cell == val for row in bd for cell in row)

# Generate all legal moves
def get_possible_moves(bd):
    moves = []
    for r in range(3):
        for c in range(3):
            target = bd[r][c]
            col = chr(ord('a') + c)
            row = str(3 - r)
            for pc, val in tile_map.items():
                if target is None and count_tile(bd, val) < 3:
                    moves.append(f"{pc}{col}{row}")
                elif target is not None and val > target and count_tile(bd, val) < 3:
                    moves.append(f"{pc}{col}{row}")
    return moves

# Apply move to board (in-place)
def apply_move_inplace(bd, m):
    pc, col, row = m[0], m[1], m[2]
    val = tile_map[pc]
    c = ord(col) - ord('a')
    r = 3 - int(row)
    bd[r][c] = val

# Deep apply move, return new board
def apply_move(bd, m):
    newb = [row.copy() for row in bd]
    apply_move_inplace(newb, m)
    return newb

# Key conversion
def board_to_key(bd): return tuple(tuple(row) for row in bd)
def key_to_board(k): return [list(row) for row in k]

# Terminal evaluation
def evaluate_terminal(key, player):
    bd = key_to_board(key)
    res = check_outcome(bd)
    if not res: return None
    last = 3 - player
    if res == 'win': return 1 if last == 1 else -1
    if res == 'loss': return -1 if last == 1 else 1
    return 0

@lru_cache(maxsize=None)
def minimax_score(key, player, depth=0):
    if AI_MAX_DEPTH is not None and depth >= AI_MAX_DEPTH:
        return 0
    term = evaluate_terminal(key, player)
    if term is not None:
        return term * (MAX_GAME_DEPTH - depth)
    bd = key_to_board(key)
    moves = get_possible_moves(bd)
    if player == 1:
        best = -float('inf')
        for m in moves:
            sc = minimax_score(board_to_key(apply_move(bd, m)), 2, depth+1)
            if sc > best: best = sc
        return best
    else:
        worst = float('inf')
        for m in moves:
            sc = minimax_score(board_to_key(apply_move(bd, m)), 1, depth+1)
            if sc < worst: worst = sc
        return worst

# Choose best AI move
def get_best_move(bd):
    if not history:
        return random.choice(get_possible_moves(bd))
    best, bm = -float('inf'), None
    moves = get_possible_moves(bd)
    random.shuffle(moves)
    for m in moves:
        sc = minimax_score(board_to_key(apply_move(bd, m)), 2, 0)
        if sc > best: best, bm = sc, m
    return bm

# Level up
def level_up():
    global AI_LEVEL, AI_MAX_DEPTH
    if AI_LEVEL < 10:
        AI_LEVEL += 1
        AI_MAX_DEPTH = AI_LEVEL
        log(f"You leveled up! AI depth now {AI_LEVEL}.")
    else:
        log("You've beaten the highest level!")

# --- Pygame UI setup ---
pygame.init()
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TriMatch: Gold, Steel & Sorcery")
FONT = pygame.font.SysFont("arial", 18)
clock = pygame.time.Clock()
AI_DELAY = 500

# Colors
WOOD = (170,150,120)
OAK = (200,170,130)
PARCHMENT = (245,238,204)
STONE = (200,200,200)
BLACK = (0,0,0)
GOLD = (212,175,55)
BURGUNDY = (120,26,42)
SILVER = (230,230,230)
SKY = (135,206,235)

# Layout
LEFT_W = 200
BOARD_SIZE = 3*120
BOARD_X = LEFT_W + 50
BOARD_Y = 50
STACK_Y = BOARD_Y + BOARD_SIZE + 100
RIGHT_X = BOARD_X + BOARD_SIZE + 50
RIGHT_W = WIDTH - RIGHT_X - 20

# Buttons
BUTTONS = ["New Game","History","Undo","Difficulty?","Difficulty+","Difficulty-","Hint","Help","Quit"]
button_rects = []
for i, txt in enumerate(BUTTONS):
    button_rects.append((pygame.Rect(10,20+i*50,LEFT_W-20,40), txt))

# Images
N_IMG = pygame.image.load("noble.png").convert_alpha()
K_IMG = pygame.image.load("knight.png").convert_alpha()
M_IMG = pygame.image.load("mystic.png").convert_alpha()
pygame.display.set_icon(N_IMG)

# Sounds
pygame.mixer.init()
pick_snd    = pygame.mixer.Sound("whoosh.ogg")
place_snd   = pygame.mixer.Sound("pebble.ogg")
button_snd  = pygame.mixer.Sound("light-switch.ogg")
win_snd     = pygame.mixer.Sound("achievement.ogg")
lose_snd    = pygame.mixer.Sound("sad-fanfare-short.ogg")
pick_snd.set_volume(0.5)

# Log buffer
log_lines = []
log_offset = 0
MAX_LOG = 50

def log(msg):
    log_lines.append(msg)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current = ""
    for w in words:
        test = current + (" " if current else "") + w
        w_width, _ = font.size(test)
        if w_width <= max_width:
            current = test
        else:
            # start a new sub-line
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# Draw functions
def draw_board():
    if game_over:
        pygame.draw.rect(WIN, BURGUNDY, (BOARD_X-10, BOARD_Y-10, BOARD_SIZE+20, BOARD_SIZE+20), 3)
    else:
        pygame.draw.rect(WIN, STONE, (BOARD_X-10, BOARD_Y-10, BOARD_SIZE+20, BOARD_SIZE+20), 3)
    for i in range(4):
        pygame.draw.line(WIN, BLACK, (BOARD_X+i*120, BOARD_Y), (BOARD_X+i*120, BOARD_Y+BOARD_SIZE), 2)
        pygame.draw.line(WIN, BLACK, (BOARD_X, BOARD_Y+i*120), (BOARD_X+BOARD_SIZE, BOARD_Y+i*120), 2)
    # Labels
    for r in range(3):
        for c in range(3):
            cell = f"{chr(ord('a')+c)}{3-r}"
            WIN.blit(FONT.render(cell, True, BLACK), (BOARD_X+c*120+5, BOARD_Y+r*120+5))
    # Tiles
    for r in range(3):
        for c in range(3):
            v = board[r][c]
            if v:
                draw_tile_image(v, (BOARD_X+c*120+60, BOARD_Y+r*120+60), 80)

def draw_tile_icon(v, pos, size): # deprecated
    x,y = pos
    if v == 1:
        pygame.draw.circle(WIN, GOLD, (x,y), size//2)
        pygame.draw.circle(WIN, BLACK, (x,y), size//2,2)
    elif v == 2:
        pts = [(x,y-size//2), (x-size//2,y+size//2), (x+size//2,y+size//2)]
        pygame.draw.polygon(WIN, SILVER, pts)
        pygame.draw.polygon(WIN, BLACK, pts,2)
    elif v == 3:
        pts = []
        for i in range(5):
            ang = i*72*math.pi/180 - math.pi/2
            pts.append((x+int(size//2*math.cos(ang)), y+int(size//2*math.sin(ang))))
        pygame.draw.polygon(WIN, SKY, pts)
        pygame.draw.polygon(WIN, BLACK, pts,2)

def draw_tile_image(val, pos, size):
    draw_tile_icon (val, pos, size)
    img = {1: N_IMG, 2: K_IMG, 3: M_IMG}[val]
    img_sized = pygame.transform.smoothscale(img, (size, size))
    rect = img_sized.get_rect(center=pos)
    WIN.blit(img_sized, rect)

def draw_stacks():
    # Draw stacks with held tile removed temporarily
    for i, pc in enumerate(['n','k','m']):
        # base available = 3 minus on-board count
        base = 3 - count_tile(board, tile_map[pc])
        # if this pc is held, temporarily remove one
        total = base - (1 if held_tile == pc else 0)
        for j in range(max(total, 0)):
            x = BOARD_X + i*150 + j*30
            y = STACK_Y
            draw_tile_image(tile_map[pc], (x,y), 60)


def draw_buttons():
    for rect, txt in button_rects:
        pygame.draw.rect(WIN, OAK, rect)
        pygame.draw.rect(WIN, BLACK, rect,2)
        WIN.blit(FONT.render(txt, True, BLACK), (rect.x+10, rect.y+10))

def draw_log():
    pygame.draw.rect(WIN, PARCHMENT, (RIGHT_X, 0, RIGHT_W, HEIGHT))
    y = HEIGHT - 20
    max_text_width = RIGHT_W - 20

    # get the last MAX_LOG lines
    for raw_line in reversed(log_lines[-MAX_LOG-log_offset : len(log_lines)-log_offset]):
        # wrap it into sub-lines
        for sub in reversed(wrap_text(raw_line, FONT, max_text_width)):
            WIN.blit(FONT.render(sub, True, BLACK), (RIGHT_X + 10, y - 20))
            y -= 20

def mouse_to_cell(mx, my):
    if BOARD_X < mx < BOARD_X+BOARD_SIZE and BOARD_Y < my < BOARD_Y+BOARD_SIZE:
        c = (mx-BOARD_X)//120
        r = (my-BOARD_Y)//120
        return int(r), int(c)
    return None

# Initialize game
new_game(1)

# Main loop
running = True
while running:
    WIN.fill((180,180,180))
    pygame.draw.rect(WIN, WOOD, (0,0,LEFT_W,HEIGHT))
    draw_buttons()
    draw_board()
    draw_stacks()
    draw_log()
    # draw held tile under cursor
    if held_tile:
        mx,my = pygame.mouse.get_pos()
        draw_tile_image(tile_map[held_tile], (mx, my), 80)

    now = pygame.time.get_ticks()
    # schedule AI move
    if not game_over and current_player == 1 and ai_timer is None:
        ai_timer = now
    # AI move after delay
    if not game_over and current_player == 1 and ai_timer and now - ai_timer >= AI_DELAY:
        move = get_best_move(board)
        ai_timer = None
        undo_stack.append((copy.deepcopy(board), history.copy(), current_player))
        apply_move_inplace(board, move)
        history.append((1, move))
        place_snd.play()
        log(f"Computer played {move.upper()}")
        res = check_outcome(board)
        if res == 'win':
            log("Computer wins! You lose!")
            game_over = True
            lose_snd.play()
        elif res == 'loss':
            log("Computer loses! You win!")
            level_up()
            game_over = True
            win_snd.play()
        else:
            current_player = 2

    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            mx,my = evt.pos
            # button clicks
            for rect, txt in button_rects:
                if rect.collidepoint(mx,my):
                    button_snd.play()
                    if txt == "New Game": new_game(1)
                    elif txt == "Quit": running = False
                    elif txt == "History": log(' | '.join(f"{i+1}.{mv.upper()}" for i,(pl,mv) in enumerate(history)))
                    elif txt == "Undo":
                        if current_player == 2 and game_over: # special case where only undo once
                            if undo_stack:
                                board, history, current_player = undo_stack.pop()
                                game_over = False
                                log("Undid last move.")
                            else:
                                log("Nothing to undo.")
                        else:
                            if len(undo_stack) >= 2:
                                for _ in range(2):
                                    board, history, current_player = undo_stack.pop()
                                game_over = False
                                log("Undid last two moves.")
                            else:
                                log("Nothing to undo.")
                        break
                    elif txt == "Difficulty?":
                        log(f"AI search depth is {AI_MAX_DEPTH}")
                    elif txt == "Difficulty+":
                        AI_MAX_DEPTH += 1
                        log(f"Depth now {AI_MAX_DEPTH}")
                    elif txt == "Difficulty-":
                        AI_MAX_DEPTH = max(1, AI_MAX_DEPTH-1)
                        log(f"Depth now {AI_MAX_DEPTH}")
                    elif txt == "Hint":
                        # Only on your turn, when the game is live
                        if current_player != 2 or game_over:
                            log("Hint only available on your turn in an ongoing game.")
                        else:
                            # Temporarily turn off depth limit
                            old_max = AI_MAX_DEPTH
                            AI_MAX_DEPTH = None
                            # Evaluate each legal human move as if the AI were to play next
                            suggestions = []
                            for m in get_possible_moves(board):
                                sc = minimax_score(board_to_key(apply_move(board, m)), 1, 0)
                                suggestions.append((m.upper(), sc))
                            AI_MAX_DEPTH = old_max
                            best_score = min(s for _, s in suggestions)
                            best_moves = [mv for mv, s in suggestions if s == best_score]
                            if best_score < 0:
                                log("You can force a win with move(s): " + " ".join(best_moves))
                            else:
                                log("No matter what, AI can force a win. Best you can do: " + " ".join(best_moves))

                    elif txt == "Help":
                        # A quick multi‐line tutorial in the log
                        log("In TriMatch: Gold, Steel & Sorcery, you and your rival are the unseen hands of three competing powers—Nobles, Knights, and Mystics—each able to replace only a weaker influence with their own: gold yields to steel, steel to sorcery.")
                        log("On your turn, you either place a tile on an empty district or 'upgrade' a lower-rank tile (returning it to the pool).")
                        log("If you ever line up three of the same ranking in a row, column, or diagonal, you seize control of the city and win;")
                        log("but if you create a line that contains exactly one Noble, one Knight, and one Mystic, their rivalries tear the city apart and you lose.")
                    break
            else:
                # stack clicks
                for i, pc in enumerate(['n','k','m']):
                    x0 = BOARD_X + i*150 - 50
                    y0 = STACK_Y - 25
                    w, h = 150, 60
                    if x0 < mx < x0+w and y0 < my < y0+h:
                        if not held_tile is None:
                            held_tile = None
                        if count_tile(board, tile_map[pc]) < 3:
                            held_tile = pc
                            pick_snd.play()
                        break
                else:
                    # board click
                    if not evt.button == 1:
                        held_tile = None
                    cell = mouse_to_cell(mx,my)
                    if held_tile and cell and not game_over and current_player == 2:
                        r, c = cell
                        target = board[r][c]
                        val = tile_map[held_tile]
                        if target is None or val > target:
                            undo_stack.append((copy.deepcopy(board), history.copy(), current_player))
                            move_str = f"{held_tile}{chr(ord('a')+c)}{3-r}"
                            apply_move_inplace(board, move_str)
                            history.append((2, move_str))
                            place_snd.play()
                            log(f"You played {move_str.upper()}")
                            held_tile = None
                            ai_timer = now
                            res = check_outcome(board)
                            if res == 'win':
                                log("You win!")
                                level_up()
                                game_over = True
                                win_snd.play()
                            elif res == 'loss':
                                log("You lose!")
                                game_over = True
                                lose_snd.play()
                            else:
                                current_player = 1
                        else:
                            log("Invalid move")
                    elif held_tile:
                        # clicked outside grid/stack: unselect
                        held_tile = None

        elif evt.type == pygame.MOUSEBUTTONUP:
            pass

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
