import copy

gold_amount = 0
wumpus_amount = 0


def input():
    fi = open('map1.txt')
    n = int(fi.readline())
    map = []
    for i in range(n):
        s = fi.readline()
        tmp = s.replace('\n', '')
        tmp = tmp.split('.')
        map.append(tmp)

    fi.close()
    return n, map


def hiddenKB(n, map):
    # Breeze, stench, wumpus, gold
    hidden = [[[False, False, False, False] for _ in range(n)] for _ in range(n)]
    global gold_amount, wumpus_amount
    agent_pos = None

    for i in range(n):
        for j in range(n):
            if 'B' in map[i][j]:
                hidden[i][j][0] = True
            if 'S' in map[i][j]:
                hidden[i][j][1] = True
            if 'W' in map[i][j]:
                hidden[i][j][2] = True
                wumpus_amount += 1
            if 'G' in map[i][j]:
                hidden[i][j][3] = True
                gold_amount += 1
            if 'A' in map[i][j]:
                agent_pos = (i, j)

    return hidden, agent_pos


def play(x, y, n, KB, hidden, explored):  # Remember explored is a PADDING !!!!
    gold, point, wumpus = 0, 0, 0
    start = (x, y)
    path = [start]
    printKB(n, KB, explored)

    while True:
        select = selectSafeCell(x, y, KB, explored)
        if select is not None:
            point -= 10
            x, y = select[0], select[1]
            path.append((x, y))
            explored[x + 1][y + 1] = True
            KB[x][y] = hidden[x][y]
            if KB[x][y][3]:
                print("Grab the gold at ", (n - x, y + 1))
                gold += 1
                point += 100
                KB[x][y][3] = False

                if gold == gold_amount and wumpus == wumpus_amount:
                    print("FINISH!")
                    return (path, point, gold)

            printKB(n, KB, explored)
            continue  # skip block of code below and go straight to the next loop

        # shoot the Wumpus
        elif KB[x][y][1]:  # Smell stench
            select = shouldShoot(x, y, n, KB, explored)
            if select is not None:
                point -= 100
                a, b = select[0], select[1]
                print("Shoot to ", (n - a, b + 1))

                if hidden[a][b][2]:  # Update hidden and KB, not so complete
                    wumpus += 1
                    if gold == gold_amount and wumpus == wumpus_amount:
                        print("FINISH!")
                        return path, point, gold

                    explored[a + 1][b + 1] = True
                    hidden[a][b][2] = False
                    if explored[a][b + 1] is not None:
                        hidden[a - 1][b][1], KB[a - 1][b][1] = False, False
                    if explored[a + 1][b + 2] is not None:
                        hidden[a][b + 1][1], KB[a][b + 1][1] = False, False
                    if explored[a + 2][b + 1] is not None:
                        hidden[a + 1][b][1], KB[a + 1][b][1] = False, False
                    if explored[a + 1][b] is not None:
                        hidden[a][b - 1][1], KB[a][b - 1][1] = False, False
                printKB(n, KB, explored)
                continue

        # Find the nearest safe cell that hasnt been explored
        adja = copy.deepcopy(explored)
        tmp = bfsNear((x, y), n, KB, adja, explored)  # (a,b), father

        if tmp == None:  # No unexplored safe cell left, climb out
            father = bfsOut((x, y), start, n, explored)
            subPath = findPath((x, y), start, father)
            point -= len(subPath) * 10
            path.extend(subPath)
            print("CLIMB OUT!")
            return (path, point + 10, gold)

        a, b = tmp[0][0], tmp[0][1]
        father = tmp[1]
        subPath = findPath((x, y), (a, b), father)
        point -= len(subPath) * 10
        path.extend(subPath)
        x, y = a, b
        printKB(n, KB, explored)


# Select 1/4 cell around current position which is safe
def selectSafeCell(x, y, KB, explored):
    if explored[x][y + 1] is False and safe(x - 1, y, KB, explored):
        return x - 1, y
    if explored[x + 1][y + 2] is False and safe(x, y + 1, KB, explored):
        return x, y + 1
    if explored[x + 2][y + 1] is False and safe(x + 1, y, KB, explored):
        return x + 1, y
    if explored[x + 1][y] is False and safe(x, y - 1, KB, explored):
        return x, y - 1

    return None


# If an unexplored cell is safe
def safe(x, y, KB, explored):  # Remember explored is a padding array => explored[x + 1][y + 1]
    # Safe if adjacent to a cell that has no signal
    null_adjacent = explored[x][y + 1] and signal(x - 1, y, KB) == 0 or \
                    explored[x + 1][y + 2] and signal(x, y + 1, KB) == 0 or \
                    explored[x + 2][y + 1] and signal(x + 1, y, KB) == 0 or \
                    explored[x + 1][y] and signal(x, y - 1, KB) == 0
    # safe if it's adjacent to 2 cell that each one has EXACTLY 1 signal and they are different, 4C2 = 6 cases UR, UD, UL, RD, RL, DL
    nonsense_signal = False
    if explored[x][y + 1] and signal(x - 1, y, KB) == 1:  # Up
        nonsense_signal = explored[x + 1][y + 2] and signal(x, y + 1, KB) == 1 and KB[x][y + 1] != KB[x - 1][y] or \
                          explored[x + 2][y + 1] and signal(x + 1, y, KB) == 1 and KB[x + 1][y] != KB[x - 1][y] or \
                          explored[x + 1][y] and signal(x, y - 1, KB) == 1 and KB[x][y - 1] != KB[x - 1][y]

    elif explored[x + 1][y + 2] and signal(x, y + 1, KB) == 1:  # Right
        nonsense_signal = explored[x + 2][y + 1] and signal(x + 1, y, KB) == 1 and KB[x + 1][y] != KB[x][y + 1] or \
                          explored[x + 1][y] and signal(x, y - 1, KB) == 1 and KB[x][y - 1] != KB[x][y + 1]

    elif explored[x + 2][y + 1] and signal(x + 1, y, KB) == 1:  # Down
        nonsense_signal = explored[x + 1][y] and signal(x, y - 1, KB) == 1 and KB[x][y - 1] != KB[x + 1][y]

    return null_adjacent or nonsense_signal


def output(path, gold, point):
    fo = open("result1.txt", "w")
    fo.write("Gold: " + str(gold) + "  Point: " + str(point) + "\n")
    fo.write("Path: " + str(path))
    fo.close()


def bfsOut(current, goal, n, adja):  # Adja is set of explored cells
    current = (current[0] + 1, current[1] + 1)  # New coordinate is based on adja padding
    goal = (goal[0] + 1, goal[1] + 1)
    frontier = [current]
    adja[current[0]][current[1]] = False
    father = [[None for j in range(n)] for i in range(n)]

    while frontier:  # Stop when frontier = []
        x, y = frontier[0][0], frontier[0][1]  # Cell[x][y]
        frontier.pop(0)

        if adja[x - 1][y]:  # F F F F adja is a False padding
            frontier.append((x - 1, y))  # F T T F but father is not!
            father[x - 2][y - 1] = (x - 1, y - 1)  # F F F F
            adja[x - 1][y] = False  # Da co trong frontier
        if adja[x][y + 1]:
            frontier.append((x, y + 1))
            father[x - 1][y] = (x - 1, y - 1)
            adja[x][y + 1] = False
        if adja[x + 1][y]:
            frontier.append((x + 1, y))
            father[x][y - 1] = (x - 1, y - 1)
            adja[x + 1][y] = False
        if adja[x][y - 1]:
            frontier.append((x, y - 1))
            father[x - 1][y - 2] = (x - 1, y - 1)
            adja[x][y - 1] = False

        if not adja[goal[0]][goal[1]]:
            return father
    return father


def bfsNear(current, n, KB, adja, explored):  # adja and explored are the same, but one for searching, one for checking
    current = (current[0] + 1, current[1] + 1)  # New coordinate is based on adja padding
    frontier = [current]
    adja[current[0]][current[1]] = False
    father = [[None for j in range(n)] for i in range(n)]

    while frontier:  # Stop when frontier = []
        x, y = frontier[0][0], frontier[0][1]  # padding x, y. REAL COORDINATE IS a, b
        a, b = x - 1, y - 1
        frontier.pop(0)

        if explored[a][b + 1] == False and safe(a - 1, b, KB, explored) or \
                explored[a + 1][b + 2] == False and safe(a, b + 1, KB, explored) or \
                explored[a + 2][b + 1] == False and safe(a + 1, b, KB, explored) or \
                explored[a + 1][b] == False and safe(a, b - 1, KB, explored):
            return ((a, b), father)

        if adja[x - 1][y]:  # F F F F adja is a False padding
            frontier.append((x - 1, y))  # F T T F but father is not!
            father[x - 2][y - 1] = (x - 1, y - 1)  # F F F F
            adja[x - 1][y] = False  # Da co trong frontier
        if adja[x][y + 1]:
            frontier.append((x, y + 1))
            father[x - 1][y] = (x - 1, y - 1)
            adja[x][y + 1] = False
        if adja[x + 1][y]:
            frontier.append((x + 1, y))
            father[x][y - 1] = (x - 1, y - 1)
            adja[x + 1][y] = False
        if adja[x][y - 1]:
            frontier.append((x, y - 1))
            father[x - 1][y - 2] = (x - 1, y - 1)
            adja[x][y - 1] = False

    return None


def findPath(current, goal, father):
    path = []
    x, y = goal[0], goal[1]

    while father[x][y] != current:  # Current cell is not counted
        path.insert(0, father[x][y])
        x, y = father[x][y][0], father[x][y][1]

    path.append(goal)
    return path


# Breeze, stench, wumpus, gold
def signal(x, y, KB):
    if KB[x][y][0] and KB[x][y][1]:
        return 2  # Breeze and stench
    if not KB[x][y][0] and not KB[x][y][1]:
        return 0  # No breeze, no stench
    return 1  # Breeze or stench


# ----------------------------------------------------------------
def atLimit(x, y, n):
    return x == n - 1 or y == n - 1


# Check if the cell has stench is only adjacent to the cell we think it has wumpus
def oneStench(x, y, n, KB, explored):
    safeAdja = 0
    if (explored[x][y + 1] != None and safe(x - 1, y, KB, explored)) or explored[x][y + 1]:
        safeAdja += 1
    if (explored[x + 1][y + 2] != None and safe(x, y + 1, KB, explored)) or explored[x + 1][y + 2]:
        safeAdja += 1
    if (explored[x + 2][y + 1] != None and safe(x + 1, y, KB, explored)) or explored[x + 2][y + 1]:
        safeAdja += 1
    if (explored[x + 1][y] != None and safe(x, y - 1, KB, explored)) or explored[x + 1][y]:
        safeAdja += 1

    return safeAdja == 3 or (safeAdja == 2 and atLimit(x, y, n))


# Check if this unexplored cell has wumpus
def checkWumpus(x, y, n, KB, explored):
    nonsense = explored[x][y + 1] and KB[x - 1][y][1] == False or \
               explored[x + 1][y + 2] and KB[x][y + 1][1] == False or \
               explored[x + 2][y + 1] and KB[x + 1][y][1] == False or \
               explored[x + 1][y] and KB[x][y - 1][1] == False

    stench = 0
    if explored[x][y + 1] and KB[x - 1][y][1] == True:
        stench += 1
        a, b = x - 1, y
    if explored[x + 1][y + 2] and KB[x][y + 1][1] == True:
        stench += 1
        a, b = x, y + 1
    if explored[x + 2][y + 1] and KB[x + 1][y][1] == True:
        stench += 1
        a, b = x + 1, y
    if explored[x + 1][y] and KB[x][y - 1][1] == True:
        stench += 1
        a, b = x, y - 1

    if stench == 1:
        sure = oneStench(a, b, n, KB, explored)

    return not nonsense and (stench >= 2 or sure)


def shouldShoot(x, y, n, KB, explored):
    if explored[x][y + 1] == False and checkWumpus(x - 1, y, n, KB, explored):
        return (x - 1, y)
    if explored[x + 1][y + 2] == False and checkWumpus(x, y + 1, n, KB, explored):
        return (x, y + 1)
    if explored[x + 2][y + 1] == False and checkWumpus(x + 1, y, n, KB, explored):
        return (x + 1, y)
    if explored[x + 1][y] == False and checkWumpus(x, y - 1, n, KB, explored):
        return (x, y - 1)

    return None


def printKB(n, KB, explored):
    for i in range(n):
        for j in range(n):
            if explored[i + 1][j + 1]:
                if KB[i][j][0] and KB[i][j][1]:
                    print("Cell", [n - i, j + 1], ": Breeze, Stench")
                elif KB[i][j][1]:
                    print("Cell", [n - i, j + 1], ": Stench")
                elif KB[i][j][0]:
                    print("Cell", [n - i, j + 1], ": Breeze")
                else:
                    print("Cell", [n - i, j + 1], ": Nothing")
    print("-----------------------------------------")


def main():
    n, map = input()  # Read file

    hidden_KB, agent_pos = hiddenKB(n, map)  # Create hidden KB (status of each room) from map

    # Breeze, stench, wumpus, gold
    KB = [[[False, False, False, False] for _ in range(n)] for _ in range(n)]  # Create KB for agent
    KB[agent_pos[0]][agent_pos[1]] = hidden_KB[agent_pos[0]][agent_pos[1]]

    m = n + 2  # Size when include padding
    explored = [[False for _ in range(m)] for _ in
                range(m)]  # A padding with False unexplored, True explored, None out of limit
    explored[0] = explored[m - 1] = [None] * m
    for i in range(m):
        explored[i][0] = explored[i][m - 1] = None

    explored[agent_pos[0] + 1][agent_pos[1] + 1] = True  # Always remember to +1 (skip padding)

    tmp = play(agent_pos[0], agent_pos[1], n, KB, hidden_KB, explored)
    path, point, gold = tmp[0], tmp[1], tmp[2]
    print("Gold: ", gold, "  Point: ", point)

    for i in range(len(path)):
        path[i] = (n - path[i][0], path[i][1] + 1)
    output(path, gold, point)


# ------------------------------------------------------

main()
