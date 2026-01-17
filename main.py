#Imports and initialisation
import pygame
from board import Board
from bot_cpp import bot_main
from graphics import Graphics

pygame.init()

#Screen and layout constants
CELL_SIZE = 60
SIDEBAR_WIDTH = CELL_SIZE * 5
WIDTH = CELL_SIZE * 9 + SIDEBAR_WIDTH
HEIGHT = CELL_SIZE * 9
GAP = 5

#Bot settings
BOT_DEPTH = 4  #bot search depth

#Pygame screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock() #used to cap FPS

#Game state variables
board = Board()
dragging_wall = None #tracks if a wall is being dragged for placement, type is a wall tuple
selected_pawn = None #tracks if a pawn is selected to move
legal_moves = [] #squares that the selected pawn can move to - needed for displaying legal moves
error_message = "" #will always display a message if there is one in this variable

#Graphics helper
graphics = Graphics(screen, font, CELL_SIZE, SIDEBAR_WIDTH, GAP)

#Player/Mode settings
mode = None  #0 for human v human, 1 for human v bot, 2 for bot v human, 3 for bot v bot
human_player = 0  #0 or 1 - just tracks which player is the human when doing human v bot or bot v human

#Starting screen
def start_screen():
    global mode, human_player

    selecting = True

    while selecting:
        screen.fill((240,240,240))
        title = font.render("Quoridor", True, (0,0,0))
        screen.blit(title, (WIDTH//2 - 60, 50))
        modes = ["Human vs Human", "Human vs Bot (Player 1)", "Bot vs Human (Player 2)", "Bot vs Bot"]

        for i in range(len(modes)):
            rect = pygame.Rect(WIDTH//2 - 150, 150 + i*100, 300, 60)
            pygame.draw.rect(screen, (180,180,180), rect)
            txt = font.render(modes[i], True, (0,0,0))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150 + i*100 + 15))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(len(modes)):
                    if pygame.Rect(WIDTH//2 - 120, 150 + i*100, 240, 60).collidepoint(mx, my):
                        mode = i
                        if mode == 2: #bot v human
                            human_player = 1
                        selecting = False

#Main game loop
start_screen()

running = True
winner = None  #Track winner to freeze input

while running:
    clock.tick(60)

    #Check winner
    if board.is_winner(0):
        winner = 0

        #Clear selections when game ends
        selected_pawn = None
        legal_moves = []
        dragging_wall = None

    elif board.is_winner(1):
        winner = 1

        #Clear selections when game ends
        selected_pawn = None
        legal_moves = []
        dragging_wall = None

    #Bot turn
    if not winner:
        if mode == 3:
            #Both players are bots
            move = bot_main(*board.export_state_for_bot(), BOT_DEPTH)
            board.apply_move(move)
            
            pygame.time.delay(500)  #add delay for bot

        elif (mode == 1 or mode == 2) and board.current_player != human_player: #if its a human-bot mode and its the bot's turn to move
            move = bot_main(*board.export_state_for_bot(), BOT_DEPTH)
            if move:
                board.apply_move(move)

            pygame.time.delay(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not winner and mode != 3:
            mx, my = event.pos

            col = mx // CELL_SIZE
            row = my // CELL_SIZE

            #Sidebar wall selectors
            if mx >= CELL_SIZE*9 and mx <= WIDTH:
                if my >= 80 and my <= (80 + CELL_SIZE//6):
                    dragging_wall = "H"

                elif my >= 150 and my <= (150 + 2*CELL_SIZE):
                    dragging_wall = "V"

            #Clicking on own pawn
            elif (row, col) == board.pawns[board.current_player]:
                selected_pawn = (row, col)
                legal_moves = board.neighbouring_squares(selected_pawn)

            #Clicking on legal move
            elif selected_pawn and (row, col) in legal_moves:
                move = (row, col)
                board.apply_move(move)
                selected_pawn = None
                legal_moves = []

        elif event.type == pygame.MOUSEBUTTONUP and not winner and mode != 3:

            if dragging_wall:
                mx, my = event.pos
                row = my // CELL_SIZE
                col = mx // CELL_SIZE
                move = (row, col, dragging_wall)
                try:
                    board.apply_move(move)
                    error_message = ""
                except ValueError:
                    error_message = "Illegal wall placement!"
                dragging_wall = None

    #Drawing
    screen.fill((240,240,240))
    graphics.draw_grid()
    graphics.draw_pawns(board)
    graphics.draw_walls(board)
    graphics.draw_sidebar(board, error_message)
    graphics.draw_legal_moves(legal_moves)

    #Draw ghost wall
    if dragging_wall and not winner and mode != "BOT_VS_BOT":
        graphics.draw_ghost_wall(dragging_wall)

    #Draw win message last so it appears on top
    if winner is not None:
        graphics.draw_win_message(winner, mode)

    pygame.display.flip()


pygame.quit()
