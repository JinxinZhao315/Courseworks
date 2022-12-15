class Piece:
    pass

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


rows, cols, grid, enemy_pieces, own_pieces, goals = parse("1.txt")

# State: grid + king's position


def print_state(grid, pos):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(str(grid[i][j]) + "\t", end="")
        print()
    print("Kings current pos", end="")
    print(pos)

def get_king_moves(grid, pos):
    new_poss = []
    if pos[0]-1 >= 0 and \
       grid[pos[0]-1][pos[1]] >= 0: # try north
        new_poss.append(pos[0]-1, pos[1])
        
    if pos[0]-1 >= 0 and pos[0]-1 < len(grid) and \
       pos[1]+1 >= 0 and pos[1]+1 < len(grid[0]) and \
       grid[pos[0]-1][pos[1]+1] >= 0: # try NE
        new_poss.append(pos[0]-1, pos[1]+1)
        
    if pos[1]+1 >= 0 and pos[0]+1 < len(grid) and \
       grid[pos[0]][pos[1]+1] >= 0: # try E
        new_poss.append(pos[0], pos[1]+1)
        
    if pos[0]+1 >= 0 and pos[0]+1 < len(grid) and \
       pos[1]+1 >= 0 and pos[1]+1 < len(grid[0]) and \
       grid[pos[0]+1][pos[1]+1] >= 0: # try SE
        new_poss.append(pos[0]+1, pos[1]+1)
    
    if pos[0]-1 >= 0 and pos[0]-1 < len(grid) and pos[1]+1 > 0 and pos[1]+1 < len(grid[0]) and grid[pos[0]-1][pos[1]+1] >= 0: # try NE
        new_poss.append(pos[0]-1, pos[1]+1)
        
    if pos[0]-1 >= 0 and pos[0]-1 < len(grid) and pos[1]+1 > 0 and pos[1]+1 < len(grid[0]) and grid[pos[0]-1][pos[1]+1] >= 0: # try NE
        new_poss.append(pos[0]-1, pos[1]+1)
        
    if pos[0]-1 >= 0 and pos[0]-1 < len(grid) and pos[1]+1 > 0 and pos[1]+1 < len(grid[0]) and grid[pos[0]-1][pos[1]+1] >= 0: # try NE
        new_poss.append(pos[0]-1, pos[1]+1)

    return new_poss

def actions(grid, pos):
    return get_king_moves(grid,pos)


def is_goal(pos,goals):
    for i in range (len(goals)):
        if pos == goals[i]:
            return True
    return False

def search(rows,cols, grid, enemy_pieces, own_pieces, goals):
    frontier = [(own_pieces[0][1], [])] # Node: (current_pos, path)
    while len(frontier) > 0:
        current = frontier.pop() # Pop from the back
        if is_goal(current[0], goals):
            return current[1]
        for a in actions(grid, current[0]):
            frontier.insert(0, (a, current[1].append(current[0]))) # Insert at the front. a is the new position moved to
    return []


# To do:
# Update grid to include enemy and threatened positions. Everywhere an enemy can move to is a threatened position

    
