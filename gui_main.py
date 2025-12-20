import pygame
import sys
import time

# --- IMPORT YOUR MODULES ---
from Game.gamestate import GameState
from Game.ship import Ship
from ai.search import SearchAI
from ai.heuristics import get_probability_grid
from ai.learning import RLBrain  # <--- NEW IMPORT

#HOW TO RUN: arjundeshpande@MacBookPro AI-project % python3 -m venv venv
#arjundeshpande@MacBookPro AI-project % source venv/bin/activate
#You must use the above commands to activate the virtual environment
#Then install pygame ce : pip install pygame-ce

# --- CONFIGURATION ---
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 600
TILE_SIZE = 40
MARGIN = 2
HEADER_HEIGHT = 80

# --- COLORS ---
BG_COLOR = (40, 44, 52)
TEXT_COLOR = (255, 255, 255)
COLOR_WATER = (30, 144, 255)
COLOR_SHIP = (105, 105, 105)
COLOR_MISS = (200, 200, 255)
COLOR_HIT = (220, 20, 60)
COLOR_VALID = (0, 255, 0)
COLOR_INVALID = (255, 0, 0)

# Initialize Pygame
pygame.init()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Battleship: Human vs AI")
FONT = pygame.font.SysFont('arial', 20)
BIG_FONT = pygame.font.SysFont('arial', 36)

# --- HELPER FUNCTIONS ---

def get_grid_coords(mouse_pos, offset_x, offset_y, size):
    mx, my = mouse_pos
    board_px_size = size * (TILE_SIZE + MARGIN)
    
    if offset_x <= mx <= offset_x + board_px_size and \
       offset_y <= my <= offset_y + board_px_size:
        
        col = (mx - offset_x) // (TILE_SIZE + MARGIN)
        row = (my - offset_y) // (TILE_SIZE + MARGIN)
        return row, col
    return None

def check_valid_placement(board, coords):
    """
    Checks if the ship placement is valid.
    1. Must be within bounds.
    2. Must not overlap existing ships.
    3. Must not touch existing ships (including diagonals).
    """
    for (r, c) in coords:
        # 1. Check Bounds
        if not (0 <= r < board.size and 0 <= c < board.size):
            return False
            
        # 2. Check overlap & Neighbors (3x3 area)
        # We check r-1 to r+1 and c-1 to c+1
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                
                # Ensure neighbor is on board
                if 0 <= nr < board.size and 0 <= nc < board.size:
                    # If ANY neighbor (or the cell itself) is a ship, it's invalid
                    if board.grid.get((nr, nc)) == "ship":
                        return False
    return True

def draw_board(surface, board, offset_x, offset_y, title, reveal_ships=False, show_heatmap=False, heatmap_grid=None):
    # Draw Title
    title_surf = BIG_FONT.render(title, True, TEXT_COLOR)
    surface.blit(title_surf, (offset_x, offset_y - 50))

    # 1. Draw Grid
    for r in range(board.size):
        for c in range(board.size):
            x = offset_x + (TILE_SIZE + MARGIN) * c
            y = offset_y + (TILE_SIZE + MARGIN) * r
            
            color = COLOR_WATER
            cell_status = board.grid.get((r, c))

            if cell_status == "ship":
                color = COLOR_SHIP if reveal_ships else COLOR_WATER
            elif cell_status == "already_hit":
                color = COLOR_HIT
            elif cell_status == "miss":
                color = COLOR_MISS

            # Heatmap Overlay
            if show_heatmap and heatmap_grid and cell_status not in ["already_hit", "miss"]:
                score = heatmap_grid[r][c]
                intensity = min(255, score * 15)
                if intensity > 0:
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    s.set_alpha(150)
                    s.fill((intensity, 0, 0))
                    pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
                    surface.blit(s, (x, y))
                    continue

            pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
            
            if cell_status == "already_hit":
                pygame.draw.line(surface, (0,0,0), (x+5, y+5), (x+TILE_SIZE-5, y+TILE_SIZE-5), 3)
                pygame.draw.line(surface, (0,0,0), (x+TILE_SIZE-5, y+5), (x+5, y+TILE_SIZE-5), 3)

    # 2. OVERLAY: Green Sunk Ships
    for ship in board.ships:
        if ship.is_sunk():
            for (r, c) in ship.coord:
                x = offset_x + (TILE_SIZE + MARGIN) * c
                y = offset_y + (TILE_SIZE + MARGIN) * r
                pygame.draw.rect(surface, (50, 205, 50), (x, y, TILE_SIZE, TILE_SIZE)) # Green
                pygame.draw.rect(surface, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 2) # Border

# --- MAIN LOOP ---

def main():
    clock = pygame.time.Clock()
    running = True
    
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    SUCCESS_GREEN = (50, 255, 50)
    DANGER_RED = (255, 50, 50)

    # Config
    BOARD_SIZE = 10
    fleets = [
        ("Carrier", 5), ("Battleship", 4), ("Cruiser", 3),
        ("Submarine", 3), ("Destroyer", 2)
    ]
    
    gs = GameState(BOARD_SIZE)
    ai_bot = SearchAI(gs.size)
    rl_brain = RLBrain(gs.size)  # <--- NEW: Initialize Learning Brain
    gs.ai_board.place_ships_randomly(fleets)

    ships_to_place = list(fleets) 
    placement_orientation = "H" 

    # UI Positioning
    PLAYER_OFFSET_X = 50
    AI_OFFSET_X = 600
    BOARD_OFFSET_Y = 120

    game_message = "Welcome! Place your ships."
    message_color = GOLD 
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if ships_to_place and event.key == pygame.K_r:
                    placement_orientation = "V" if placement_orientation == "H" else "H"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # --- PLACEMENT PHASE ---
                    if ships_to_place:
                        coords = get_grid_coords(mouse_pos, PLAYER_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)
                        if coords:
                            r, c = coords
                            ship_name, ship_size = ships_to_place[0]
                            
                            new_coords = []
                            if placement_orientation == "H":
                                new_coords = [(r, c+i) for i in range(ship_size)]
                            else:
                                new_coords = [(r+i, c) for i in range(ship_size)]

                            # --- CHECK VALIDITY (Includes Neighbors) ---
                            if check_valid_placement(gs.player_board, new_coords):
                                new_ship = Ship(ship_name, new_coords)
                                gs.player_board.add_ship(new_ship)
                                ships_to_place.pop(0)
                                if not ships_to_place:
                                    game_message = "Combat Started! Click Enemy Waters."
                                    message_color = GOLD
                            else:
                                game_message = "Invalid Placement!"
                                message_color = DANGER_RED

                    # --- COMBAT PHASE ---
                    elif not gs.game_over and gs.current_turn == "player":
                        coords = get_grid_coords(mouse_pos, AI_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)
                        if coords:
                            r, c = coords
                            if (r,c) not in gs.ai_board.shots_taken:
                                result = gs.make_move((r, c))
                                
                                if "sunk" in result:
                                    ship_name = result.replace("sunk ", "")
                                    game_message = f"BOOM! You sunk the Enemy {ship_name}!"
                                    message_color = SUCCESS_GREEN
                                    
                                    # Force Draw & Pause
                                    SCREEN.fill(BG_COLOR)
                                    msg_surf = BIG_FONT.render(game_message, True, message_color)
                                    msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
                                    SCREEN.blit(msg_surf, msg_rect)
                                    draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", reveal_ships=True, show_heatmap=False)
                                    draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=False) 
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                                else:
                                    game_message = f"You fired at ({r},{c}): {result.upper()}"
                                    message_color = GOLD
                                
                                if gs.game_over:
                                    # 1. SHOW LEARNING MESSAGE
                                    SCREEN.fill(BG_COLOR)
                                    learn_msg = BIG_FONT.render("Match Finished. Updating AI Memory...", True, GOLD)
                                    msg_rect = learn_msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                    SCREEN.blit(learn_msg, msg_rect)
                                    pygame.display.flip()
                                    pygame.time.wait(1000) # Pause so user sees it

                                    # 2. PERFORM LEARNING
                                    rl_brain.learn_from_game(gs.player_board)

                                    # 3. SET FINAL VICTORY MESSAGE
                                    game_message = f"VICTORY! Enemy fleet destroyed. (AI Learned)"
                                    message_color = SUCCESS_GREEN

                            else:
                                game_message = "You already shot there!"
                                message_color = WHITE

                if event.button == 3 and ships_to_place:
                    placement_orientation = "V" if placement_orientation == "H" else "H"

        # --- AI TURN ---
        if not ships_to_place and gs.current_turn == "ai" and not gs.game_over:
            pygame.display.flip() 
            pygame.time.wait(600) 
            
            # --- NEW: PASS rl_brain TO AI ---
            ai_move = ai_bot.get_next_move(gs.player_board, rl_brain)
            ai_result = gs.make_move(ai_move)
            ai_bot.update_result(ai_move, ai_result, gs.player_board)
            
            if "sunk" in ai_result:
                ship_name = ai_result.replace("sunk ", "")
                game_message = f"ALERT! AI sunk your {ship_name}!"
                message_color = DANGER_RED
                
                SCREEN.fill(BG_COLOR)
                msg_surf = BIG_FONT.render(game_message, True, message_color)
                msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
                SCREEN.blit(msg_surf, msg_rect)
                draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", reveal_ships=True, show_heatmap=False)
                draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=False)
                pygame.display.flip()
                pygame.time.wait(2000)

            else:
                game_message = f"AI fired at ({ai_move[0]},{ai_move[1]}): {ai_result.upper()}"
                message_color = GOLD

            if gs.game_over:
                # 1. SHOW LEARNING MESSAGE
                SCREEN.fill(BG_COLOR)
                learn_msg = BIG_FONT.render("Match Finished. Updating AI Memory...", True, GOLD)
                msg_rect = learn_msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                SCREEN.blit(learn_msg, msg_rect)
                pygame.display.flip()
                pygame.time.wait(1000) # Pause so user sees it

                # 2. PERFORM LEARNING
                rl_brain.learn_from_game(gs.player_board)

                # 3. SET FINAL DEFEAT MESSAGE
                game_message = f"DEFEAT! The AI won. (AI Learned)"
                message_color = DANGER_RED

        # --- DRAWING ---
        SCREEN.fill(BG_COLOR)
        
        msg_surf = BIG_FONT.render(game_message, True, message_color)
        msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
        SCREEN.blit(msg_surf, msg_rect)

        # Draw Player Board (Heatmap DISABLED here)
        draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", 
                   reveal_ships=True, show_heatmap=False)

        # Draw Enemy Board
        reveal_enemy = True if gs.game_over else False
        draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=reveal_enemy)

        # GHOST SHIP OVERLAY
        if ships_to_place:
            ship_name, ship_size = ships_to_place[0]
            coords = get_grid_coords(mouse_pos, PLAYER_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)
            
            if coords:
                r, c = coords
                # Generate ghost coords
                ghost_coords = []
                for i in range(ship_size):
                    if placement_orientation == "H": nr, nc = r, c+i
                    else: nr, nc = r+i, c
                    ghost_coords.append((nr, nc))

                # CHECK VALIDITY (Includes Neighbors)
                is_valid = check_valid_placement(gs.player_board, ghost_coords)

                # Color logic
                hover_color = COLOR_VALID if is_valid else COLOR_INVALID
                
                # Draw Ghost
                for (gr, gc) in ghost_coords:
                    # Only draw if on screen (check_valid_placement handles logical bounds, but we need visual bounds)
                    if 0 <= gr < BOARD_SIZE and 0 <= gc < BOARD_SIZE:
                        x = PLAYER_OFFSET_X + (TILE_SIZE + MARGIN) * gc
                        y = BOARD_OFFSET_Y + (TILE_SIZE + MARGIN) * gr
                        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                        s.set_alpha(128)
                        s.fill(hover_color)
                        SCREEN.blit(s, (x, y))
                        pygame.draw.rect(SCREEN, (255,255,255), (x, y, TILE_SIZE, TILE_SIZE), 1)

            instr_text = FONT.render(f"Placing: {ship_name} ({ship_size}) - Press 'R' to Rotate", True, WHITE)
            SCREEN.blit(instr_text, (PLAYER_OFFSET_X, BOARD_OFFSET_Y + (BOARD_SIZE * 45)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()