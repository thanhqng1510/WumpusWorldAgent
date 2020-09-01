from enum import IntEnum


class GameOver(IntEnum):
    Dead = 0
    ExploredAll = 1
    GotOut = 2


class Percept(IntEnum):
    Glitter = 0
    Breeze = 1
    Stench = 2


class Action(IntEnum):
    GoForward = 0
    TurnLeft = 1
    TurnRight = 2
    Grab = 3
    Shoot = 4
    Climb = 5


class Orientation(IntEnum):
    Up = 0
    Right = 1
    Down = 2
    Left = 3


class RelativeOrientation(IntEnum):
    Front = 0
    Right = 1
    Back = 2
    Left = 3


class RoomReal(IntEnum):
    Breeze = 0
    Stench = 1


def printPercept(percepts):
    names = ['Glitter', 'Breeze', 'Stench']

    print('Percepts: ', end='')
    for i in range(len(percepts)):
        if percepts[i]:
            print(names[i], end=' ')
    print()


def printAction(actions):
    names = ['GoForward', 'TurnLeft', 'TurnRight', 'Grab', 'Shoot', 'Climb']

    print('Actions: ', end='')
    for action in actions:
        print(names[action], end=' ')
    print()


def getAdjacents(map_size, i, j):
    res = [None] * 4
    for idx, d in enumerate(([-1, 0], [0, 1], [1, 0], [0, -1])):
        dx = d[0]
        dy = d[1]
        next_x = i + dx
        next_y = j + dy

        if next_x < 0 or next_x > map_size - 1 or next_y < 0 or next_y > map_size - 1:
            continue

        res[idx] = [next_x, next_y]
    return res


def toCArrayIndex(map_size, x, y):
    if x is None or y is None:
        return None, None
    return map_size - y, x - 1


def toOxyIndex(map_size, i, j):
    if i is None or j is None:
        return None, None
    return j + 1, map_size - i
