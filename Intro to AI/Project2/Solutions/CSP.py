import random
import sys

number_to_piece_dict = {-10: "King", -11: "Queen", -12: "Bishop", -13: "Rook", \
    -14: "Knight", -15: "Ferz", -16: "Princess", -17: "Empress"}

piece_to_number_dict = {"King": -10, "Queen": -11, "Bishop": -12, "Rook": -13, \
    "Knight": -14, "Ferz": -15, "Princess": -16, "Empress": -17}

# index_to_piece_dict = {0: "King", 1: "Queen", 2:"Bishop", 3:"Rook", 4: "Knight", 5:"Ferz", 6:"Princess", 7:"Empress"}


# Helper functions to aid in your implementation. Can edit/remove
#############################################################################
######## Piece
#############################################################################
class Piece:
    def __init__(self, name):
        self.name = name
        self.threat_no = 0
    
    def __str__(self):
        return '{},{}'.format(self.name, self.threat_no)
    
    def test_and_append(self, new_pos, r_step, c_step, pos, board, rows, cols):
        if pos[0] + r_step >= 0 and pos[0] + r_step < rows and \
            pos[1] + c_step >= 0 and pos[1] + c_step < cols:
            dest_cost = board[pos[0] + r_step][pos[1] + c_step]
            if dest_cost >= 0:
                new_pos.append( (pos[0] + r_step, pos[1] + c_step) )
                return True
            elif dest_cost <= -10:
                self.threat_no += 1
                return False
            elif dest_cost == -1:
                return False
        else:
            return False

    def loop_test_and_append(self, new_pos, r_dir, c_dir, pos, board, rows, cols):
            for factor in range(1, max(rows, cols)):
                if self.test_and_append(new_pos, r_dir * factor, c_dir * factor, pos, board, rows, cols):
                    continue
                else:
                    break       
    
    # Given a piece and its current position, returns an array of tuples of its new possible locations
    def get_actions(self, pos, board, rows, cols):
        self.threat_no = 0
        new_pos = []
        if self.name == "King":
            for r in [-1, 0, 1]:
                for c in [-1, 0, 1]:
                    if r == 0 and c == 0:
                        continue
                    self.test_and_append(new_pos, r, c, pos, board, rows, cols)
        elif self.name == "Rook":
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_append(new_pos, r_dir, c_dir, pos, board, rows, cols)
        elif self.name == "Bishop":
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_append(new_pos, r_dir, c_dir, pos, board, rows, cols)
        elif self.name == "Queen":
            for r_dir in [-1, 0, 1]:
                for c_dir in [-1, 0, 1]:
                    if r_dir == 0 and c_dir == 0:
                        continue
                    self.loop_test_and_append(new_pos, r_dir, c_dir, pos, board, rows, cols)
        elif self.name == "Knight":
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], pos, board, rows, cols)
        elif self.name == "Ferz":
            for r in [-1, 1]:
                for c in [-1, 1]:
                    self.test_and_append(new_pos, r, c, pos, board, rows, cols)
        elif self.name == "Princess": # Kight + Bishop
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], pos, board, rows, cols)
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    self.loop_test_and_append(new_pos, r_dir, c_dir, pos, board, rows, cols)            
        elif self.name == "Empress": # Kight + Rook
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                self.test_and_append(new_pos, move[0], move[1], pos, board, rows, cols)
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.loop_test_and_append(new_pos, r_dir, c_dir, pos, board, rows, cols)
        return new_pos

#############################################################################
######## Board
#############################################################################

# board[r][c] values meaning:
#  == 0: Free location
#  == -1: Obstacle
#  <= -10: Ocupied by a piece specified by a number <= -10
#  >= 1: Number of pieces that threaten this position (aka number of the "layers" of threat)

#############################################################################
######## Helper functions
#############################################################################

# TODO: Comment out this function
# def print_board(board, rows, cols):
#     for i in range(0, rows):
#         for j in range(0, cols):
#             if board[i][j] >= -1:
#                 print("{:<20s}".format(str(board[i][j])), end="")
#             elif board[i][j] <= -10:
#                 piece_name = number_to_piece_dict[board[i][j]]
#                 piece = Piece(piece_name)
#                 piece.get_actions((i, j), board, rows, cols)
#                 print("{:<20s}".format(str(piece)), end="")
#         print()

def format_solution(assignments):
    formatted_dict = {}
    for piece_tup in assignments:
        pos_tup = assignments[piece_tup]
        formatted_pos = (chr(pos_tup[1] + 97), pos_tup[0])
        formatted_dict[formatted_pos] = piece_tup[0]
    return formatted_dict

            
# Order of choosing piece: Queen(1) > Empress(7) > Princess(6) > Rook(3) > Bishop(2) > King(0) > Knight(4) > Ferz(5)
def select_unassigned_var(unassigned_pce_arr):
    if unassigned_pce_arr[1] > 0:
        return "Queen", unassigned_pce_arr[1], 1
    if unassigned_pce_arr[7] > 0:
        return "Empress", unassigned_pce_arr[7], 7
    if unassigned_pce_arr[6] > 0:
        return "Princess", unassigned_pce_arr[6], 6
    if unassigned_pce_arr[3] > 0:
        return "Rook", unassigned_pce_arr[3], 3
    if unassigned_pce_arr[2] > 0:
        return "Bishop", unassigned_pce_arr[2], 2
    if unassigned_pce_arr[0] > 0:
        return "King", unassigned_pce_arr[0], 0
    if unassigned_pce_arr[4] > 0:
        return "Knight", unassigned_pce_arr[4], 4
    if unassigned_pce_arr[5] > 0:
        return "Ferz", unassigned_pce_arr[5], 5
    return None, None, None

# If val1 < val2 (val1 is ordered first), func should return negative. 
# manh(val1) > manh(val2), so return manh(val2) - manh(val1) < 0
def order_domain_values(free_location_arr):
    # r_center = (rows - 1) / 2
    # c_center = (cols - 1) / 2

    # def cmp_manh_dist(val1, val2):
    #     return (abs(val2[0] - r_center) + abs(val2[1] - c_center)) - (abs(val1[0] - r_center) + abs(val1[1] - c_center))
    
    # return sorted(free_location_arr, key = cmp_to_key(cmp_manh_dist))
    random.shuffle(free_location_arr)
    return free_location_arr

def backtrack(board, safe_location_arr, unassigned_pce_arr, assignments, rows, cols):
    if sum(unassigned_pce_arr) == 0:
        # return board
        # TODO: Change return to next line
        return assignments
    chosen_piece_name, chosen_piece_num, chosen_piece_index = select_unassigned_var(unassigned_pce_arr)
    curr_piece = Piece(chosen_piece_name)
    for pos in order_domain_values(safe_location_arr): # Pos is a position tuple
        curr_threat_pos = curr_piece.get_actions(pos, board, rows, cols)
        if curr_piece.threat_no == 0: # If new pos assignment is consistent with existing assignment:
            # Add var = value to assignment
            assignments[(chosen_piece_name, chosen_piece_num)] = pos
            unassigned_pce_arr[chosen_piece_index] -= 1
            board[pos[0]][pos[1]] = piece_to_number_dict[chosen_piece_name] # Update board value to number corresponding to piece
            safe_location_arr.remove(pos)

            is_inference_success = len(safe_location_arr) >= sum(unassigned_pce_arr)
            if is_inference_success:
                # Add inference to CSP
                for threat_pos in curr_threat_pos:
                    board[threat_pos[0]][threat_pos[1]] += 1
                    if board[threat_pos[0]][threat_pos[1]] == 1:
                        safe_location_arr.remove(threat_pos)
                
                result = backtrack(board, safe_location_arr, unassigned_pce_arr, assignments, rows, cols)
                
                if result != False:
                    return result
                
                # Remove inference from CSP
                for threat_pos in curr_threat_pos:
                    board[threat_pos[0]][threat_pos[1]] -= 1
                    if board[threat_pos[0]][threat_pos[1]] == 0:
                        safe_location_arr.append(threat_pos)

            # Remove var = value from assignment
            del assignments[(chosen_piece_name, chosen_piece_num)]
            unassigned_pce_arr[chosen_piece_index] += 1
            board[pos[0]][pos[1]] = 0
            safe_location_arr.append(pos)
    return False


#############################################################################
######## Implement Search Algorithm
#############################################################################
def search(rows, cols, grid, num_pieces):
    random.seed(1)
    board = grid
    unassigned_pce_arr = list(num_pieces)
    assignments = {} # (piece_name, piece_no) : pos
    safe_location_arr = []
    for i in range(0, rows):
        for j in range(0, cols):
            if board[i][j] == 0:
                safe_location_arr.append((i,j))

    result = backtrack(board, safe_location_arr, unassigned_pce_arr, assignments, rows, cols)
    # return result
    # TODO: Change return to next line
    return format_solution(result)


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

    num_obstacles = int(get_par(handle.readline()))
    if num_obstacles > 0:
        for ch_coord in get_par(handle.readline()).split():  # Init obstacles
            r, c = from_chess_coord(ch_coord)
            grid[r][c] = -1
    else:
        handle.readline()
    
    piece_nums = get_par(handle.readline()).split()
    num_pieces = [int(x) for x in piece_nums] #List in the order of King, Queen, Bishop, Rook, Knight

    return rows, cols, grid, num_pieces

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
# testcase = "Test/CSP1.txt"
# rows, cols, grid, num_pieces = parse(testcase)

def run_CSP():
    testcase = sys.argv[1] #Do not remove. This is your input testfile.
    rows, cols, grid, num_pieces = parse(testcase)
    goalstate = search(rows, cols, grid, num_pieces)
    return goalstate #Format to be returned
