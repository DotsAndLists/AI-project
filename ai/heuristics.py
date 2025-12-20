def get_probability_grid(board, remaining_ships, rl_brain=None): # <--- Added rl_brain param
    """
    Generates a probability grid based on the remaining ships and the current board state.
    Now accounts for the rule: SHIPS CANNOT TOUCH + RL BIAS.
    """
    size = board.size
    prob_grid = [[0 for _ in range(size)] for _ in range(size)]

    # --- STEP 1: CREATE FORBIDDEN ZONES ---
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
                forbidden_mask.add((sr, sc))
                # Add neighbors
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
                    if coord in forbidden_mask:
                        valid_placement = False; break
                    if board.grid.get(coord) == "already_hit" and coord not in forbidden_mask: pass
                    elif board.grid.get(coord) == "already_hit": valid_placement = False; break
                    possible_coords.append(coord)
                
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        weight = 10 if board.grid.get((pr, pc)) == "already_hit" else 1
                        prob_grid[pr][pc] += weight

        # Try Vertical Placements
        for r in range(size - length + 1):
            for c in range(size):
                possible_coords = []
                valid_placement = True
                for i in range(length):
                    coord = (r + i, c)
                    if coord in forbidden_mask:
                        valid_placement = False; break
                    if board.grid.get(coord) == "already_hit" and coord not in forbidden_mask: pass
                    elif board.grid.get(coord) == "already_hit": valid_placement = False; break
                    possible_coords.append(coord)
                
                if valid_placement:
                    for (pr, pc) in possible_coords:
                        weight = 10 if board.grid.get((pr, pc)) == "already_hit" else 1
                        prob_grid[pr][pc] += weight

    # --- STEP 3: APPLY REINFORCEMENT LEARNING BIAS ---
    if rl_brain:
        for r in range(size):
            for c in range(size):
                if board.grid.get((r, c)) not in ["miss", "already_hit"]:
                    bias = rl_brain.get_bias_score(r, c)
                    prob_grid[r][c] += bias
                        
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