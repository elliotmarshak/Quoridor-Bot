#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <algorithm>
#include <unordered_set>

namespace py = pybind11;

struct Move {
    int row;
    int col;
    char type; //0 for H, 1 for V or 2 for P
};

struct Square {
    int row;
    int col;

    bool operator==(const Square& other) const {
        return (row == other.row && col == other.col);
    }
};

struct SquareHash {
    std::size_t operator()(const Square& s) const {
        return s.row * 9 + s.col;
    }
};

struct Wall {
    int row;
    int col;
    int type; // 0 for horizontal, 1 for vertical

    bool operator==(const Wall& other) const {
        return (row == other.row && col == other.col && type == other.type);
    }
};

struct WallHash {
    std::size_t operator()(const Wall& w) const {
        return (w.row * 9 + w.col) * 2 + w.type;
    }
};

class Board {
    public:
        Square pawns[2]; //[player][row/col]
        std::unordered_set<Wall, WallHash> walls;
        int walls_remaining[2];
        int current_player;
        bool game_over = false;

        Board() {
            //P1
            pawns[0].row = 8;
            pawns[0].col = 4;

            //P2
            pawns[1].row = 0;
            pawns[1].col = 4;

            walls_remaining[0] = walls_remaining[1] = 10;
            current_player = 0;
        }

        bool wall_exists(Wall wall) {
            return (walls.find(wall) != walls.end());
        }

        bool is_valid_location(Square location) const {
            int row = location.row;
            int col = location.col;
            return (row >= 0 && row < 9 && col >= 0 && col < 9);
        }

        bool is_blocked(Square location_a, Square location_b) {
            int row1 = location_a.row; int col1 = location_a.col;
            int row2 = location_b.row; int col2 = location_b.col;

            if (col1 == col2) { //the movement is vertical
                int lower_row = std::max(row1, row2);
                if (wall_exists({lower_row, col1, 0}) || wall_exists({lower_row, col1-1, 0})) {return true;}
            }

            if (row1 == row2) { //the movement is horizontal
                int leftmost_col = std::min(col1, col2);
                if (wall_exists({row1, leftmost_col, 1}) || wall_exists({row1+1, leftmost_col, 1})) {return true;}
            }

            return false;
        }

        std::vector<Square> neighbouring_squares(Square square) {
            int row = square.row;
            int col = square.col;

            std::vector<Square> neighbours;
            
            const int dirs[4][2] = {
                {-1, 0},
                {1, 0},
                {0, -1},
                {0 , 1}
            };

            for (const auto& d : dirs) {
                int dx = d[0];
                int dy = d[1];
                int new_row = row + dx;
                int new_col = col + dy;
                Square adjacent = {new_row, new_col};
                
                //Check if adjacent square is valid and not blocked by wall
                if (!is_valid_location(adjacent) || is_blocked(square, adjacent)) {
                    continue;
                }
                
                //Check if theres a pawn on the adjacent square
                bool pawn_on_adjacent = (pawns[0] == adjacent || pawns[1] == adjacent);
                
                if (!pawn_on_adjacent) {
                    //No pawn - normal move
                    neighbours.push_back(adjacent);
                } else {
                    //Theress a pawn on the adjacent square
                    int jump_row = new_row + dx;
                    int jump_col = new_col + dy;
                    Square jump_square = {jump_row, jump_col};
                    
                    //Try to jump over the opponent
                    if (is_valid_location(jump_square) && !is_blocked(adjacent, jump_square)) {
                        neighbours.push_back(jump_square);
                    } else {
                        //Cant jump - blocked by wall or edge so try diagonal moves
                        //Diagonal moves are perpendicular to the original direction
                        
                        int perp_dirs[2][2] = {
                            {dy, dx},    //perpendicular direction 1
                            {-dy, -dx}   //perpendicular direction 2
                        };
                        
                        for (const auto& perp : perp_dirs) {
                            int perp_dx = perp[0];
                            int perp_dy = perp[1];
                            int diag_row = new_row + perp_dx;
                            int diag_col = new_col + perp_dy;
                            Square diag_square = {diag_row, diag_col};
                            
                            //Check if diagonal square is valid and not blocked from opponents position
                            if (is_valid_location(diag_square) && !is_blocked(adjacent, diag_square)) {
                                neighbours.push_back(diag_square);
                            }
                        }
                    }
                }
            }
            
            return neighbours;
        }

        bool is_legal_wall(Wall wall) {
            if (wall_exists(wall)) {return false;}

            int r = wall.row; int c = wall.col; int type = wall.type;

            //Walls cannot hang off the edge of the board
            if (type == 0) { //Horizontal
                if (c < 0 || c > 7 || r < 1 || r > 8) {return false;}
            }
            else {
                if (r < 1 || r > 8 || c < 0 || c > 7) {return false;}
            }

            //Horizontal and vertical walls cannot intersect such that they form a plus shape
            if (type == 0) {
                if (wall_exists({r, c, 1})) {return false;}
            }
            else {
                if (wall_exists({r, c, 0})) {return false;}
            }

            //prevent overlaps of walls of same type
            if (type == 0) {
                if (wall_exists({r, c+1, 0}) || wall_exists({r, c-1, 0})) {return false;}
            }
            else {
                if (wall_exists({r+1, c, 1}) || wall_exists({r-1, c, 1})) {return false;}
            }

            walls.insert(wall);
            bool legal = (shortest_path(0) != -1 && shortest_path(1) != -1);
            walls.erase(wall);

            return legal;
        }

        std::vector<Move> legal_pawn_moves() {
            std::vector<Move> moves;
            for (Square square : neighbouring_squares(pawns[current_player])) {
                moves.push_back({square.row, square.col, 2});
            }
            return moves;
        }

        std::vector<Move> legal_wall_moves() {
            std::vector<Move> moves;
            if (walls_remaining[current_player] == 0) {return moves;}

            for (int row = 0; row < 8; row++) {
                for (int col = 0; col < 8; col++) {
                    for (int type = 0; type < 2; type++) {
                        Wall wall = {row, col, type};
                        if (is_legal_wall(wall)) {
                            Move move = {row, col, type};
                            moves.push_back(move);
                        }
                    }
                }
            }
            return moves;
        }

        std::vector<Move> legal_moves() {
            std::vector<Move> legal_moves = legal_pawn_moves();
            std::vector<Move> wall_moves = legal_wall_moves();
            legal_moves.insert(legal_moves.end(), wall_moves.begin(), wall_moves.end());

            return legal_moves;
        }

        void apply_move(Move move) {
            if (move.type == 2) { //pawn
                pawns[current_player] = {move.row, move.col};    
            }
            else { //wall
                walls.insert({move.row, move.col, move.type});
                walls_remaining[current_player] -= 1;
            }

            current_player = 1 - current_player;
        }

        Board copy() const {
            Board new_board;
            new_board.pawns[0].row = pawns[0].row;
            new_board.pawns[0].col = pawns[0].col;
            new_board.pawns[1].row = pawns[1].row;
            new_board.pawns[1].col = pawns[1].col;

            new_board.walls = walls;
            new_board.walls_remaining[0] = walls_remaining[0];
            new_board.walls_remaining[1] = walls_remaining[1];
            new_board.current_player = current_player;

            return new_board;
        }

        bool is_winner(int player) const {
            if (player == 0) {
                return (pawns[0].row == 0);
            }
            else { //player = 1
                return (pawns[1].row == 8);
            }
        }

        int shortest_path(int player) { //get the shortest path distance for that player. -1 if no path.
            Square start_position = pawns[player];
            std::queue<std::pair<Square, int>> queue;
            std::unordered_set<Square, SquareHash> visited;

            std::pair<Square, int> start_node = {start_position, 0};
            visited.insert(start_position);
            queue.push(start_node);

            while (!queue.empty()) {
                std::pair<Square, int> node = queue.front();
                queue.pop();

                if (player == 0 && node.first.row == 0) {return node.second;}
                if (player == 1 && node.first.row == 8) {return node.second;}

                for (Square neighbour : neighbouring_squares(node.first)) {
                    if (visited.find(neighbour) == visited.end()) {
                        visited.insert(neighbour);
                        queue.push({neighbour, node.second + 1});
                    }
                }
            }

            return -1;

        }
};

double evaluate(Board board) {
    int distance0 = board.shortest_path(0);
    int distance1 = board.shortest_path(1);

    int walls0 = board.walls_remaining[0];
    int walls1 = board.walls_remaining[1];

    double score = (distance1 - distance0) + (walls0 - walls1)*0.2;

    return score;
}

std::pair<Move, double> minimax(Board board, int depth, double alpha, double beta, bool maximisingPlayer) {
    if (board.is_winner(0)) {return {{0,0,0}, 100};}
    if (board.is_winner(1)) {return {{0,0,0}, -100};}
    if (depth == 0) {return {{0,0,0}, evaluate(board)};}

    double value;
    Move best_move;

    std::vector<Move> legal_moves = board.legal_moves();

    if (maximisingPlayer) {
        value = -999.0;

        for (Move move : legal_moves) {
            Board new_board = board.copy();
            new_board.apply_move(move);
            std::pair<Move, double> result = minimax(new_board, depth-1, alpha, beta, false);
            
            if (result.second > value) {
                value = result.second;
                best_move = move;
            }
            alpha = std::max(alpha, value);
            if (alpha >= beta) {
                break;
            }
        }
        return {best_move, value};
    }

    else { //minimising player
        value = 999.0;

        for (Move move : legal_moves) {
            Board new_board = board.copy();
            new_board.apply_move(move);
            std::pair<Move, double> result = minimax(new_board, depth-1, alpha, beta, true);
            
            if (result.second < value) {
                value = result.second;
                best_move = move;
            }
            beta = std::min(beta, value);
            if (alpha >= beta) {
                break;
            }
        }
        return {best_move, value};
    }
}

// Main bot function
py::object bot_main(std::vector<std::pair<int, int>> pawns, std::vector<std::tuple<int, int, int>> walls, std::vector<int> walls_remaining, int current_player, int max_depth) {
    Board board;
    board.pawns[0] = {pawns[0].first, pawns[0].second};
    board.pawns[1] = {pawns[1].first, pawns[1].second};
    for (std::tuple<int, int, int> wall : walls) {
        board.walls.insert({std::get<0>(wall), std::get<1>(wall), std::get<2>(wall)});
    }
    board.walls_remaining[0] = walls_remaining[0];
    board.walls_remaining[1] = walls_remaining[1];
    board.current_player = current_player;

    bool maximising = (current_player == 0);

    std::pair<Move, double> result = minimax(board, max_depth, -999, 999, maximising);
    Move best_move = result.first;

    std::string move_type;
    if (best_move.type == 0) {
        return py::make_tuple(best_move.row, best_move.col, "H");
    }
    else if (best_move.type == 1) {
        return py::make_tuple(best_move.row, best_move.col, "V");
    }
    else {
        return py::make_tuple(best_move.row, best_move.col);
    }
}

PYBIND11_MODULE(bot_cpp, m) {
    m.def("bot_main", &bot_main);
}