class Queue:
    #needed for the BFS
    def __init__(self):
        self.queue = []
        self.head = 0

    def add(self, item):
        self.queue.append(item)

    def remove(self):
        item = self.queue[self.head]
        self.head += 1
        return item

    def is_empty(self):
        return self.head >= len(self.queue)

class Board:
    def __init__(self):
        self.pawns = [(8, 4), (0, 4)] #storing the pawns as a list of tuples with row col (row number increases going down by convention)
        # Coordinates stored as row col tuple. Board size 9x9.
        self.walls = set() #collection of walls stored as a set (hash set) of tuples
        #Each wall will be stored as a tuple e.g ('H', (r, c))
        self.walls_remaining = [10, 10]
        self.current_player = 0
        self.game_over = False
        self.winner = None
    
    def switch_turn(self):
        #change the current turn between 0 and 1
        self.current_player = 1 - self.current_player

    def legal_pawn_moves(self):
        #return a list of all the legal pawn moves
        moves = []
        current_position = self.pawns[self.current_player]
        for square in self.neighbouring_squares(current_position):
            moves.append(square) #notation for a move is ("PAWN", (row, col)) or ("WALL", "H", (row, col))
        return moves

    def is_legal_wall(self, wall):
        if wall in self.walls:
            return False

        r, c, orientation = wall

        #walls cannot hang off edge of board
        if orientation == "H":
            if c < 0 or c > 7 or r < 1 or r > 8:
                return False  # prevents hanging off left/right
        else:  # "V"
            if r < 1 or r > 8 or c < 0 or c > 7:
                return False  # prevents hanging off top/bottom

        #horizontal and vertical walls cannont intersect to form a plus shape
        if orientation == "H":
            # check for vertical intersection (prevent "+" overlap)
            if (r, c, "V") in self.walls:
                return False
        else:  # vertical
            if (r, c, "H") in self.walls:  # blocks intersection
                return False

        #prevent overlaps of walls of same type
        if orientation == "H":
            if (r, c+1, "H") in self.walls or (r, c-1, "H") in self.walls:
                return False  # prevents overlapping / inside
        else:  # "V"
            if (r+1, c, "V") in self.walls or (r-1, c, "V") in self.walls:
                return False  # prevents overlapping / inside

        self.walls.add(wall) #add the wall so that we can then check if its ok
        legal = (self.path_exists(0) and self.path_exists(1)) #a path must exist for both player 0 and player 1
        self.walls.remove(wall) #undo the wall placement

        return legal

    def legal_wall_moves(self):
        #return a list of all the legal wall moves
        if self.walls_remaining[self.current_player] == 0:
            return []

        moves = []
        for row in range(8):
            for col in range(8):
                for orientation in ["H", "V"]:
                    if self.is_legal_wall((row, col, orientation)):
                        moves.append((row, col, orientation))
        return moves

    def apply_pawn_move(self, position):
        if position not in self.legal_pawn_moves():
            raise ValueError(f"Illegal pawn move: {position}")
        self.pawns[self.current_player] = position

    def apply_wall_move(self, wall):
        if not self.is_legal_wall(wall) or self.walls_remaining[self.current_player] == 0:
            raise ValueError(f"Illegal wall move: {wall}")

        self.walls.add(wall)
        self.walls_remaining[self.current_player] -= 1

    def apply_move(self, move):
        if self.game_over:
            return False

        if len(move) == 2:
            self.apply_pawn_move(move)
        elif len(move) == 3:
            self.apply_wall_move(move)
        else:
            raise ValueError(f"Invalid move type: {move}")

        if self.is_winner(self.current_player):
            self.game_over = True
            self.winner = self.current_player
        else:
            self.switch_turn()

        return True

    def is_valid_location(self, location):
        row, col = location
        return row >= 0 and row < 9 and col >= 0 and col < 9

    def neighbouring_squares(self, square):
        #give the 4 possible squares unless blocked by wall, and account for special pawn moves
        row, col = square
        neighbours = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row + dx
            new_col = col + dy
            adjacent = (new_row, new_col)
            
            #Check if adjacent square is valid and not blocked by wall
            if not self.is_valid_location(adjacent) or self.is_blocked(square, adjacent):
                continue
            
            #Check if theres a pawn on the adjacent square
            if adjacent not in self.pawns:
                #No pawn - normal move
                neighbours.append(adjacent)
            else:
                #Theres a pawn on the adjacent square
                jump_row = new_row + dx
                jump_col = new_col + dy
                jump_square = (jump_row, jump_col)
                
                #Try to jump over the opponent
                if self.is_valid_location(jump_square) and not self.is_blocked(adjacent, jump_square):
                    neighbours.append(jump_square)
                else:
                    #Cant jump - blocked by wall or edge so try diagonal moves
                    #Diagonal moves are perpendicular to the original direction
                    for perp_dx, perp_dy in [(dy, dx), (-dy, -dx)]:
                        diag_row = new_row + perp_dx
                        diag_col = new_col + perp_dy
                        diag_square = (diag_row, diag_col)
                        
                        #Check if diagonal square is valid and not blocked from opponents position
                        if (self.is_valid_location(diag_square) and 
                            not self.is_blocked(adjacent, diag_square)):
                            neighbours.append(diag_square)
            
        return neighbours

    def is_winner(self, player):
        row, col = self.pawns[player]
        if player == 0 and row == 0:
            return True
        elif player == 1 and row == 8:
            return True
        return False

    def is_blocked(self, a, b):
        #is the path from point a to b (adjacent squares) blocked? a,b are row col tuples
        r1, c1 = a
        r2, c2 = b

        if c1 == c2: #the movement is vertical
            lower_row = max(r1, r2)
            if (lower_row, c1, "H") in self.walls or (lower_row, c1-1, "H") in self.walls:
                return True #the path of this vertical movement is blocked

        if r1 == r2: #the movement is horizontal
            leftmost_col = min(c1, c2)
            if (r1, leftmost_col, "V") in self.walls or (r1+1, leftmost_col, "V") in self.walls:
                return True

        return False #the path is not blocked

    def path_exists(self, player):
        #determine if a path to the end exists for {player} using BFS
        start_node = self.pawns[player]
        queue = Queue()
        visited = set()
        queue.add(start_node)

        while not queue.is_empty():
            position = queue.remove()
            row, col = position
            if player == 0 and row == 0:
                return True
            if player == 1 and row == 8:
                return True

            for neighbour in self.neighbouring_squares(position):
                if neighbour not in visited:
                    queue.add(neighbour)
                    visited.add(neighbour)
        return None
    
    def export_state_for_bot(self):
        #export the board state in a format suitable for the bot


        state = (
            self.pawns,
            [(r, c, 0 if o == "H" else 1) for (r, c, o) in self.walls],
            self.walls_remaining,
            self.current_player
        )
        return state


