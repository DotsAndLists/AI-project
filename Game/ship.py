class Ship:

    def __init__(self, name, coord):
        self.coord = coord
        self.name = name  
        self.hits = set()  
    def register_hit(self, coord):
        self.hits.add(coord) 

    def is_sunk(self):
        return len(self.hits) == len(self.coord)
        
# ship1 = Ship("destroyer", [(1,1), (1,2), (1,3)])
# print(ship1.coord)
# print(ship1.name)