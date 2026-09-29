import random
import math
from matplotlib import scale

#measured in minutes away from deadline
skewShape = -3            # skew factor
middleMinutes = 3.2       # curve location
widthMinutes = 17.4       # curve scale
earliestMinutes = -36.0   # 2.5 bound
latestMinutes = 8.2       # 97.5 bound

location = middleMinutes * 60
scale = widthMinutes * 60
earliest = earliestMinutes * 60
latest = latestMinutes * 60
window = latest - earliest     
deadline = -earliest  

floorPeople = {1: 100, 2: 120, 3: 60, 4: 120, 5: 80, 6: 20}

def makeArrivals():
    delta = skewShape / math.sqrt(1 + skewShape ** 2)
    arrivals = []
    for floor in floorPeople:
        for i in range(floorPeople[floor]):
            while True:
                first = random.gauss(0, 1)
                second = random.gauss(0, 1)
                tilted = delta * abs(first) + math.sqrt(1 - delta ** 2) * second

                time = location + scale * tilted
                if earliest <= time <= latest:
                    break
            arrivals.append((time - earliest, floor))

    arrivals.sort()
    return arrivals