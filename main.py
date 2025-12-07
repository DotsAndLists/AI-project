import os
from Game.board import Board
from Game.ship import Ship
from Game.gamestate import GameState
from ai.search import SearchAI

# --- 1. CONFIGURATION & SETUP ---

# Ask user for board size
while True:
    try:
        raw_size = input("Choose board size (5 or 10): ").strip()
        if raw_size in ["5", "10"]:
            BOARD_SIZE = int(raw_size)
            break
        print("Invalid choice. Please type 5 or 10.")
    except ValueError:
        pass

# Define fleets based on size
if BOARD_SIZE == 5:
    # Small fleet for small board
    fleets = [
        ("Submarine", 3),
        ("Destroyer", 2)
    ]
else:
    # Standard fleet for big board
    fleets = [
        ("Carrier", 5),
        ("Battleship", 4),
        ("Cruiser", 3),
        ("Submarine", 3),
        ("Destroyer", 2)
    ]

# Create game state
gs = GameState(BOARD_SIZE)

# Initialize the Smart AI
ai_bot = SearchAI(gs.size)

# Place ships randomly using the specific fleet list
gs.player_board.place_ships_randomly(fleets)
gs.ai_board.place_ships_randomly(fleets)


# Function to display board nicely
def display_board(board, reveal_ships=False):
    # Dynamic header numbers
    header_numbers = [str(i+1) for i in range(board.size)]
    print("    " + " ".join(header_numbers))
    print("   " + "-" * (board.size * 2 + 1))

    for r in range(board.size):
        row_display = []
        for c in range(board.size):
            cell = board.grid.get((r, c), ".")
            if cell == "ship" and reveal_ships:
                row_display.append("S")
            elif cell == "already_hit":
                row_display.append("X")
            elif cell == "miss":
                row_display.append("O")
            elif cell == "ship": 
                row_display.append(".") # Hide ship if not revealing
            else:
                row_display.append(".")
        
        # Formatting row numbers
        row_num = str(r + 1)
        if len(row_num) < 2: row_num += " "
        
        print(f"{row_num}| " + " ".join(row_display))
    print()


# --- 2. THE GAME LOOP ---
while not gs.game_over:
    # Removed screen clearing so scroll works
    # os.system('cls' if os.name == 'nt' else 'clear')

    print("Your board:")
    display_board(gs.player_board, reveal_ships=True)
    
    print(f"Opponent board ({gs.size}x{gs.size}):")
    display_board(gs.ai_board, reveal_ships=False)
    
    # Player move
    while True:
        raw_col = input(f"Enter column (1-{gs.size}) or type 'quit': ").strip().lower()
        if raw_col in ["quit", "stop"]:
            print("Game ended by player.")
            gs.game_over = True
            gs.winner = "none"
            break

        raw_row = input(f"Enter row (1-{gs.size}) or type 'quit': ").strip().lower()
        if raw_row in ["quit", "stop"]:
            print("Game ended by player.")
            gs.game_over = True
            gs.winner = "none"
            break

        try:
            col = int(raw_col) - 1
            row = int(raw_row) - 1
            coord = (row, col)

            if coord in [move["coord"] for move in gs.player_moves]:
                print("You already shot there! Try again.")
            elif row < 0 or row >= gs.size or col < 0 or col >= gs.size:
                print("Out of bounds. Try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Enter numbers only.")

    if gs.game_over:
        break

    result = gs.make_move(coord)
    print(f"You fired at ({col+1},{row+1}): {result}\n")

    if gs.game_over:
        break
    
    # AI move
    ai_coord = ai_bot.get_next_move(gs.player_board)
    ai_result = gs.make_move(ai_coord)
    ai_bot.update_result(ai_coord, ai_result, gs.player_board)
    
    print(f"AI fired at ({ai_coord[1]+1},{ai_coord[0]+1}): {ai_result}\n")


if gs.winner == "player":
    print("Congratulations, you won!")
elif gs.winner == "ai":
    print("The AI won. Better luck next time!")
else:
    print("Game ended early.")

print("\nFinal Player Board:")
display_board(gs.player_board, reveal_ships=True)

print("Final Opponent Board:")
display_board(gs.ai_board, reveal_ships=True)  # reveal so you can see AI ships at the end