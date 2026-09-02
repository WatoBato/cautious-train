def fillElevator(lobby, capacity):
    if len(lobby) == 0:
        return []

    targetFloor = lobby[0].destFloor
    picked = []
    stillWaiting = []

    for person in lobby:
        if person.destFloor == targetFloor and len(picked) < capacity:
            picked.append(person)
        else:
            stillWaiting.append(person)

    while len(stillWaiting) > 0 and len(picked) < capacity:
        picked.append(stillWaiting.pop(0))

    #lobby list override
    lobby[:] = stillWaiting
    return picked
