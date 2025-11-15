#But the Board must track:
#   which coordinates contain ships
#   which coordinates were hit
#   which coordinates were missed
#   This is the minimum needed for the board to function.
# .ships is an attribute not a function, so it only calls a list, it does not call a method
# note - board1.place_ship(ship1) really means Board.place_ship(board1, ship1), so self refers to the board you call it on
# - for (r,c) probably goes through list of coord just 1 by 1 in the list, not like parsing thru a matrix like (0,0), (0,1) ...



class Board:

    def __init__(self, size):
        self.size = size
        self.ships = []                 
        self.grid = {}                  #grid is a dictionary where it has keys (coordinates) and values of ship, alr hit, and miss
        self.shots_taken = set() # - is a set because there can be no duplicates, and it is a registry of shots taken. once a shot taken it cant be shot again   
        
    def add_ship(self, ship):
        for (r,c) in ship.coord: #checking to see if it is in bounds or not, self refers to board here
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            
        #checking if ship is already in spot, so no overlapping can happen
        for (r,c) in ship.coord:
            if self.grid.get((r,c)) == "ship":
                return False

        self.ships.append(ship)
        for (r,c) in ship.coord: #actually puts the ship in ts
            self.grid[(r,c)] = "ship"

        return True

    def receive_shot(self, coord):      #returns either: repeat, hit, or miss, or sunk. Note that hit returns as just hit, but in grid its already_hit so people know from now on its been hit
        (r,c) = coord #defines r and c for this method from input coord

        # prevent duplicate shots
        if coord in self.shots_taken:
            return "repeat"

        self.shots_taken.add(coord)

        # check if there is a ship here
        if self.grid.get(coord) == "ship":
            # find which ship
            for ship in self.ships:     #looks at every ship in ship list []
                if coord in ship.coord:     #finds whcih ship is at this coordinate (r,c)
                    ship.register_hit(coord)    #for THIS ship, it registers the hit from the ship class
                    self.grid[coord] = "already_hit"    #now this coord in the grid dictionary goes from "ship" to "already_hit"

                    if ship.is_sunk():      #if ship was at its last life, and now is hit, it registers as sunk from now on
                        return f"sunk {ship.name}"      #returns sunk with the exact name of the ship, thanks to the f before ""
                    else:
                        return "hit"

        # otherwise it is a miss
        self.grid[coord] = "miss"       #not in grid yet means it missed, dont need else cuz it will go thru if first and return if not a miss
        return "miss"


#tester
