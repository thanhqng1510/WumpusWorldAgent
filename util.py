from enum import IntEnum


class Percept(IntEnum):
    Glitter = 0
    Breeze = 1
    Stench = 2
    Scream = 3
    SunLight = 4


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


class RoomReal(IntEnum):
    Unknown = 0
    Safe = 1
    Breeze = 2
    Stench = 3


class RoomPredict(IntEnum):
    Unknown = 0
    Safe = 1
    Pit = 2
    Wumpus = 3
    MaybePit = 4
    MaybeWumpus = 5


def getAdjacents(map_size, x, y):
    res = []
    for dx, dy in ([0, 1], [1, 0], [0, -1], [-1, 0]):
        next_x = x + dx
        next_y = y + dy

        if next_x < 1 or next_x > map_size or next_y < 1 or next_y > map_size:
            continue

        res.append([next_x, next_y])
    return res


def toCArrayIndex(map_size, x, y):
    if x is None or y is None:
        return None, None
    return map_size - y, x - 1


def toOxyIndex(map_size, i, j):
    if i is None or j is None:
        return None, None
    return j + 1, map_size - i
