import sys

# Helper functions to aid in your implementation. Can edit/remove
#############################################################################
######## Piece
#############################################################################
class Piece:
    def __init__(self, name, side):
        self.name = name
        if side == "Own":
            self.is_enemy = False
        elif side == "Enemy":
            self.is_enemy = True
    
    def get_actions(self, pos, board, rows, cols):
        new_pos = []

        # Test if, given current pos, moving r_step and c_step on the board will be a legal move. 
        # If legal, append the new position to the new_pos list
        # A legal move does not 1. Go out of bound, 2. Step into obstacle or threatened position
        def test_and_append(is_enemy, r_step, c_step, new_pos):
            if pos[0] + r_step >= 0 and pos[0] + r_step < rows and \
                pos[1] + c_step >= 0 and pos[1] + c_step < cols:
                dest_cost = board[pos[0] + r_step][pos[1] + c_step]
                if is_enemy == False:
                    is_unblocked = dest_cost >= 0
                else:
                    is_unblocked = dest_cost >= 0 or dest_cost == -2
                # For enemy pieces, threatened positions (cost = -2) of another enemy 
                # don't block the threat area of current enemy like an obstacle,
                # so threatened positions are allowed to go through cost=-2 cells
                if is_unblocked:
                    new_pos.append( (pos[0] + r_step, pos[1] + c_step) )
                    return True
                else:
                    return False
            else:
                return False

        # Generates new positions for pieces that can keep moving in a certain direction (r_dir, c_dir) 
        # until going out of bound or hit obstacle.
        def loop_test_and_append(is_enemy, r_dir, c_dir, new_pos):
                for factor in range(1, max(rows, cols)):
                    if test_and_append(is_enemy, r_dir * factor, c_dir * factor, new_pos):
                        continue
                    else:
                        break     

        if self.name == "King":
            for r in [-1, 0, 1]:
                for c in [-1, 0, 1]:
                    if r == 0 and c == 0:
                        continue
                    test_and_append(self.is_enemy, r, c, new_pos)
        elif self.name == "Rook":
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                loop_test_and_append(self.is_enemy, r_dir, c_dir, new_pos)
        elif self.name == "Bishop":
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    loop_test_and_append(self.is_enemy, r_dir, c_dir, new_pos)
        elif self.name == "Queen":
            for r_dir in [-1, 0, 1]:
                for c_dir in [-1, 0, 1]:
                    if r_dir == 0 and c_dir == 0:
                        continue
                    loop_test_and_append(self.is_enemy, r_dir, c_dir, new_pos)
        elif self.name == "Knight":
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                test_and_append(self.is_enemy, move[0], move[1], new_pos)
        elif self.name == "Ferz":
            for r in [-1, 1]:
                for c in [-1, 1]:
                    test_and_append(self.is_enemy, r, c, new_pos)
        elif self.name == "Princess": # Kight + Bishop
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                test_and_append(self.is_enemy, move[0], move[1], new_pos)
            for r_dir in [1, -1]:
                for c_dir in [1, -1]:
                    loop_test_and_append(self.is_enemy, r_dir, c_dir, new_pos)            
        elif self.name == "Empress": # Kight + Rook
            for move in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1)]:
                test_and_append(self.is_enemy, move[0], move[1], new_pos)
            for (r_dir, c_dir) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                loop_test_and_append(self.is_enemy, r_dir, c_dir, new_pos)
        return new_pos

#############################################################################
######## Board
#############################################################################
class Board:
    def __init__(self, grid, enemy_pieces, rows, cols):
        self.board = grid
        for enemy in enemy_pieces:
            self.board[enemy[1][0]][enemy[1][1]] = -10  # Enemy position is marked as -10 on board
            # All enemy pieces must be placed down first 
            # before we can test for negative values on board in the next loop
        for enemy in enemy_pieces:
            piece = Piece(enemy[0], "Enemy")
            for threat_pos in piece.get_actions(enemy[1], self.board, rows, cols):
                self.board[threat_pos[0]][threat_pos[1]] = -2  # Threatened position is marked as -2
            

#############################################################################
######## Node
#############################################################################

class Node:
    def __init__(self, state, path, cost):
        self.state = state # State = own king's position
        self.path = path
        self.cost = cost


#############################################################################
######## Helper functions
#############################################################################

# TODO: Delete next 2 lines when submitting
# rows, cols, grid, enemy_pieces, own_pieces, goals = parse("Test/4.txt")
# board = Board(grid, enemy_pieces, rows, cols)

# def print_grid(grid, own_pieces, goals, solution_list):
#     for i in range(len(grid)):
#         for j in range(len(grid[i])):
#             if (i,j) in goals:
#                 print('G' + "\t", end="")
#             elif (i,j) == own_pieces[0][1]:
#                 print('S' + "\t", end="")
#             elif (i,j) in solution_list:
#                 print("X" + "\t", end="")
#             else:
#                 print(str(grid[i][j]) + "\t", end="")
#         print()
        
def is_goal(current_pos, goals):
    return current_pos in goals

def format_solution(solution_list):
    formatted_list = []
    output_list = []
    for tup in solution_list:
        formatted_list.append( (chr(tup[1] + 97), tup[0]) )
    for i in range(len(formatted_list) - 1):
        output_list.append([ (formatted_list[i]), (formatted_list[i+1]) ] )
    return output_list
        

#############################################################################
######## Implement Search Algorithm
#############################################################################
def search(rows, cols, grid, enemy_pieces, own_pieces, goals):
    king = Piece("King", "Own")
    board = Board(grid, enemy_pieces, rows, cols).board
    reached_dict = {own_pieces[0][1] : 0} # {state : cost to state}
    frontier = [ Node(own_pieces[0][1], [], 0) ]
    while (len(frontier) > 0):
        curr_node = frontier.pop(0)
        # print('curr node: {}, {}, {}'.format(curr_node.state, curr_node.path, curr_node.cost))
        if is_goal(curr_node.state, goals):
            # print("Finished")
            return format_solution(curr_node.path + [curr_node.state])
            # return curr_node.path + [curr_node.state]
        for new_pos in king.get_actions(curr_node.state, board, rows, cols):
            new_cost = curr_node.cost + board[new_pos[0]][new_pos[1]]
            if new_pos not in reached_dict or new_cost < reached_dict[new_pos]:
                new_path = curr_node.path + [curr_node.state]
                frontier.append( Node(new_pos, new_path, new_cost) )
                reached_dict[new_pos] = new_cost
    return []


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
    grid = [[1 for j in range(cols)] for i in range(rows)] # Dictionary, label empty spaces as 1 (Default Step Cost)
    enemy_pieces = [] # List
    own_pieces = [] # List
    goals = [] # List

    handle.readline()  # Ignore number of obstacles
    for ch_coord in get_par(handle.readline()).split():  # Init obstacles
        r, c = from_chess_coord(ch_coord)
        grid[r][c] = -1 # Label Obstacle as -1

    handle.readline()  # Ignore Step Cost header
    line = handle.readline()
    while line.startswith("["):
        line = line[1:-2].split(",")
        r, c = from_chess_coord(line[0])
        grid[r][c] = int(line[1]) if grid[r][c] == 1 else grid[r][c] #Reinitialize step cost for coordinates with different costs
        line = handle.readline()
    
    line = handle.readline() # Read Enemy Position
    while line.startswith("["):
        line = line[1:-2]
        piece = add_piece(line)
        enemy_pieces.append(piece)
        line = handle.readline()

    # Read Own King Position
    line = handle.readline()[1:-2]
    piece = add_piece(line)
    own_pieces.append(piece)

    # Read Goal Positions
    for ch_coord in get_par(handle.readline()).split():
        r, c = from_chess_coord(ch_coord)
        goals.append((r, c))
    
    return rows, cols, grid, enemy_pieces, own_pieces, goals

def add_piece( comma_seperated) -> Piece:
    piece, ch_coord = comma_seperated.split(",")
    r, c = from_chess_coord(ch_coord)
    return [piece, (r,c)]

def from_chess_coord( ch_coord):
    return (int(ch_coord[1:]), ord(ch_coord[0]) - 97)

#############################################################################
######## Main function to be called
#############################################################################
### DO NOT EDIT/REMOVE THE FUNCTION BELOW###
# To return: List of moves
# Return Format Example: [[('a', 0), ('a', 1)], [('a', 1), ('c', 3)], [('c', 3), ('d', 5)]]
def run_BFS():    
    testcase = sys.argv[1]
    rows, cols, grid, enemy_pieces, own_pieces, goals = parse(testcase)
    moves = search(rows, cols, grid, enemy_pieces, own_pieces, goals)
    return moves
    

