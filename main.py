import os
from Game.board import Board
from Game.ship import Ship
from Game.gamestate import GameState
from ai.search import SearchAI  # <--- IMPORT YOUR NEW BRAIN

# --- 1. SETUP THE GAME ---

# Create game state
gs = GameState(5)

# Initialize your AI Bot
# We pass the size so it knows boundaries
ai_bot = SearchAI(gs.size) 

# Place ships manually for testing
# (Later you can make a function to place these randomly)
gs.player_board.add_ship(Ship("Destroyer", [(0,0), (0,1)]))
gs.player_board.add_ship(Ship("Submarine", [(2,2), (3,2)]))

gs.ai_board.add_ship(Ship("Destroyer", [(1,1), (1,2)]))
gs.ai_board.add_ship(Ship("Submarine", [(3,0), (3,1)]))


# Function to display board nicely
def display_board(board, reveal_ships=False):
    print("   1 2 3 4 5") # Header for columns
    print("  " + "-" * 11)
    for r in range(board.size): # Going 0 to 4
        row_display = []
        for c in range(board.size):
            cell = board.grid.get((r, c), ".")
            
            if cell == "ship" and reveal_ships:
                row_display.append("S")
            elif cell == "already_hit":
                row_display.append("X")
            elif cell == "miss":
                row_display.append("O")
            elif cell == "ship": # Hidden ship
                row_display.append(".")
            else:
                row_display.append(".")
                
        print(f"{r+1}| " + " ".join(row_display))
    print()


# --- 2. THE GAME LOOP ---

while not gs.game_over:
    
    # Print status
    print("\n" + "="*20)
    print("OPPONENT BOARD (AI)")
    display_board(gs.ai_board, reveal_ships=False) # Hide AI ships
    
    print("YOUR BOARD")
    display_board(gs.player_board, reveal_ships=True) # Show your ships

    # --- PLAYER TURN ---
    while True:
        try:
            raw_col = input(f"Enter column (1-{gs.size}) or 'quit': ").strip().lower()
            if raw_col == "quit":
                gs.game_over = True
                break
                
            raw_row = input(f"Enter row (1-{gs.size}): ").strip().lower()
            
            col = int(raw_col) - 1
            row = int(raw_row) - 1
            coord = (row, col)

            # Validation
            if row < 0 or row >= gs.size or col < 0 or col >= gs.size:
                print("Out of bounds.")
            elif coord in [m["coord"] for m in gs.player_moves]:
                print("You already shot there.")
            else:
                break # Valid input
        except ValueError:
            print("Please enter valid numbers.")

    if gs.game_over:
        break

    # Execute Player Move
    result = gs.make_move(coord)
    print(f"\n>>> You fired at ({col+1}, {row+1}): {result.upper()}")

    if gs.game_over:
        break
    
    # --- AI TURN (The New Part) ---
    
    # 1. Ask the AI Brain for the best coordinate
    # Note: We pass gs.player_board because the AI is looking at YOUR board
    ai_coord = ai_bot.get_next_move(gs.player_board)
    
    # 2. Execute the move in the Game Engine
    ai_result = gs.make_move(ai_coord)
    
    # 3. Tell the AI Brain what happened so it can learn
    # (If it hit, it switches to Target Mode. If it sunk, it goes back to Hunt Mode)
    ai_bot.update_result(ai_coord, ai_result, gs.player_board)
    
    print(f">>> AI fired at ({ai_coord[1]+1}, {ai_coord[0]+1}): {ai_result.upper()}")


# --- 3. GAME OVER ---

print("\n" + "="*30)
if gs.winner == "player":
    print("CONGRATULATIONS! You sank the AI fleet!")
elif gs.winner == "ai":
    print("GAME OVER. The AI sank your fleet.")
else:
    print("Game ended.")

print("\nFinal AI Board Layout:")
display_board(gs.ai_board, reveal_ships=True)