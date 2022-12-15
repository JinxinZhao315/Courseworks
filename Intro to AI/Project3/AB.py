import sys
from copy import deepcopy
import random
import math

PCE_AI_VALUE = {
    "King": 100,
    "Queen": 25,
    "Empress": 20,
    "Princess": 20,
    "Bishop": 15,
    "Rook": 15,
    "Knight": 10,
    "Ferz": 5,
    "Pawn": 1,
}

 # White pieces are represented on board by numbers in NAME_TO_REPR
 # black pieces are represented by the negative of numbers in NAME_TO_REPR
NAME_TO_REPR = {
    "King": 10,
    "Queen": 11,
    "Empress": 12,
    "Princess": 13,
    "Bishop": 14,
    "Rook": 15,
    "Knight": 16,
    "Ferz": 17,
    "Pawn": 18,
}

REPR_TO_NAME = {
    10: "King(W)", 
    11: "Queen(W)", 
    12: "Empress(W)",
    13: "Princess(W)", 
    14: "Bishop(W)", 
    15: "Rook(W)",
    16: "Knight(W)", 
    17: "Ferz(W)", 
    18: "Pawn(W)",
    -10: "King(B)", 
    -11: "Queen(B)", 
    -12: "Empress(B)",
    -13: "Princess(B)", 
    -14: "Bishop(B)", 
    -15: "Rook(B)",
    -16: "Knight(B)", 
    -17: "Ferz(B)", 
    -18: "Pawn(B)",
}

MAX_DEPTH = 2


### IMPORTANT: Remove any print() functions or rename any print functions/variables/string when submitting on CodePost
### The autograder will not run if it detects any print function.

# Helper functions to aid in your implementation. Can edit/remove
#############################################################################
######## Piece
#############################################################################
class Piece:
    def __init__(self, name, pos, is_white):
        self.name = name
        self.pos = pos # Pos is a tuple
        self.is_white = is_white
        if (is_white):
            self.board_repr_value = NAME_TO_REPR[name]
        else:
            self.board_repr_value = - NAME_TO_REPR[name] 
    
    def __str__(self):
        if self.is_white:
            color_str = "White"
        else:
            color_str = "Black"
        return '{},{},{}'.format(self.name, color_str, self.pos)

    def __repr__(self):
        if self.is_white:
            color_str = "White"
        else:
            color_str = "Black"
        return '{},{},{}'.format(self.name, color_str, self.pos)

    def is_move_in_bound(self, new_r, new_c, rows, cols):
        return 0 <= new_r < rows and 0 <= new_c < cols

    def can_consume_opponent(self, dest_board_val):
        return self.board_repr_value * dest_board_val < 0

    def is_dest_empty(self, dest_board_val):
        return dest_board_val == 0

    # Test if a piece can move to a new location, and if so, if the piece can move further in that direction.
    # Returns True if piece can go further after moving to new dest, and append new possible locations to new_pos
    def test_and_append(self, new_pos, r_step, c_step, board_obj):
        board_arr = board_obj.board_arr
        rows = board_obj.rows
        cols = board_obj.cols
        pos = self.pos
        new_r = pos[0] + r_step
        new_c = pos[1] + c_step
        if self.is_move_in_bound(new_r, new_c, rows, cols):
            dest_cell_value = board_arr[new_r][new_c]
            if self.is_dest_empty(dest_cell_value):
                new_pos.append( (new_r, new_c) )
                return True
            else: # If dest cell is not empty
                if self.can_consume_opponent(dest_cell_value):
                    new_pos.append( (new_r, new_c) )
                    return False # Consuming an opponent stops piece from going further
                else:
                    return False
        else:
            return False

    def pawn_test_and_append(self, new_pos, board_obj):
        pos = self.pos
        board_arr = board_obj.board_arr
        rows = board_obj.rows
        cols = board_obj.cols
        if self.is_white:
            dest_down = (pos[0] + 1, pos[1])
            dest_down_left = (pos[0] + 1, pos[1] - 1)
            dest_down_right = (pos[0] + 1, pos[1] + 1)
            
            if self.is_move_in_bound(dest_down[0], dest_down[1], rows, cols):
                dest_cell_value = board_arr[dest_down[0]][dest_down[1]]
                if self.is_dest_empty(dest_cell_value):
                    new_pos.append(dest_down)

            for dest in (dest_down_left, dest_down_right):
                if self.is_move_in_bound(dest[0], dest[1], rows, cols):
                    dest_cell_value = board_arr[dest[0]][dest[1]]
                    if self.can_consume_opponent(dest_cell_value):
                        new_pos.append(dest)
        else:
            dest_up = (pos[0] - 1, pos[1])
            dest_up_left = (pos[0] - 1, pos[1] - 1)
            dest_up_right = (pos[0] - 1, pos[1] + 1)
            
            if self.is_move_in_bound(dest_up[0], dest_up[1], rows, cols):
                dest_cell_value = board_arr[dest_up[0]][dest_up[1]]
                if self.is_dest_empty(dest_cell_value):
                    new_pos.append(dest_up)

            for dest in (dest_up_left, dest_up_right):
                if self.is_move_in_bound(dest[0], dest[1], rows, cols):
                    dest_cell_value = board_arr[dest[0]][dest[1]]
                    if self.can_consume_opponent(dest_cell_value):
                        new_pos.append(dest)

    def loop_test_and_append(self, new_pos, r_dir, c_dir, board_obj):
            for factor in range(1, max(board_obj.rows, board_obj.cols)):
                if self.test_and_append(new_pos, r_dir * factor, c_dir * factor, board_obj):
                    continue
                else:
                    break     
    
    def get_actions(self, board_obj):
        new_pos = []

        if self.name == "King":
            for r in [-1, 0, 1]:
                for c in [-1, 0, 1]:
                    if r == 0 and c == 0:
                        continue
                    self.test_and_append(new_pos, r, c, board_obj)
        elif self.name == "Rook":
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_append(new_pos, r_dir, c_dir, board_obj)
        elif self.name == "Bishop":
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_append(new_pos, r_dir, c_dir, board_obj)
        elif self.name == "Queen":
            for r_dir in [-1, 0, 1]:
                for c_dir in [-1, 0, 1]:
                    if r_dir == 0 and c_dir == 0:
                        continue
                    self.loop_test_and_append(new_pos, r_dir, c_dir, board_obj)
        elif self.name == "Knight":
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], board_obj)
        elif self.name == "Ferz":
            for r in [-1, 1]:
                for c in [-1, 1]:
                    self.test_and_append(new_pos, r, c, board_obj)
        elif self.name == "Princess": # Kight + Bishop
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], board_obj)
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_append(new_pos, r_dir, c_dir, board_obj)            
        elif self.name == "Empress": # Kight + Rook
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], board_obj)
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_append(new_pos, r_dir, c_dir, board_obj)
        elif self.name == "Pawn":
            self.pawn_test_and_append(new_pos, board_obj)
        return new_pos
#############################################################################
######## Board
#############################################################################
class Board:
    def __init__(self, rows, cols, white_pieces, black_pieces):
        self.rows = rows
        self.cols = cols
        self.board_arr = [[0 for i in range(rows)] for j in range(cols)]
        self.is_white_turn = True
        self.white_pieces = {} # (pos: piece_obj)
        self.black_pieces = {}
        self.is_white_king_alive = True
        self.is_black_king_alive = True
        self.moves_without_consume = 0

        for white_pce in white_pieces:
            pos = white_pce.pos
            self.white_pieces[pos] = white_pce
            self.board_arr[pos[0]][pos[1]] = white_pce.board_repr_value

        for black_pce in black_pieces:
            pos = black_pce.pos
            self.black_pieces[pos] = black_pce
            self.board_arr[pos[0]][pos[1]] = black_pce.board_repr_value

    def move_piece(self, old_pos, new_pos):
        new_board_obj = deepcopy(self)
        moving_piece_obj = None
        if self.is_white_turn:
            moving_piece_obj = new_board_obj.white_pieces[old_pos]
            new_board_obj.white_pieces[new_pos] =  moving_piece_obj
            del new_board_obj.white_pieces[old_pos]
        else:
            moving_piece_obj = new_board_obj.black_pieces[old_pos]
            new_board_obj.black_pieces[new_pos] =  moving_piece_obj
            del new_board_obj.black_pieces[old_pos]

        old_pos_board_val = new_board_obj.board_arr[old_pos[0]][old_pos[1]]
        new_pos_board_val = new_board_obj.board_arr[new_pos[0]][new_pos[1]]
        is_consuming_opponent = old_pos_board_val * new_pos_board_val < 0
        if not is_consuming_opponent:
            new_board_obj.moves_without_consume += 1
        else:
            new_board_obj.moves_without_consume = 0

        # Update board array and piece position
        new_board_obj.board_arr[old_pos[0]][old_pos[1]] = 0
        new_board_obj.board_arr[new_pos[0]][new_pos[1]] = moving_piece_obj.board_repr_value
        moving_piece_obj.pos = new_pos

        if self.is_white_turn and is_consuming_opponent:
            removed_piece_obj = new_board_obj.black_pieces[new_pos]
            del new_board_obj.black_pieces[new_pos]
            if removed_piece_obj.name == "King":
                new_board_obj.is_black_king_alive = False
        elif not self.is_white_turn and is_consuming_opponent:
            removed_piece_obj = new_board_obj.white_pieces[new_pos]
            del new_board_obj.white_pieces[new_pos]
            if removed_piece_obj.name == "King":
                new_board_obj.is_white_king_alive = False

        new_board_obj.is_white_turn = not self.is_white_turn
        
        return new_board_obj

    def get_all_moves(self):
        all_moves = []
        if self.is_white_turn:
            for white_pce in self.white_pieces.values():
                pce_moves = white_pce.get_actions(self)
                for dest in pce_moves:
                    all_moves.append((white_pce.pos, dest))
        else:
            for black_pce in self.black_pieces.values():
                pce_moves = black_pce.get_actions(self)
                for dest in pce_moves:
                    all_moves.append((black_pce.pos, dest))
        return all_moves

    def is_game_over(self, all_moves):
        if not self.is_white_king_alive or not self.is_black_king_alive:
            return True
        if self.moves_without_consume >= 50:
            return True
        if len(all_moves) == 0:
            return True
        return False

    def value_board(self):
        max_val = 0
        min_val = 0
        for pce in self.white_pieces.values():
            max_val += PCE_AI_VALUE[pce.name]
        for pce in self.black_pieces.values():
            min_val += PCE_AI_VALUE[pce.name]
        return max_val - min_val

#############################################################################
######## Helper functions
#############################################################################

def chess_coord_to_num(ch_coord):
    return (int(ch_coord[1]), ord(ch_coord[0]) - 97)

def num_to_chess_coord(num_coord):
    return (chr(num_coord[1] + 97), num_coord[0])

# TODO: Comment out this function
# def print_board(board_obj):
#     board = board_obj.board_arr
#     rows = board_obj.rows
#     cols = board_obj.cols
#     for r in [-1, 0, 1, 2, 3, 4, 5, 6]:
#         print("{:<20d}".format(r), end="")
#     print()
#     c = 0
#     for i in range(0, rows):
#         for j in range(0, cols):
#             if j == 0:
#                 print("{:<20d}".format(c), end="")
#                 c += 1
#             if board[i][j] == 0:
#                 print("{:<20d}".format(0), end="")
#             else:
#                 piece_name = REPR_TO_NAME[board[i][j]]
#                 print("{:<20s}".format(str(piece_name)), end="")
#         print()

#Implement your minimax with alpha-beta pruning algorithm here.
def ab(board_obj):
    if board_obj.is_white_turn:
        value, move = maximize(MAX_DEPTH, board_obj, - math.inf, math.inf)
    else:
        value, move = minimize(MAX_DEPTH, board_obj, - math.inf, math.inf)
    return value, move


def maximize(depth, board_obj, alpha, beta):
    all_moves = board_obj.get_all_moves()
    if board_obj.is_game_over(all_moves) or depth == 0:
        return board_obj.value_board(), None
    max_value = - math.inf
    move_to_take = None
    random.shuffle(all_moves)
    for move in all_moves:
        opp_value, opp_move = minimize(depth - 1, board_obj.move_piece(move[0], move[1]), alpha, beta)
        if opp_value > max_value:
            max_value, move_to_take = opp_value, (move[0], move[1])
            alpha = max(alpha, max_value)
        if max_value >= beta:
            return max_value, move_to_take
    return max_value, move_to_take

def minimize(depth, board_obj, alpha, beta):
    all_moves = board_obj.get_all_moves()
    if board_obj.is_game_over(all_moves) or depth == 0:
        return board_obj.value_board(), None
    min_value = math.inf
    move_to_take = None
    random.shuffle(all_moves)
    for move in all_moves:
        opp_value, opp_move = maximize(depth - 1, board_obj.move_piece(move[0], move[1]), alpha, beta)
        if opp_value < min_value:
            min_value, move_to_take = opp_value, (move[0], move[1])
            beta = min(beta, min_value)
        if min_value <= alpha:
            return min_value, move_to_take
    return min_value, move_to_take

#############################################################################
######## Parser function and helper functions
#############################################################################
### DO NOT EDIT/REMOVE THE FUNCTION BELOW###
# Return number of rows, cols, grid containing obstacles and step costs of coordinates, enemy pieces, own piece, and goal positions
def parse(testcase):
    handle = open(testcase, "r")

    get_par = lambda x: x.split(":")[1]
    rows = int(get_par(handle.readline())) # Integer
    cols = int(get_par(handle.readline())) # Integer
    gameboard = {}
    
    enemy_piece_nums = get_par(handle.readline()).split()
    num_enemy_pieces = 0 # Read Enemy Pieces Positions
    for num in enemy_piece_nums:
        num_enemy_pieces += int(num)

    handle.readline()  # Ignore header
    for i in range(num_enemy_pieces):
        line = handle.readline()[1:-2]
        coords, piece = add_piece(line)
        gameboard[coords] = (piece, "Black")    

    own_piece_nums = get_par(handle.readline()).split()
    num_own_pieces = 0 # Read Own Pieces Positions
    for num in own_piece_nums:
        num_own_pieces += int(num)

    handle.readline()  # Ignore header
    for i in range(num_own_pieces):
        line = handle.readline()[1:-2]
        coords, piece = add_piece(line)
        gameboard[coords] = (piece, "White")    

    return rows, cols, gameboard

def add_piece( comma_seperated) -> Piece:
    piece, ch_coord = comma_seperated.split(",")
    r, c = from_chess_coord(ch_coord)
    return [(r,c), piece]

def from_chess_coord( ch_coord):
    return (int(ch_coord[1:]), ord(ch_coord[0]) - 97)

# You may call this function if you need to set up the board
def setUpBoard():
    config = sys.argv[1]
    rows, cols, gameboard = parse(config)

# gameboard = {('a', 1): ('Ferz', 'White'), ('a', 5): ('Ferz', 'Black'), ('g', 1): ('Ferz', 'White'), \
# ('g', 5): ('Ferz', 'Black'), ('b', 1): ('Pawn', 'White'), ('b', 5): ('Pawn', 'Black'), ('c', 1): ('Pawn', 'White'), \
# ('c', 5): ('Pawn', 'Black'), ('d', 1): ('Pawn', 'White'), ('d', 5): ('Pawn', 'Black'), ('e', 1): ('Pawn', 'White'), \
# ('e', 5): ('Pawn', 'Black'), ('f', 1): ('Pawn', 'White'), ('f', 5): ('Pawn', 'Black'), ('a', 0): ('Knight', 'White'), \
# ('a', 6): ('Knight', 'Black'), ('b',0): ('Bishop', 'White'), ('b', 6): ('Bishop', 'Black'), ('c', 0): ('Queen', 'White'), \
# ('c', 6): ('Queen', 'Black'), ('d', 0): ('King', 'White'), ('d', 6): ('King', 'Black'), ('e', 0): ('Princess', 'White'), \
# ('e', 6): ('Princess', 'Black'), ('f', 0): ('Empress', 'White'), ('f', 6):  ('Empress', 'Black'), \
# ('g', 0):  ('Rook', 'White'), ('g',6):  ('Rook', 'Black')}

### DO NOT EDIT/REMOVE THE FUNCTION HEADER BELOW###
# Chess Pieces: King, Queen, Knight, Bishop, Rook, Princess, Empress, Ferz, Pawn (First letter capitalized)
# Colours: White, Black (First Letter capitalized)
# Positions: Tuple. (column (String format), row (Int)). Example: ('a', 0)

# Parameters:
# gameboard: Dictionary of positions (Key) to the tuple of piece type and its colour (Value). This represents the current pieces left on the board.
# Key: position is a tuple with the x-axis in String format and the y-axis in integer format.
# Value: tuple of piece type and piece colour with both values being in String format. Note that the first letter for both type and colour are capitalized as well.
# gameboard example: {('a', 0) : ('Queen', 'White'), ('d', 10) : ('Knight', 'Black'), ('g', 25) : ('Rook', 'White')}
#
# Return value:
# move: A tuple containing the starting position of the piece being moved to the new ending position for the piece. x-axis in String format and y-axis in integer format.
# move example: (('a', 0), ('b', 3))


def studentAgent(gameboard):
    # You can code in here but you cannot remove this function, change its parameter or change the return type
    white_pieces = []
    black_pieces = []

    for pos in gameboard:
        pce_and_color = gameboard[pos]
        if pce_and_color[1] == "White":
            curr_pce = Piece(pce_and_color[0], chess_coord_to_num(pos), True)
            white_pieces.append(curr_pce)
        else:
            curr_pce = Piece(pce_and_color[0], chess_coord_to_num(pos), False)
            black_pieces.append(curr_pce)

    board_obj = Board(7, 7, white_pieces, black_pieces)
    value, move = ab(board_obj)
    formatted_move = (num_to_chess_coord(move[0]), num_to_chess_coord(move[1]))
    return formatted_move #Format to be returned (('a', 0), ('b', 3))

