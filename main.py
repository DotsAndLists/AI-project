import random
import os
from Game.board import Board
from Game.ship import Ship
from Game.gamestate import GameState

# Create game state with 4x4 board
gs = GameState(4)

# Place ships manually for testing
gs.player_board.add_ship(Ship("Destroyer", [(0,0), (0,1)]))
gs.player_board.add_ship(Ship("Submarine", [(2,2), (3,2)]))

gs.ai_board.add_ship(Ship("Destroyer", [(1,1), (1,2)]))
gs.ai_board.add_ship(Ship("Submarine", [(3,0), (3,1)]))

# Function to display board nicely
def display_board(board, reveal_ships=False):
    # Flip board so bottom row is 0
    for r in reversed(range(board.size)):
        row_display = []
        for c in range(board.size):
            cell = board.grid.get((r, c), ".")
            if cell == "ship" and reveal_ships:
                row_display.append("S")
            elif cell == "already_hit":
                row_display.append("X")
            elif cell == "miss":
                row_display.append("O")
            else:
                row_display.append(".")
        print(" ".join(row_display))
    print()  # blank line

# Keep track of AI moves to avoid repeats
ai_possible_moves = [(r, c) for r in range(gs.size) for c in range(gs.size)]

# Main game loop
while not gs.game_over:
    os.system('cls' if os.name == 'nt' else 'clear')  # optional clear screen
    
    print("Your board:")
    display_board(gs.player_board, reveal_ships=True)
    
    print("Opponent board:")
    display_board(gs.ai_board, reveal_ships=False)
    
    # Player move
    while True:
        try:
            col = int(input(f"Enter column (1-{gs.size}): ")) - 1
            row = int(input(f"Enter row (1-{gs.size}): ")) - 1
            coord = (row, col)
            if coord in [move["coord"] for move in gs.player_moves]:
                print("You already shot there! Try again.")
            elif row < 0 or row >= gs.size or col < 0 or col >= gs.size:
                print("Out of bounds. Try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Enter numbers only.")
    
    result = gs.make_move(coord)
    print(f"You fired at ({col+1},{row+1}): {result}\n")
    
    if gs.game_over:
        break
    
    # AI move
    ai_coord = random.choice(ai_possible_moves)
    ai_possible_moves.remove(ai_coord)  # remove so AI cannot repeat
    ai_result = gs.make_move(ai_coord)
    print(f"AI fired at ({ai_coord[1]+1},{ai_coord[0]+1}): {ai_result}\n")
    
print("Game Over!")
print(f"Winner: {gs.winner}")
