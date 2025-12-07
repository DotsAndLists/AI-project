import pygame
import sys
import time

# --- IMPORT YOUR MODULES ---
from Game.gamestate import GameState
from Game.ship import Ship  # Needed to create ships manually
from ai.search import SearchAI
from ai.heuristics import get_probability_grid

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
# New Colors for placement
COLOR_VALID = (0, 255, 0)   # Green for good placement
COLOR_INVALID = (255, 0, 0) # Red for bad placement

# Initialize Pygame
pygame.init()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Battleship: Human vs AI")
FONT = pygame.font.SysFont('arial', 20)
BIG_FONT = pygame.font.SysFont('arial', 36)

def draw_board(surface, board, offset_x, offset_y, title, reveal_ships=False, show_heatmap=False, heatmap_grid=None):
    # Draw Title
    title_surf = BIG_FONT.render(title, True, TEXT_COLOR)
    surface.blit(title_surf, (offset_x, offset_y - 50))

    # 1. Draw the Base Grid (Water, Misses, Hits)
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
            
            # Draw X for hits
            if cell_status == "already_hit":
                pygame.draw.line(surface, (0,0,0), (x+5, y+5), (x+TILE_SIZE-5, y+TILE_SIZE-5), 3)
                pygame.draw.line(surface, (0,0,0), (x+TILE_SIZE-5, y+5), (x+5, y+TILE_SIZE-5), 3)

    # 2. OVERLAY: Check for Sunk Ships and color them GREEN
    # We iterate over the ship objects directly
    for ship in board.ships:
        if ship.is_sunk():
            for (r, c) in ship.coord:
                x = offset_x + (TILE_SIZE + MARGIN) * c
                y = offset_y + (TILE_SIZE + MARGIN) * r
                
                # Draw Green Tile
                pygame.draw.rect(surface, (50, 205, 50), (x, y, TILE_SIZE, TILE_SIZE)) # Lime Green
                
                # Optional: Draw a checkmark or different border to indicate "Done"
                pygame.draw.rect(surface, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 2)

def get_grid_coords(mouse_pos, offset_x, offset_y, size):
    """ Converts pixel to grid coordinates """
    mx, my = mouse_pos
    board_px_size = size * (TILE_SIZE + MARGIN)
    
    if offset_x <= mx <= offset_x + board_px_size and \
       offset_y <= my <= offset_y + board_px_size:
        
        col = (mx - offset_x) // (TILE_SIZE + MARGIN)
        row = (my - offset_y) // (TILE_SIZE + MARGIN)
        return row, col
    return None

def main():
    clock = pygame.time.Clock()
    running = True
    
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    SUCCESS_GREEN = (50, 255, 50)
    DANGER_RED = (255, 50, 50)

    # --- SETUP ---
    BOARD_SIZE = 10
    fleets = [
        ("Carrier", 5), ("Battleship", 4), ("Cruiser", 3),
        ("Submarine", 3), ("Destroyer", 2)
    ]

    gs = GameState(BOARD_SIZE)
    ai_bot = SearchAI(gs.size)
    gs.ai_board.place_ships_randomly(fleets)

    ships_to_place = list(fleets) 
    placement_orientation = "H" 

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
                    # --- PLACEMENT ---
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

                            new_ship = Ship(ship_name, new_coords)
                            if gs.player_board.add_ship(new_ship):
                                ships_to_place.pop(0)
                                if not ships_to_place:
                                    game_message = "Combat Started! Click Enemy Waters."
                                    message_color = GOLD
                            else:
                                game_message = "Invalid placement! Try again."
                                message_color = WHITE

                    # --- COMBAT ---
                    elif not gs.game_over and gs.current_turn == "player":
                        coords = get_grid_coords(mouse_pos, AI_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)
                        if coords:
                            r, c = coords
                            if (r,c) not in gs.ai_board.shots_taken:
                                result = gs.make_move((r, c))
                                
                                # CHECK SUNK LOGIC
                                if "sunk" in result:
                                    ship_name = result.replace("sunk ", "")
                                    game_message = f"BOOM! You sunk the Enemy {ship_name}!"
                                    message_color = SUCCESS_GREEN
                                    
                                    # --- FORCE DRAW AND WAIT ---
                                    # We redraw everything manually right here so the user sees the 
                                    # Green ship and the message BEFORE the AI thinks.
                                    SCREEN.fill(BG_COLOR)
                                    msg_surf = BIG_FONT.render(game_message, True, message_color)
                                    msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
                                    SCREEN.blit(msg_surf, msg_rect)
                                    draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", reveal_ships=True)
                                    # Reveal enemy temporarily so we can see the green sunk ship
                                    draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=False) 
                                    pygame.display.flip()
                                    
                                    # PAUSE FOR 2 SECONDS
                                    pygame.time.wait(2000)
                                    
                                else:
                                    game_message = f"You fired at ({r},{c}): {result.upper()}"
                                    message_color = GOLD
                                
                                if gs.game_over:
                                    game_message = f"VICTORY! You destroyed the enemy fleet!"
                                    message_color = SUCCESS_GREEN
                            else:
                                game_message = "You already shot there!"
                                message_color = WHITE

                if event.button == 3 and ships_to_place:
                    placement_orientation = "V" if placement_orientation == "H" else "H"

        # 2. AI Turn
        if not ships_to_place and gs.current_turn == "ai" and not gs.game_over:
            pygame.display.flip() 
            pygame.time.wait(600) 
            
            ai_move = ai_bot.get_next_move(gs.player_board)
            ai_result = gs.make_move(ai_move)
            ai_bot.update_result(ai_move, ai_result, gs.player_board)
            
            if "sunk" in ai_result:
                ship_name = ai_result.replace("sunk ", "")
                game_message = f"ALERT! AI sunk your {ship_name}!"
                message_color = DANGER_RED
                
                # Pause again so we see the damage
                SCREEN.fill(BG_COLOR)
                msg_surf = BIG_FONT.render(game_message, True, message_color)
                msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
                SCREEN.blit(msg_surf, msg_rect)
                draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", reveal_ships=True)
                draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=False)
                pygame.display.flip()
                pygame.time.wait(2000)

            else:
                game_message = f"AI fired at ({ai_move[0]},{ai_move[1]}): {ai_result.upper()}"
                message_color = GOLD

            if gs.game_over:
                game_message = f"DEFEAT! The AI won."
                message_color = DANGER_RED

        # 3. Drawing
        SCREEN.fill(BG_COLOR)
        
        msg_surf = BIG_FONT.render(game_message, True, message_color)
        msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
        SCREEN.blit(msg_surf, msg_rect)

        draw_board(SCREEN, gs.player_board, PLAYER_OFFSET_X, BOARD_OFFSET_Y, "Your Fleet", reveal_ships=True)
        reveal_enemy = True if gs.game_over else False
        draw_board(SCREEN, gs.ai_board, AI_OFFSET_X, BOARD_OFFSET_Y, "Enemy Waters", reveal_ships=reveal_enemy)

        # GHOST SHIP
        if ships_to_place:
            ship_name, ship_size = ships_to_place[0]
            coords = get_grid_coords(mouse_pos, PLAYER_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)
            if coords:
                r, c = coords
                valid_hover = True
                ghost_coords = []
                for i in range(ship_size):
                    if placement_orientation == "H": nr, nc = r, c+i
                    else: nr, nc = r+i, c
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        ghost_coords.append((nr, nc))
                        if gs.player_board.grid.get((nr, nc)) == "ship": valid_hover = False
                    else: valid_hover = False
                if len(ghost_coords) != ship_size: valid_hover = False

                hover_color = (0, 255, 0) if valid_hover else (255, 0, 0)
                for (gr, gc) in ghost_coords:
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
    # Define WHITE if not defined globally
    WHITE = (255, 255, 255)
    main()