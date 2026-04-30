import math
import time
import sys
import pygame
from collections import deque

class TicTacToeState:
    MAX_SYMBOLS = 4
  
    def __init__(self):
        self.board  = [[None] * 3 for _ in range(3)]
        self.queues = {'X': deque(), 'O': deque()}
        self.turn   = 'X'

    def clone(self):
        s = TicTacToeState()
        s.board  = [row[:] for row in self.board]
        s.queues = {'X': deque(self.queues['X']),
                    'O': deque(self.queues['O'])}
        s.turn   = self.turn
        return s

    def key(self):
        flat = tuple(cell or '.' for row in self.board for cell in row)
        return (flat, self.turn)

    def other(self, player):
        return 'O' if player == 'X' else 'X'

    def apply_move(self, row: int, col: int):
        assert self.board[row][col] is None, "Cell already occupied"
        s = self.clone()
        player = s.turn
        #Remove oldest symbol when queue is full (5th-symbol rule)
        if len(s.queues[player]) == self.MAX_SYMBOLS:
            old_r, old_c = s.queues[player].popleft()
            s.board[old_r][old_c] = None

        s.board[row][col] = player
        s.queues[player].append((row, col))
        s.turn = s.other(player)
        return s

    def winner(self):
        b = self.board
        lines = (
            [b[0][0], b[0][1], b[0][2]],
            [b[1][0], b[1][1], b[1][2]],
            [b[2][0], b[2][1], b[2][2]],
            [b[0][0], b[1][0], b[2][0]],
            [b[0][1], b[1][1], b[2][1]],
            [b[0][2], b[1][2], b[2][2]],
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]],
        )
        for line in lines:
            if line[0] and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def is_terminal(self):
        return self.winner() is not None

    def utility(self, maximizing_player='X') -> int:
        w = self.winner()
        if w == maximizing_player:
            return 10
        elif w is not None:
            return -10
        return 0

    def legal_moves(self):
        return [(r, c) for r in range(3) for c in range(3)
                if self.board[r][c] is None]

    def heuristic(self, maximizing_player='X') -> float:
        opp = self.other(maximizing_player)
        b   = self.board
        score = 0

        lines = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
        ]
        for line in lines:
            vals    = [b[r][c] for r, c in line]
            me      = vals.count(maximizing_player)
            opp_cnt = vals.count(opp)

            if opp_cnt == 0:
                score += (10 ** me) if me else 1
            if me == 0:
                score -= (10 ** opp_cnt) if opp_cnt else 1

        #Centre bonus
        if b[1][1] == maximizing_player:
            score += 3
        elif b[1][1] == opp:
            score -= 3

        return score

class AlphaBetaAgent:
    def __init__(self, player: str = 'O', max_depth: int = 6):
        self.player          = player
        self.max_player      = player
        self.max_depth       = max_depth
        self.nodes_evaluated = 0

    def choose_move(self, state: TicTacToeState):
        self.nodes_evaluated = 0
        best_val  = -math.inf
        best_move = None
        alpha, beta = -math.inf, math.inf
        root_visited = {state.key()}

        for move in state.legal_moves():
            child = state.apply_move(*move)
            val   = self._min_value(child, alpha, beta,
                                    depth=1,
                                    visited=root_visited | {child.key()})
            if val > best_val:
                best_val  = val
                best_move = move
            alpha = max(alpha, best_val)

        return best_move

    def _max_value(self, state, alpha, beta, depth, visited):
        self.nodes_evaluated += 1
        if state.is_terminal():
            return state.utility(self.max_player)
        if depth >= self.max_depth:
            return state.heuristic(self.max_player)

        v = -math.inf
        for move in state.legal_moves():
            child = state.apply_move(*move)
            k     = child.key()
            child_val = 0 if k in visited else \
                        self._min_value(child, alpha, beta,
                                        depth + 1, visited | {k})
            v     = max(v, child_val)
            alpha = max(alpha, v)
            if v >= beta:
                break          #beta cut-off
        return v

    def _min_value(self, state, alpha, beta, depth, visited):
        self.nodes_evaluated += 1
        if state.is_terminal():
            return state.utility(self.max_player)
        if depth >= self.max_depth:
            return state.heuristic(self.max_player)

        v = math.inf
        for move in state.legal_moves():
            child = state.apply_move(*move)
            k     = child.key()
            child_val = 0 if k in visited else \
                        self._max_value(child, alpha, beta,
                                        depth + 1, visited | {k})
            v    = min(v, child_val)
            beta = min(beta, v)
            if v <= alpha:
                break          #alpha cut-off
        return v

CELL        = 160          #pixels per cell
MARGIN      = 20           #board margin
PANEL_H     = 110          #status panel height
LINE_W      = 3            #grid line width
SYMBOL_FONT = 85           #symbol font size
INFO_FONT   = 18
BTN_FONT    = 16

BOARD_SIZE  = 3 * CELL + 2 * MARGIN
WIN_W       = BOARD_SIZE
WIN_H       = BOARD_SIZE + PANEL_H

C = {
    'bg':        (30,  30,  46),
    'panel':     (24,  24,  37),
    'cell':      (49,  50,  68),
    'cell_hl':   (69,  71,  90),
    'grid':      (205, 214, 244),
    'X':         (255, 80, 80),     #red
    'O':         (137, 180, 250),   #blue
    'old':       (88,  91, 112),    #faded / about-to-vanish
    'status_ok': (166, 227, 161),   #green
    'status_ai': (250, 179, 135),   #peach
    'status_end':(243, 139, 168),   #pink
    'btn':       (88,  91, 112),
    'btn_hover': (108, 112, 134),
    'btn_text':  (205, 214, 244),
    'white':     (205, 214, 244),

}

class TicTacToeGUI:
    def __init__(self, human: str = 'X', ai_depth: int = 6):
        pygame.init()
        pygame.display.set_caption("Tic-Tac-Toe")

        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock  = pygame.time.Clock()

        self.human_player = human
        self.ai_player    = 'O' if human == 'X' else 'X'
        self.agent        = AlphaBetaAgent(player=self.ai_player,
                                           max_depth=ai_depth)

        # fonts
        self.font_sym  = pygame.font.SysFont('Arial', SYMBOL_FONT, bold=True)
        self.font_info = pygame.font.SysFont('Arial', INFO_FONT)
        self.font_btn  = pygame.font.SysFont('Arial', BTN_FONT, bold=True)

        #button rect (New Game)
        self.btn_rect = pygame.Rect(WIN_W // 2 - 70, BOARD_SIZE + 72, 140, 30)

        self._reset()
        self._run()

    def _reset(self):
        self.state       = TicTacToeState()
        self.game_over   = False
        self.status_msg  = f"Your turn  ({self.human_player})"
        self.status_col  = C['status_ok']
        self.hover_cell  = None
        self.ai_thinking = False
        self.ai_pending  = False   #flag: schedule AI move next frame
        self.last_info   = ""      #nodes / time info line

        #If AI goes first
        if self.state.turn == self.ai_player:
            self.ai_pending = True

    def _cell_at(self, px, py):
        col = (px - MARGIN) // CELL
        row = (py - MARGIN) // CELL
        if 0 <= row < 3 and 0 <= col < 3:
            return int(row), int(col)
        return None

    def _cell_rect(self, row, col):
        x = MARGIN + col * CELL
        y = MARGIN + row * CELL
        return pygame.Rect(x + 2, y + 2, CELL - 4, CELL - 4)

    def _draw(self):
        self.screen.fill(C['bg'])
        self._draw_cells()
        self._draw_grid()
        self._draw_panel()
        pygame.display.flip()

    def _draw_cells(self):
        state = self.state
        for r in range(3):
            for c in range(3):
                rect  = self._cell_rect(r, c)
                hover = (self.hover_cell == (r, c) and
                         not self.game_over and
                         state.turn == self.human_player and
                         state.board[r][c] is None)
                color = C['cell_hl'] if hover else C['cell']
                pygame.draw.rect(self.screen, color, rect, border_radius=8)

                sym = state.board[r][c]
                if sym:
                    q         = state.queues[sym]
                    is_oldest = (len(q) == TicTacToeState.MAX_SYMBOLS and
                                 q[0] == (r, c))
                    sym_color = C['old'] if is_oldest else C[sym]
                    surf = self.font_sym.render(sym, True, sym_color)
                    self.screen.blit(surf,
                                     surf.get_rect(center=rect.center))

    def _draw_grid(self):
        for i in range(1, 3):
            #vertical
            pygame.draw.line(self.screen, C['grid'],
                             (MARGIN + i * CELL, MARGIN),
                             (MARGIN + i * CELL, BOARD_SIZE - MARGIN), LINE_W)
            #horizontal
            pygame.draw.line(self.screen, C['grid'],
                             (MARGIN, MARGIN + i * CELL),
                             (BOARD_SIZE - MARGIN, MARGIN + i * CELL), LINE_W)

    def _draw_panel(self):
        panel = pygame.Rect(0, BOARD_SIZE, WIN_W, PANEL_H)
        pygame.draw.rect(self.screen, C['panel'], panel)

        #status line
        status_surf = self.font_info.render(self.status_msg, True,
                                            self.status_col)
        self.screen.blit(status_surf,
                         status_surf.get_rect(center=(WIN_W // 2,
                                                       BOARD_SIZE + 22)))

        #info line (nodes / time)
        if self.last_info:
            info_surf = self.font_info.render(self.last_info, True,
                                              C['white'])
            self.screen.blit(info_surf,
                             info_surf.get_rect(center=(WIN_W // 2,
                                                         BOARD_SIZE + 46)))

        #New Game button
        mx, my = pygame.mouse.get_pos()
        btn_c  = C['btn_hover'] if self.btn_rect.collidepoint(mx, my) \
                 else C['btn']
        pygame.draw.rect(self.screen, btn_c, self.btn_rect, border_radius=6)
        btn_surf = self.font_btn.render("New Game", True, C['btn_text'])
        self.screen.blit(btn_surf,
                         btn_surf.get_rect(center=self.btn_rect.center))

    def _human_move(self, cell):
        if (self.game_over or
                self.state.turn != self.human_player or
                self.state.board[cell[0]][cell[1]] is not None):
            return
        self._apply_and_check(cell)
        if not self.game_over:
            self.ai_pending = True

    def _do_ai_move(self):
        self.ai_thinking = True
        self.status_msg  = "AI thinking…"
        self.status_col  = C['status_ai']
        self._draw()                    

        t0   = time.time()
        move = self.agent.choose_move(self.state)
        dt   = time.time() - t0

        self.ai_thinking = False
        if move:
            self._apply_and_check(move)
            self.last_info = (f"AI: {dt:.2f}s  |  "
                              f"nodes={self.agent.nodes_evaluated}")
            if not self.game_over:
                self.status_msg = f"Your turn  ({self.human_player})"
                self.status_col = C['status_ok']

    def _apply_and_check(self, cell):
        self.state = self.state.apply_move(*cell)

        winner = self.state.winner()
        if winner:
            self.game_over  = True
            if winner == self.human_player:
                self.status_msg = "You win!"
            else:
                self.status_msg = "AI wins!"
            self.status_col = C['status_end']
        elif not self.state.legal_moves():
            self.game_over  = True
            self.status_msg = "It's a draw!"
            self.status_col = C['status_end']

    def _run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    #New Game button
                    if self.btn_rect.collidepoint(event.pos):
                        self._reset()
                        continue
                    #Board click
                    if not self.game_over and not self.ai_thinking:
                        cell = self._cell_at(*event.pos)
                        if cell:
                            self._human_move(cell)

                elif event.type == pygame.MOUSEMOTION:
                    self.hover_cell = self._cell_at(*event.pos)
            #AI turn (deferred so UI refreshes first)
            if self.ai_pending and not self.game_over:
                self.ai_pending = False
                self._do_ai_move()

            self._draw()
            self.clock.tick(60)

if __name__ == '__main__':
    print("Starting Tic-Tac-Toe")
    print("  Human = X (goes first)   AI = O   depth = 6")
    TicTacToeGUI(human='X', ai_depth=6)
