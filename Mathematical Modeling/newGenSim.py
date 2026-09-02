# morning rush elevator sim

import math
import random
import matplotlib.pyplot as plt

from randomFunc import fillElevator #from other files, choose fill method
# from instantFunc import makeArrivals
# from bankingFunc import fillElevator
# from groupingFunc import fillElevator
from skewFunc import makeArrivals

#measured in minutes away from deadline
skewShape = -3            # skew factor
middleMinutes = 3.2       # curve location
widthMinutes = 17.4       # curve scale
earliestMinutes = -36.0   # 2.5 bound
latestMinutes = 8.2       # 97.5 bound

# the sim clock starts at 0, and 0 is the moment the earliest person walks in.
# everything below is in seconds so the rest of the sim does not have to change.
location = middleMinutes * 60
scale = widthMinutes * 60
earliest = earliestMinutes * 60
latest = latestMinutes * 60
window = latest - earliest     
deadline = -earliest  


# problem parameters
stepSeconds = 5           # sim step second for optimization
secondsPerFloor = 5
stopTime = 10
reopenTime = 8
reopenChance = 0.07       # 7 out of 100 upstairs stops the doors reopen
loadTime = 15
carSize = 10
carCount = 4
simMinutes = 100
floorPeople = {1: 100, 2: 120, 3: 60, 4: 120, 5: 80, 6: 20}


class Person:
    def __init__(self, destFloor, arriveTime):
        self.destFloor = destFloor
        self.arriveTime = arriveTime
        self.boardTime = None
        self.dropTime = None

class Elevator:
    def __init__(self, name):
        self.name = name
        self.floor = 0
        self.passengers = []
        self.stopsLeft = []
        self.status = "loading"
        self.timer = 0
        self.tripStart = 0
        self.trips = []
        self.delivered = 0
        self.stopCounts = []
        self.topFloors = []

    def step(self, now, lobby):
        if self.status == "loading":
            self.doLoading(now, lobby)
        elif self.status == "moving":
            self.doMoving()
        elif self.status == "stopped":
            self.doStopped(now)
        elif self.status == "returning":
            self.doReturning(now)

    def doLoading(self, now, lobby):
        if len(self.passengers) == 0:
            picked = fillElevator(lobby, carSize)
            if len(picked) == 0:
                return
            for person in picked:
                person.boardTime = now
                self.passengers.append(person)
            self.tripStart = now
            self.timer = loadTime
            return

        self.timer -= stepSeconds
        if self.timer <= 0:
            stops = []
            for person in self.passengers:
                if person.destFloor not in stops:
                    stops.append(person.destFloor)
            stops.sort()
            self.stopsLeft = stops
            # remember the two numbers the write up cares about
            self.stopCounts.append(len(stops))
            self.topFloors.append(stops[-1])
            self.status = "moving"
            self.timer = secondsPerFloor

    def doMoving(self):
        self.timer -= stepSeconds
        if self.timer > 0:
            return
        self.floor += 1
        if self.floor in self.stopsLeft:
            self.status = "stopped"
            self.timer = stopTime
            # 7 percent of upstairs stops the doors have to open a second time
            if random.random() < reopenChance:
                self.timer += reopenTime
        else:
            self.timer = secondsPerFloor

    def doStopped(self, now):
        self.timer -= stepSeconds
        if self.timer > 0:
            return

        stillRiding = []
        for person in self.passengers:
            if person.destFloor == self.floor:
                person.dropTime = now
                self.delivered += 1
            else:
                stillRiding.append(person)
        self.passengers = stillRiding
        self.stopsLeft.remove(self.floor)

        if len(self.stopsLeft) > 0:
            self.status = "moving"
        else:
            self.status = "returning"
        self.timer = secondsPerFloor

    def doReturning(self, now):
        self.timer -= stepSeconds
        if self.timer > 0:
            return
        self.floor -= 1
        if self.floor <= 0:
            self.floor = 0
            self.status = "loading"
            self.timer = 0
            self.trips.append(now - self.tripStart)
        else:
            self.timer = secondsPerFloor


def runSimulation():
    arrivals = makeArrivals()
    nextPerson = 0
    lobby = []
    everyone = []
    history = []

    elevators = []
    for i in range(carCount):
        elevators.append(Elevator("Elevator " + str(i + 1)))

    now = 0
    while now < simMinutes * 60:
        while nextPerson < len(arrivals) and arrivals[nextPerson][0] <= now:
            floor = arrivals[nextPerson][1]
            person = Person(floor, now)
            lobby.append(person)
            everyone.append(person)
            nextPerson += 1

        for elevator in elevators:
            elevator.step(now, lobby)

        history.append((now / 60, len(lobby)))
        now += stepSeconds

    return everyone, elevators, history


def showResults(everyone, elevators, history):
    delivered = 0
    stuck = 0
    late = 0
    lateAlready = 0
    for person in everyone:
        if person.dropTime is None:
            stuck += 1
        else:
            delivered += 1
            if person.dropTime > deadline:
                late += 1
                #count people who were already late (only necessary with normal skew)
                if person.arriveTime > deadline:
                    lateAlready += 1

    print("People delivered:", delivered)
    print("People stuck:", stuck)
    print()
    print("Late to their desk:", late)
    print("  of those, after 9:00 arrival:", lateAlready)
    print("  elevs made", late - lateAlready, "late arrivals")
    print()

    allTrips = []
    allStops = []
    allTops = []
    for elevator in elevators:
        allTrips.extend(elevator.trips)
        allStops.extend(elevator.stopCounts[:len(elevator.trips)])
        allTops.extend(elevator.topFloors[:len(elevator.trips)])
        if len(elevator.trips) > 0:
            average = sum(elevator.trips) / len(elevator.trips)
            print(elevator.name, "average round trip:", round(average, 1), "s")
        else:
            print(elevator.name, "somehow this failed? something never finished a trip")

    if len(allTrips) > 0:
        print()
        print("avg rt:", round(sum(allTrips) / len(allTrips), 1), "s")
        print("E|D|:", round(sum(allStops) / len(allStops), 3))
        print("E|M|:", round(sum(allTops) / len(allTops), 3))

    minutes = []
    waiting = []
    for point in history:
        minutes.append(point[0])
        waiting.append(point[1])

    arrivalMinutes = []
    for person in everyone:
        arrivalMinutes.append(person.arriveTime / 60)

#graphs to confirm distribution and lobby dist to do a quick "realism sim check"
    plt.subplot(2, 1, 1)
    plt.hist(arrivalMinutes, bins=30)
    # dotted line w/ last time people are allowed to arrive by sim
    plt.axvline(window / 60, linestyle="--")
    # 9am line
    plt.axvline(deadline / 60, linestyle=":")
    plt.xlabel("minutes")
    plt.ylabel("people")
    plt.title("lobby arrivals")

    plt.subplot(2, 1, 2)
    plt.plot(minutes, waiting)
    plt.axvline(window / 60, linestyle="--")
    plt.axvline(deadline / 60, linestyle=":")
    plt.xlabel("min since arrival")
    plt.ylabel("waits in lobby")
    plt.title("lobby line over time")

    plt.tight_layout()
    plt.show()

everyone, elevators, history = runSimulation()
showResults(everyone, elevators, history)