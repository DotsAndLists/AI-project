#   Gamestate function
#   decide whose turn it is
#   decide the winner
#   manage players
#   run the match
# need function for switching turns, winning, scoring, going turn, 

from Game.board import Board
from Game.ship import Ship

class GameState:
    
    def __init__(self, size):
        self.size = size
        self.player_board = Board(size)
        self.ai_board = Board(size)

        self.current_turn = "player"        #starting player, person is starting
        self.game_over = False              #game is ongoing
        self.winner = None

        self.player_moves = []              #these 2 lines track the move list, important for later
        self.ai_moves = []

    def make_move(self, coord):
        if self.game_over:                  #stops if game over
            return "Game is finished"

        if self.current_turn == "player":
            result = self.ai_board.receive_shot(coord)              #this puts the shot type in result AND updates the board grid dictionary
            self.record_move("player", coord, result)
        else:
            result = self.player_board.receive_shot(coord)          
            self.record_move("ai", coord, result)

        self.check_for_winner()

        if not self.game_over:
            self.switch_turn()                                  #switches turn if game not over, keeps game running

        return result

    def switch_turn(self):
        if self.current_turn == "player":    #simply swaps who is going
            self.current_turn = "ai"
        else:
            self.current_turn = "player"

    
    def record_move(self, current_player, coord, result):        #current player = "player" or "ai"

        move = {                            #dictionary with key of string getting you the variable 
            "player": current_player,
            "coord": coord,
            "result": result
        }

        if current_player == "player":                  #if the current player is the person (player) then it adds the move to the dictionary
            self.player_moves.append(move)              #otherwise, it adds it to the ai dictionary
        else:
            self.ai_moves.append(move)

    def check_for_winner(self):
        if self.ai_board.all_ships_sunk():
            self.game_over = True
            self.winner = "player"

        if self.player_board.all_ships_sunk():
            self.game_over = True
            self.winner = "ai"

    
