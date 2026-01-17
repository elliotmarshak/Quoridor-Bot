#Imports and constants
import pygame

class Graphics:
    def __init__(self, screen, font, cell_size, sidebar_width, gap):
        # Use screen and font provided by main.py to keep single display
        self.screen = screen
        self.font = font
        self.cell_size = cell_size
        self.sidebar_width = sidebar_width
        self.width = cell_size * 9 + sidebar_width
        self.height = cell_size * 9
        self.gap = gap
        self.clock = pygame.time.Clock()

    def draw_grid(self): #draws the 9x9 grid
        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def draw_pawns(self, board): #draw the player pawns as circles
        for player in range(2):
            row, col = board.pawns[player]
            color = (200, 50, 50) if player == 0 else (50, 50, 200)
            pygame.draw.circle(
                self.screen, color,
                (col * self.cell_size + self.cell_size // 2, row * self.cell_size + self.cell_size // 2),
                self.cell_size // 3
            )

    def draw_walls(self, board): #draw both horizontal and vertical walls
        thickness = self.cell_size // 6
        for (r, c, orientation) in board.walls:
            if orientation == "H":
                #Horizontal wall: starts at the top-left corner of (r,c) and extends two squares to the right
                rect = pygame.Rect(
                    (c) * self.cell_size + self.gap, 
                    (r) * self.cell_size - thickness//2, 
                    2*self.cell_size - 2*self.gap, 
                    thickness
                )

            else: #vertical
                #Vertical wall: bottom-right corner of (r,c) 2 squares up
                rect = pygame.Rect(
                    (c + 1) * self.cell_size - thickness//2,
                    (r - 1) * self.cell_size + self.gap,
                    thickness, 
                    2*self.cell_size - 2*self.gap
                    )
            pygame.draw.rect(self.screen, (100, 100, 100), rect)

    def draw_sidebar(self, board, error_message): #sidebar displays wall counts
        sidebar_rect = pygame.Rect(self.cell_size * 9, 0, self.sidebar_width, self.height)
        pygame.draw.rect(self.screen, (220, 220, 220), sidebar_rect)

        text = self.font.render(f"P1 Walls: {board.walls_remaining[0]}", True, (0, 0, 0))
        self.screen.blit(text, (self.cell_size * 9 + 10, 10))

        text = self.font.render(f"P2 Walls: {board.walls_remaining[1]}", True, (0, 0, 0))
        self.screen.blit(text, (self.cell_size * 9 + 10, 40))

        #Wall selectors that you can drag
        pygame.draw.rect(self.screen, (100, 100, 100), (self.cell_size * 9 + 50, 80, 2 * self.cell_size, self.cell_size // 6))
        pygame.draw.rect(self.screen, (100, 100, 100), (self.cell_size * 9 + 50, 150, self.cell_size // 6, 2 * self.cell_size))

        if error_message: #display error message if there is one
            txt = self.font.render(error_message, True, (200, 0, 0))
            self.screen.blit(txt, (self.cell_size * 9 + 10, 220))

    def draw_win_message(self, winner, mode): #display the win message with a nice dark overlay
        if winner is None:
            return
        
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if winner == 0:
            player_name = "Player 1"
        else:
            player_name = "Player 2"

        if mode == 1:
            if winner == 0:
                player_name = "Human"
            else:
                player_name = "Bot"

        elif mode == 2:
            if winner == 0:
                player_name = "Bot"
            else:
                player_name = "Human"

        elif mode == 3:
            player_name = f"Bot {winner + 1}" #winner is either 0 or 1 so add 1

        win_text = self.font.render(f"{player_name} Wins!", True, (255, 255, 0)) #yellow
        text_rect = win_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(win_text, text_rect)

    def draw_legal_moves(self, legal_moves): #highlights the squares the selected pawn can move to in green
        for row, col in legal_moves:
            pygame.draw.circle(self.screen, (0, 200, 0), (col * self.cell_size + self.cell_size // 2, row * self.cell_size + self.cell_size // 2), self.cell_size // 6)

    def draw_ghost_wall(self, dragging_wall):
        if not dragging_wall:
            return
        mx, my = pygame.mouse.get_pos()
        col = mx // self.cell_size
        row = my // self.cell_size

        #Determine the rectangle
        if dragging_wall == "H":
            wall_x = col * self.cell_size
            wall_y = row * self.cell_size
            rect = pygame.Rect(wall_x, wall_y, 2 * self.cell_size, self.cell_size // 6)
        else:
            thickness = self.cell_size // 6
            wall_x = (col + 1) * self.cell_size - thickness
            wall_y = (row - 1) * self.cell_size
            rect = pygame.Rect(wall_x, wall_y, thickness, 2 * self.cell_size)

        pygame.draw.rect(self.screen, (150, 150, 150), rect)
