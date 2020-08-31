from enum import IntEnum


class Percept(IntEnum):
    Glitter = 0
    Breeze = 1
    Stench = 2
    Scream = 3


class Action(IntEnum):
    GoForward = 0
    TurnLeft = 1
    TurnRight = 2
    Grab = 3
    Shoot = 4
    Climb = 5

    def __repr__(self):
        names = ['GoForward', 'TurnLeft', 'TurnRight', 'Grab', 'Shoot', 'Climb']
        return names[self.value]


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
    Unvisited = 0
    Safe = 1
    Breeze = 2
    Stench = 3


class RoomPredict(IntEnum):
    Unknown = 0
    Safe = 1
    Danger = 2


def getAdjacents(map_size, x, y):
    """
    Param: map_size and current position
    Return: Oxy position of each room corresponding in each direction or None, [Up, Right, Down, Left]
    """
    res = [None, None, None, None]
    for i, d in enumerate(([0, 1], [1, 0], [0, -1], [-1, 0])):
        dx = d[0]
        dy = d[1]
        next_x = x + dx
        next_y = y + dy

        if next_x < 1 or next_x > map_size or next_y < 1 or next_y > map_size:
            continue

        res[i] = [next_x, next_y]
    return res


def toCArrayIndex(map_size, x, y):
    if x is None or y is None:
        return None, None
    return map_size - y, x - 1


def toOxyIndex(map_size, i, j):
    if i is None or j is None:
        return None, None
    return j + 1, map_size - i
