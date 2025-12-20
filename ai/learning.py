import json
import os

MEMORY_FILE = "ai_memory.json"

class RLBrain:
    def __init__(self, size=10):
        self.size = size
        self.memory_grid = self.load_memory()

    def load_memory(self):
        """Loads the heatmap from a JSON file. If none exists, creates a blank one."""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                try:
                    data = json.load(f)
                    # Simple check to ensure size matches
                    if len(data) == self.size:
                        return data
                except:
                    pass
        # Return empty grid of zeros
        return [[0 for _ in range(self.size)] for _ in range(self.size)]

    def save_memory(self):
        """Saves current heatmap to file."""
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory_grid, f)

    def learn_from_game(self, opponent_board):
        """
        Called at the end of a game. 
        Scans the opponent's TRUE board and updates frequency counts.
        """
        # We need to look at the opponent's ships, even the ones we didn't hit!
        for r in range(self.size):
            for c in range(self.size):
                # If there is a ship here (hit or unhit)
                cell = opponent_board.grid.get((r, c))
                if cell == "ship" or cell == "already_hit":
                    self.memory_grid[r][c] += 1
        
        self.save_memory()

    def get_bias_score(self, r, c):
        """
        Returns a small bonus score based on how often ships appear here.
        We scale it down so it doesn't overpower the main logic.
        """
        raw_count = self.memory_grid[r][c]
        
        # Scaling factor: Divides by 10 so logic is still #1, but memory breaks ties
        return raw_count / 10.0