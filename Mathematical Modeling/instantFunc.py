import random

floorPeople = {1: 100, 2: 120, 3: 60, 4: 120, 5: 80, 6: 20}


def makeArrivals():
    arrivals = []
    for floor in floorPeople:
        for i in range(floorPeople[floor]):
            arrivals.append((0.0, floor))
            
    random.shuffle(arrivals)
    return arrivals