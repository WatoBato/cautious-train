import random


empDist = {
    "1": 100,
    "2": 120,
    "3": 60,
    "4": 120,
    "5": 80,
    "6": 20
}

chanceDist = [0.2, 0.24, 0.12, 0.24, 0.16, 0.04]
totalTimes = []


def main():
    for _ in range(1000):
        elevatorTimes = []
        for _ in range(50):
                elevList = []
                for _ in range(10):
                    floor = random.choices(list(empDist.keys()), weights=chanceDist, k=1)[0]
                    empDist[floor] -= 1
                    elevList.append(floor)
        
                destinations = sorted({int(floor) for floor in elevList})
                travelTime = 0
                currentFloor = 0
                for destination in destinations:
                    travelTime += (destination - currentFloor) * 5
                    currentFloor = destination
                travelTime += currentFloor * 5
        
                stopTime = len(set(elevList)) * 10
                elevatorTime = 15 + travelTime + stopTime
                elevatorTimes.append(elevatorTime)

        totalTimes.append(sum(elevatorTimes) / len(elevatorTimes))

    print(sum(totalTimes) / len(totalTimes))

if __name__ == "__main__":
    main()

