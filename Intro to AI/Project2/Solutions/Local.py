import sys
import random

number_to_pce_name_dict = {-10: "King", -11: "Queen", -12: "Bishop", -13: "Rook", \
    -14: "Knight", -15: "Ferz", -16: "Princess", -17: "Empress"}

pce_name_to_number_dict = {"King": -10, "Queen": -11, "Bishop": -12, "Rook": -13, \
    "Knight": -14, "Ferz": -15, "Princess": -16, "Empress": -17}

# Helper functions to aid in your implementation. Can edit/remove
#############################################################################
######## Piece
#############################################################################
class Piece:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos # Pos is a tuple
        self.threat_no = 0 # Number of other pieces that self threatens.
    
    def __str__(self):
        return '{},{}'.format(self.name, self.threat_no)

    def __repr__(self):
        return '{},{}'.format(self.name, self.pos)

    def __eq__(self, other):
        return self.name == other.name and self.pos == other.pos
    
    def test_and_count(self, r_step, c_step, board_arr, rows, cols):
        pos = self.pos
        if pos[0] + r_step >= 0 and pos[0] + r_step < rows and \
            pos[1] + c_step >= 0 and pos[1] + c_step < cols:
            dest_cost = board_arr[pos[0] + r_step][pos[1] + c_step]
            if dest_cost <= -10:
                self.threat_no += 1
                return False
            elif dest_cost == -1:
                return False
            elif dest_cost >= 0:
                return True
        else:
            # Piece move out of board
            return False

    def loop_test_and_count(self, r_dir, c_dir, board_arr, rows, cols):
            for factor in range(1, max(rows, cols)):
                if self.test_and_count(r_dir * factor, c_dir * factor, board_arr, rows, cols):
                    continue
                else:
                    break       
    
    def count_threat(self, board_arr, rows, cols):
        self.threat_no = 0
        if self.name == "King":
            for r in [-1, 0, 1]:
                for c in [-1, 0, 1]:
                    if r == 0 and c == 0:
                        continue
                    self.test_and_count(r, c, board_arr, rows, cols)
        elif self.name == "Rook":
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_count(r_dir, c_dir, board_arr, rows, cols)
        elif self.name == "Bishop":
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_count(r_dir, c_dir, board_arr, rows, cols)
        elif self.name == "Queen":
            for r_dir in [-1, 0, 1]:
                for c_dir in [-1, 0, 1]:
                    if r_dir == 0 and c_dir == 0:
                        continue
                    self.loop_test_and_count(r_dir, c_dir, board_arr, rows, cols)
        elif self.name == "Knight":
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_count(move[0], move[1], board_arr, rows, cols)
        elif self.name == "Ferz":
            for r in [-1, 1]:
                for c in [-1, 1]:
                    self.test_and_count(r, c, board_arr, rows, cols)
        elif self.name == "Princess": # Kight + Bishop
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_count(move[0], move[1], board_arr, rows, cols)
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_count(r_dir, c_dir, board_arr, rows, cols)            
        elif self.name == "Empress": # Kight + Rook
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_count(move[0], move[1], board_arr, rows, cols)
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_count(r_dir, c_dir, board_arr, rows, cols)
        return self.threat_no

#############################################################################
######## Board
#############################################################################
class Board:
    def __init__(self, grid, pieces_obj_arr, rows, cols):
        self.board_arr = list(grid)
        self.rows = rows
        self.cols = cols
        self.pieces_arr = pieces_obj_arr
        for piece_obj in pieces_obj_arr:
            pos = piece_obj.pos
            piece_num = pce_name_to_number_dict[piece_obj.name]
            self.board_arr[pos[0]][pos[1]] = piece_num

    def add_piece(self, piece_obj):
        pos = piece_obj.pos
        piece_num = pce_name_to_number_dict[piece_obj.name]
        self.board_arr[pos[0]][pos[1]] = piece_num
        self.pieces_arr.append(piece_obj)

    def remove_piece(self, piece_obj):
        pos = piece_obj.pos
        self.board_arr[pos[0]][pos[1]] = 0
        self.pieces_arr.remove(piece_obj)
    
    def value(self):
        threat_pairs = 0
        for piece_obj in self.pieces_arr:
            threat_pairs += piece_obj.count_threat(self.board_arr, self.rows, self.cols)
        return threat_pairs
    
    def is_goal(self):
        for piece_obj in self.pieces_arr:
            threat_num = piece_obj.count_threat(self.board_arr, self.rows, self.cols)
            if threat_num > 0:
                return False
        return True



#############################################################################
######## Helper functions
#############################################################################

# TODO: Comment out this function
# def print_board(board_arr, rows, cols):
#     for i in range(rows):
#         for j in range(cols):
#             if board_arr[i][j] >= -1:
#                 print("{:<20s}".format(str(board_arr[i][j])), end="")
#             elif board_arr[i][j] <= -10:
#                 piece_name = number_to_pce_name_dict[board_arr[i][j]]
#                 piece = Piece(piece_name, (i, j))
#                 piece.count_threat(board_arr, rows, cols)
#                 print("{:<20s}".format(str(piece)), end="")
#         print()

def format_solution(piece_obj_arr):
    formatted_dict = {}
    for piece_obj in piece_obj_arr:
        pos = piece_obj.pos
        formatted_pos = ((chr(pos[1] + 97), pos[0]))
        formatted_dict[formatted_pos] = piece_obj.name
    return formatted_dict



#############################################################################
######## Implement Search Algorithm
#############################################################################
def search(rows, cols, grid, pieces, k):
    full_pieces_obj_arr = []
    for pos in pieces:
        pce_name = pieces[pos]
        full_pieces_obj_arr.append(Piece(pce_name, pos))
    rand_k_pieces = random.sample(full_pieces_obj_arr, int(k))
    board_state = Board(grid, rand_k_pieces, rows, cols)
    is_goal_bool = board_state.is_goal()

    while not is_goal_bool:
        pieces_removed = []
        for piece_obj in full_pieces_obj_arr:
            if piece_obj not in board_state.pieces_arr:
                pieces_removed.append(piece_obj)
        curr_val = board_state.value()
        piece_to_remove = None
        piece_to_add = None
        for piece_to_rmv_test in board_state.pieces_arr:
            board_state.remove_piece(piece_to_rmv_test)
            for piece_to_add_test in pieces_removed:
                board_state.add_piece(piece_to_add_test)
                neighbour_val = board_state.value()
                if neighbour_val <= curr_val:
                    piece_to_remove = piece_to_rmv_test
                    piece_to_add = piece_to_add_test
                    curr_val = neighbour_val
                    if curr_val == 0:
                        is_goal_bool = True
                        break
                board_state.remove_piece(piece_to_add_test)
            board_state.add_piece(piece_to_rmv_test)
            if is_goal_bool:
                break
        if not piece_to_remove is None:
            board_state.remove_piece(piece_to_remove)
            board_state.add_piece(piece_to_add)

    # return format_solution(board_state.pieces_arr), board_state.board_arr
    return format_solution(board_state.pieces_arr)
    
    


#############################################################################
######## Parser function and helper functions
#############################################################################
### DO NOT EDIT/REMOVE THE FUNCTION BELOW###
def parse(testcase):
    handle = open(testcase, "r")

    get_par = lambda x: x.split(":")[1]
    rows = int(get_par(handle.readline()))
    cols = int(get_par(handle.readline()))
    grid = [[0 for j in range(cols)] for i in range(rows)]
    k = 0
    pieces = {}

    num_obstacles = int(get_par(handle.readline()))
    if num_obstacles > 0:
        for ch_coord in get_par(handle.readline()).split():  # Init obstacles
            r, c = from_chess_coord(ch_coord)
            grid[r][c] = -1
    else:
        handle.readline()
    
    k = handle.readline().split(":")[1].strip() # Read in value of k

    piece_nums = get_par(handle.readline()).split()
    num_pieces = 0
    for num in piece_nums:
        num_pieces += int(num)

    handle.readline()  # Ignore header
    for i in range(num_pieces):
        line = handle.readline()[1:-2]
        coords, piece = add_piece(line)
        pieces[coords] = piece    

    return rows, cols, grid, pieces, k

def add_piece( comma_seperated):
    piece, ch_coord = comma_seperated.split(",")
    r, c = from_chess_coord(ch_coord)
    return [(r,c), piece]

#Returns row and col index in integers respectively
def from_chess_coord( ch_coord):
    return (int(ch_coord[1:]), ord(ch_coord[0]) - 97)

### DO NOT EDIT/REMOVE THE FUNCTION HEADER BELOW###
# To return: Goal State which is a dictionary containing a mapping of the position of the grid to the chess piece type.
# Chess Pieces (String): King, Queen, Knight, Bishop, Rook (First letter capitalized)
# Positions: Tuple. (column (String format), row (Int)). Example: ('a', 0)

# Goal State to return example: {('a', 0) : Queen, ('d', 10) : Knight, ('g', 25) : Rook}

# TODO: Remove next 2 lines
# testcase = "Test/Local4.txt"
# rows, cols, grid, pieces, k = parse(testcase)

def run_local():
    testcase = sys.argv[1] #Do not remove. This is your input testfile.
    rows, cols, grid, pieces, k = parse(testcase)
    goalstate = search(rows, cols, grid, pieces, k)
    return goalstate #Format to be returned
