from Game.gamestate import GameState
from ai.search import SearchAI
from ai.random_bot import RandomAI 

def run_batch(bot_type, num_games=1000):
    total_moves = 0
    BOARD_SIZE = 10  # <--- Change to 5 or 10 here
    
    # Define the fleet based on the board size (Must match main.py logic)
    if BOARD_SIZE == 5:
        fleets = [("Submarine", 3), ("Destroyer", 2)]
    else:
        fleets = [("Carrier", 5), ("Battleship", 4), ("Cruiser", 3), ("Submarine", 3), ("Destroyer", 2)]
    
    print(f"Running {num_games} games for {bot_type.__name__}...", end="", flush=True)
    
    for i in range(num_games):
        gs = GameState(BOARD_SIZE)
        
        # FIX: Now we pass 'fleets' to the function!
        gs.ai_board.place_ships_randomly(fleets)
        
        # Initialize the specific bot
        bot = bot_type(gs.size)
        
        moves_taken = 0
        while not gs.ai_board.all_ships_sunk():
            move = bot.get_next_move(gs.ai_board)
            result = gs.make_move_simulation(move)
            bot.update_result(move, result, gs.ai_board)
            moves_taken += 1
            
            # Safety break just in case
            if moves_taken > BOARD_SIZE**2 + 10: break
                
        total_moves += moves_taken
        
    print(" Done.")
    return total_moves / num_games

if __name__ == "__main__":
    print(f"--- BATTLESHIP AI SIMULATION ---")
    
    # Run Random Bot
    avg_random = run_batch(RandomAI, num_games=1000)
    
    # Run Smart Bot
    avg_smart = run_batch(SearchAI, num_games=1000)
    
    print(f"\n--- FINAL RESULTS (Lower is Better) ---")
    print(f"Random Bot Average: {avg_random:.2f} moves")
    print(f"Smart AI Average:   {avg_smart:.2f} moves")
    
    if avg_random > 0:
        improvement = ((avg_random - avg_smart) / avg_random) * 100
        print(f"\nYour AI is {improvement:.1f}% more efficient than random guessing!")