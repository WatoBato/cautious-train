def fillElevator(lobby, capacity):
    picked = []
    while len(lobby) > 0 and len(picked) < capacity:
        picked.append(lobby.pop(0))
    return picked
