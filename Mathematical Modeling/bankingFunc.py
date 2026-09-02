lowFloors = [1, 2, 3]
highFloors = [4, 5, 6]


def fillElevator(lobby, capacity, carNumber=1):
    if carNumber <= 2:
        myFloors = lowFloors
    else:
        myFloors = highFloors

    picked = []
    stillWaiting = []

    for person in lobby:
        if person.destFloor in myFloors and len(picked) < capacity:
            picked.append(person)
        else:
            stillWaiting.append(person)

    #lobby list override
    lobby[:] = stillWaiting
    return picked