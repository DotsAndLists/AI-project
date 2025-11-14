class Ship:

    def __init__(self, coord):
        self.coord = coord

    def register_hit(self):
        self.hits +=1

    def is_sunk(self):
        return self.hits == len(self.coord)
        
ship1 = Ship([(1,1), (1,2), (1,3)])
print(ship1.coord)