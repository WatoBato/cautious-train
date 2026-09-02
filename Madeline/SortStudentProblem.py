def permutations(mnList):
    def generate(start):
        if start == len(mnList) - 1:
            yield tuple(mnList)
            return
        for i in range(start, len(mnList)):
            mnList[start], mnList[i] = mnList[i], mnList[start]
            yield from generate(start + 1)
            mnList[start], mnList[i] = mnList[i], mnList[start]

    yield from generate(0)


def main():
    students = [1, 1, 3, 3, 5, 5, 4, 4, 4]
    students.sort()
    minDistances = []
    topScore = 0
    winningList = []

    for ordering in permutations(students):
        print(ordering)

        minDistances = []
        score = 0
        
        for value in sorted(set(ordering)):
            positions = [idx for idx, item in enumerate(ordering) if item == value]
            minDist = None
            for i in range(1, len(positions)):
                dist = positions[i] - positions[i - 1]
                if minDist is None or dist < minDist:
                    minDist = dist
            minDistances.append(minDist)

        score = 100 * (sum(minDistances) - len(set(ordering))) / (len(ordering) * len(set(ordering)))
        score = round(score, 1)
        if score > topScore:
            topScore = score
            winningList = ordering


        print(score)

    print("Top Score:", topScore)
    print("Winning List:", winningList)


if __name__ == "__main__":
    main()
