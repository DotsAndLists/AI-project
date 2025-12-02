#heristics is based on how good a move is, which is which space has the highest mathematical probability of containing a ship.
#this is done by generating a heatmap, that would take every enemy boat that is still alive, and try to fit it in every space. if it can fit the space, it gets a +1
# the spot with the highest score will be shot, prefers the middle as more places for ships to be

#two phases, the hunt phase (global search in whole board when no ship is partially hit) 
# and the target phase (local search when you have partially hit a ship, ignored global search and does local DFS and puts each dir in a stack/queue)


# heuristics.py

def get_probability_grid(board, remaining_ships):
    """
    Generates a probability grid based on the remaining ships and the current board state.
    
    Args:
        board: The Board object (opponent's board).
        remaining_ships: A list of Ship objects that have NOT been sunk yet.
    
    Returns:
        A 2D list (grid) of probability scores.
    """
    size = board.size
    # Initialize a grid of zeros
    prob_grid = [[0 for _ in range(size)] for _ in range(size)]

    # We need the lengths of the remaining ships to try fitting them
    ship_lengths = [len(ship.coord) for ship in remaining_ships]

    for length in ship_lengths:
        # --- 1. Try Horizontal Placements ---
        for r in range(size):
            # c ranges so the ship fits horizontally
            for c in range(size - length + 1): 
                
                # Check if this placement is valid (no "miss" or "already_hit" blocking it)
                valid_placement = True
                possible_coords = []
                
                for i in range(length):
                    coord = (r, c + i)
                    # We check what is currently KNOWN about this spot.
                    # We treat hidden "ship" spots as valid because the AI doesn't know they are there yet.
                    # We only avoid known 'miss' or 'already_hit' spots.
                    status = board.grid.get(coord)
                    
                    if status == "miss" or status == "already_hit":
                        valid_placement = False
                        break
                    possible_coords.append(coord)
                
                # If the ship fits here, increase probability score for every cell it covers
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        prob_grid[pr][pc] += 1

        # --- 2. Try Vertical Placements ---
        for r in range(size - length + 1):
            for c in range(size):
                
                valid_placement = True
                possible_coords = []
                
                for i in range(length):
                    coord = (r + i, c)
                    status = board.grid.get(coord)
                    
                    if status == "miss" or status == "already_hit":
                        valid_placement = False
                        break
                    possible_coords.append(coord)
                
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        prob_grid[pr][pc] += 1
                        
    return prob_grid

def get_best_hunt_move(board, prob_grid):
   
    best_score = -1
    best_move = None
    
    for r in range(board.size):
        for c in range(board.size):
            coord = (r, c)
            
            # Skip spots we already shot at
            if coord in board.shots_taken:
                continue
                
            score = prob_grid[r][c]
            
            # Update best found
            if score > best_score:
                best_score = score
                best_move = coord
                
    return best_move