def get_probability_grid(board, remaining_ships):
    """
    Generates a probability grid based on the remaining ships and the current board state.
    Now accounts for the rule: SHIPS CANNOT TOUCH.
    """
    size = board.size
    prob_grid = [[0 for _ in range(size)] for _ in range(size)]

    # --- STEP 1: CREATE FORBIDDEN ZONES ---
    # We identify spots where ships definitely CANNOT be.
    # 1. Misses
    # 2. Sunk Ships (and their neighbors!)
    forbidden_mask = set()

    # Add all known misses
    for r in range(size):
        for c in range(size):
            if board.grid.get((r, c)) == "miss":
                forbidden_mask.add((r, c))

    # Add Sunk Ships AND their Buffer Zones
    for ship in board.ships:
        if ship.is_sunk():
            for (sr, sc) in ship.coord:
                # Add the ship part itself
                forbidden_mask.add((sr, sc))
                
                # Add all 8 neighbors (The Buffer Zone)
                # Because no OTHER ship can touch this sunk ship
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = sr + dr, sc + dc
                        if 0 <= nr < size and 0 <= nc < size:
                            forbidden_mask.add((nr, nc))

    # --- STEP 2: SLIDING WINDOW (The Heatmap) ---
    ship_lengths = [len(ship.coord) for ship in remaining_ships]

    for length in ship_lengths:
        # Try Horizontal Placements
        for r in range(size):
            for c in range(size - length + 1): 
                possible_coords = []
                valid_placement = True
                
                for i in range(length):
                    coord = (r, c + i)
                    
                    # NEW CHECK: Is this spot forbidden?
                    # (This covers misses, sunk ships, AND the buffer zones around sunk ships)
                    if coord in forbidden_mask:
                        valid_placement = False
                        break
                        
                    # Also check "already_hit"
                    # If we hit something that ISN'T sunk, we can overlap it (it might be us!)
                    # But if we overlap a hit that IS sunk, forbidden_mask catches it.
                    if board.grid.get(coord) == "already_hit" and coord not in forbidden_mask:
                         # Valid to assume this hit belongs to the ship we are testing
                         pass
                    elif board.grid.get(coord) == "already_hit":
                         # If it's a hit inside a forbidden zone (impossible?), mark invalid
                         valid_placement = False
                         break

                    possible_coords.append(coord)
                
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        # Weight it slightly higher if it overlaps an existing active hit
                        # (Encourages targeting the rest of a found ship)
                        if board.grid.get((pr, pc)) == "already_hit":
                            prob_grid[pr][pc] += 10 # massive bonus to finish ships
                        else:
                            prob_grid[pr][pc] += 1

        # Try Vertical Placements
        for r in range(size - length + 1):
            for c in range(size):
                possible_coords = []
                valid_placement = True
                
                for i in range(length):
                    coord = (r + i, c)
                    
                    if coord in forbidden_mask:
                        valid_placement = False
                        break

                    possible_coords.append(coord)
                
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        if board.grid.get((pr, pc)) == "already_hit":
                            prob_grid[pr][pc] += 10
                        else:
                            prob_grid[pr][pc] += 1
                        
    return prob_grid

def get_best_hunt_move(board, prob_grid):
    """
    Finds the coordinate with the highest probability score that hasn't been shot at.
    """
    best_score = -1
    best_move = None
    
    for r in range(board.size):
        for c in range(board.size):
            coord = (r, c)
            
            # Skip spots we already shot at
            if coord in board.shots_taken:
                continue
                
            score = prob_grid[r][c]
            
            if score > best_score:
                best_score = score
                best_move = coord
            # Tie-breaker: Prefer parity squares (checkerboard) to save moves
            elif score == best_score:
                if (r + c) % 2 == 0: # Simple checkerboard logic
                     best_move = coord
                
    return best_move