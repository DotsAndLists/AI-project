from Game.board import Board
from Game.ship import Ship

#printing tester
def display(self):
    for r in range(self.size):
        row = []
        for c in range(self.size):
            cell = self.grid.get((r, c), ".")
            if cell == "ship":
                row.append("S")
            elif cell == "hit":
                row.append("H")
            elif cell == "miss":
                row.append("M")
            else:
                row.append(".")
        print(" ".join(row))

board1 = Board(10)

# Create ships
ship1 = Ship("Destroyer", [(0,0), (0,1)])
ship2 = Ship("Submarine", [(2,2), (3,2)])

# Place ships
print("Placing ship1:", board1.add_ship(ship1))  # True
print("Placing ship2:", board1.add_ship(ship2))  # True

# Fire shots
shots = [(0,0), (0,1), (4,4), (0,0), (2,2), (3,2)]
for shot in shots:
    result = board1.receive_shot(shot)
    print(f"Shot at {shot}: {result}")

# Print final board
print("\nFinal board state:")
