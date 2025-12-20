import random
from ai.heuristics import get_probability_grid, get_best_hunt_move

class SearchAI:
    def __init__(self, board_size):
        self.mode = "hunt"
        self.target_stack = [] 
        self.current_hits = [] # NEW: Tracks the specific hits on the current ship

    def get_next_move(self, opponent_board, rl_brain=None): # <--- Accept rl_brain
        if self.mode == "target":
            # ... (Target Mode logic stays exactly the same) ...
            if self.target_stack:
                next_target = self.target_stack.pop()
                while next_target in opponent_board.shots_taken:
                    if not self.target_stack:
                        self.mode = "hunt"
                        return self.get_next_move(opponent_board, rl_brain) # Pass it here too
                    next_target = self.target_stack.pop()
                return next_target
            else:
                self.mode = "hunt"
        
        # Hunt Mode logic 
        remaining_ships = [s for s in opponent_board.ships if not s.is_sunk()]
        
        # PASS THE BRAIN TO THE HEURISTIC
        probs = get_probability_grid(opponent_board, remaining_ships, rl_brain)
        
        move = get_best_hunt_move(opponent_board, probs)
        
        if move is None:
            possible = [(r, c) for r in range(opponent_board.size) 
                       for c in range(opponent_board.size) 
                       if (r,c) not in opponent_board.shots_taken]
            return random.choice(possible) if possible else None
            
        return move

    def update_result(self, move, result, opponent_board):
        if "sunk" in result:
            self.target_stack = [] 
            self.current_hits = [] # Reset hits when ship sinks
            self.mode = "hunt"
            
        elif result == "hit":
            self.mode = "target"
            self.current_hits.append(move) # Add this hit to our list
            
            # --- INTELLIGENT TARGETING ---
            
            # 1. Determine the neighbors
            (r, c) = move
            neighbors = [
                (r+1, c), (r-1, c), (r, c+1), (r, c-1)
            ]
            
            # 2. Filter invalid neighbors (off board or already shot)
            valid_neighbors = []
            for n in neighbors:
                nr, nc = n
                if 0 <= nr < opponent_board.size and 0 <= nc < opponent_board.size:
                    if n not in opponent_board.shots_taken:
                        valid_neighbors.append(n)

            # 3. CHECK ALIGNMENT (The Fix)
            # If we have 2 or more hits, we can check if they form a line.
            if len(self.current_hits) >= 2:
                # Get the first two hits to compare
                h1 = self.current_hits[0]
                h2 = self.current_hits[1]
                
                # Check if Horizontal (Rows match)
                if h1[0] == h2[0]: 
                    # Keep ONLY horizontal neighbors (same Row)
                    valid_neighbors = [n for n in valid_neighbors if n[0] == h1[0]]
                    # Also CLEAN the existing stack of bad vertical shots
                    self.target_stack = [t for t in self.target_stack if t[0] == h1[0]]
                    
                # Check if Vertical (Cols match)
                elif h1[1] == h2[1]: 
                    # Keep ONLY vertical neighbors (same Col)
                    valid_neighbors = [n for n in valid_neighbors if n[1] == h1[1]]
                    # Also CLEAN the existing stack of bad horizontal shots
                    self.target_stack = [t for t in self.target_stack if t[1] == h1[1]]

            # Add remaining valid neighbors to stack
            for vn in valid_neighbors:
                 # Avoid duplicates in stack
                if vn not in self.target_stack:
                    self.target_stack.append(vn)