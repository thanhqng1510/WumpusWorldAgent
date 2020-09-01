from util import *
from queue import Queue
from copy import deepcopy


class Agent(object):
    def __init__(self):
        """
        Constructor of class Agent
        """
        # Format of [Breeze, Stench]
        self.map_real = None

        # Check adjacency after every update
        # Save danger rooms
        self.map_danger = None

        self.map_size = None
        self.spawn_location = None
        self.current_location = None
        self.orientation = None

    def toRelativeOrientation(self, adj_rooms, front=None):
        """
        Change from fixed orientation to relative orientation

        :param adj_rooms: an array of adjacent rooms in format of [Up, Right, Down, Left]
        :param front: an orientation which in front of the agent, if not provided, will use self.orientation
        :return: an array of adjacent rooms in format of [Front, Right, Back, Left]
        """
        res = [None] * 4
        if front is not None:
            orientation = front
        else:
            orientation = self.orientation

        res[RelativeOrientation.Front] = deepcopy(adj_rooms[orientation])  # Front
        res[RelativeOrientation.Right] = deepcopy(adj_rooms[orientation - 3])  # Right = self + 1 = self - 3
        res[RelativeOrientation.Back] = deepcopy(adj_rooms[orientation - 2])  # Back = self + 2 = self - 2
        res[RelativeOrientation.Left] = deepcopy(adj_rooms[orientation - 1])  # Left = self - 1

        return res

    def updateMap(self, percepts):
        """
        Update the map base on agent's last perception (don't need to handle Glitter and Scream)

        :param percepts: an array of Percept in format of [Glitter, Breeze, Stench]
        """
        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])
        cur_i, cur_j = self.current_location[0], self.current_location[1]

        self.map_real[cur_i][cur_j][RoomReal.Breeze] = percepts[Percept.Breeze]
        self.map_real[cur_i][cur_j][RoomReal.Stench] = percepts[Percept.Stench]

        for room in adj_rooms:
            if room is not None:
                room_i, room_j = room[0], room[1]
                if (self.map_danger[room_i][room_j] is not None) and \
                        (not self.map_danger[room_i][room_j]):  # If this room is already Safe
                    continue

                self.map_danger[room_i][room_j] = (percepts[Percept.Breeze] or percepts[Percept.Stench])

    def BFS(self, goal=None):
        """
        Find shortest way to a room

        :param goal: goal of BFS, if not provided, it will find way to the nearest room which is Safe and Unvisited
        :return: path from current room to goal room
        """
        direction_table = {
            3: Orientation.Left,
            2: Orientation.Down,
            1: Orientation.Right,
            0: Orientation.Up,
            -1: Orientation.Left,
            -2: Orientation.Down,
            -3: Orientation.Right
        }

        if (goal is not None) and (self.current_location == goal):
            return []

        frontier = Queue()
        frontier.put([[self.current_location, self.orientation]])  # Safe additional data for each path
        explored_list = [self.current_location]

        while not frontier.empty():
            # Pop from frontier
            cur_path = frontier.get()

            cur_data = deepcopy(cur_path[-1])
            cur_room = deepcopy(cur_data[0])
            cur_orientation = cur_data[1]

            cur_path = cur_path[:-1]

            relative_rooms = getAdjacents(self.map_size, cur_room[0], cur_room[1])
            relative_rooms = self.toRelativeOrientation(relative_rooms, cur_orientation)

            for i in range(len(relative_rooms)):
                if (relative_rooms[i] is not None) and (relative_rooms[i] not in explored_list):
                    room_i, room_j = relative_rooms[i][0], relative_rooms[i][1]
                    if (self.map_danger[room_i][room_j] is not None) and \
                            (self.map_danger[room_i][room_j]):
                        continue

                    # Path to go to a neighbour
                    path_to_neighbour = deepcopy(cur_path)
                    orientation = cur_orientation

                    if i == RelativeOrientation.Left:
                        path_to_neighbour.append(Action.TurnLeft)
                        orientation = direction_table[orientation - 1]
                    elif i == RelativeOrientation.Back:
                        path_to_neighbour.append(Action.TurnLeft)
                        path_to_neighbour.append(Action.TurnLeft)
                        orientation = direction_table[orientation - 2]
                    elif i == RelativeOrientation.Right:
                        path_to_neighbour.append(Action.TurnRight)
                        orientation = direction_table[orientation - 3]

                    path_to_neighbour.append(Action.GoForward)

                    # Test goal condition
                    if ((goal is not None) and (relative_rooms[i] == goal)) or \
                            ((goal is None) and (self.map_real[room_i][room_j] == [None] * 2) and
                             (not self.map_danger[room_i][room_j])):
                        return path_to_neighbour

                    if (self.map_real[room_i][room_j] is not None) and \
                            (not self.map_real[room_i][room_j][RoomReal.Breeze]) and \
                            (self.map_real[room_i][room_j][RoomReal.Stench]):
                        adj_rooms = getAdjacents(self.map_size, room_i, room_j)
                        cnt_unvisited_danger_rooms = 0
                        for room in adj_rooms:
                            if room is not None:
                                adj_i, adj_j = room[0], room[1]
                                if (self.map_real[adj_i][adj_j] == [None] * 2) and \
                                        self.map_danger[adj_i][adj_j]:
                                    cnt_unvisited_danger_rooms += 1
                        if cnt_unvisited_danger_rooms != 0:
                            return path_to_neighbour

                    path_to_neighbour.append([relative_rooms[i], orientation])

                    frontier.put(path_to_neighbour)

                    if relative_rooms[i] not in explored_list:
                        explored_list.append(relative_rooms[i])

        return None

    def process(self, percepts):
        """
        Steps:
            1. If there is gold -> Grab
            2. Go to Unvisited room with Safe prediction, maintain Orientation if possible
            3. Now all adjacent rooms are Visited/Danger
                a. Find Wumpus in adjacent rooms -> Shoot
                b. If none exist
                    ba. BFS to the nearest Unvisited room
                    bb. If none exist -> BFS to the spawn room

        :param percepts: an array of Percept in format of [Glitter, Breeze, Stench]
        :return: an array of action the agent want to perform
        """
        self.updateMap(percepts)
        actions = []

        # Step 1 --------------------------
        if percepts[Percept.Glitter]:
            actions.append(Action.Grab)
        # ---------------------------------

        # Step 2 --------------------------
        # Safe rooms = Visited rooms + (Unvisited and safe rooms)
        adj_rooms = getAdjacents(self.map_size, self.current_location[0],
                                 self.current_location[1])  # Adjacent rooms of each orientation

        safe_unvisited_rooms = deepcopy(adj_rooms)  # Keep only unvisited and safe rooms
        for i in range(len(safe_unvisited_rooms)):
            if safe_unvisited_rooms[i] is not None:
                room_i, room_j = safe_unvisited_rooms[i][0], safe_unvisited_rooms[i][1]
                if (self.map_real[room_i][room_j] != [None] * 2) or self.map_danger[room_i][room_j]:
                    safe_unvisited_rooms[i] = None

        relative_safe_unvisited_rooms = self.toRelativeOrientation(safe_unvisited_rooms)

        # If there is unvisited room
        if relative_safe_unvisited_rooms[RelativeOrientation.Front] is not None:
            actions.append(Action.GoForward)
            return actions
        elif relative_safe_unvisited_rooms[RelativeOrientation.Right] is not None:
            actions.append(Action.TurnRight)
            actions.append(Action.GoForward)
            return actions
        elif relative_safe_unvisited_rooms[RelativeOrientation.Left] is not None:
            actions.append(Action.TurnLeft)
            actions.append(Action.GoForward)
            return actions
        # ---------------------------------

        # Step 3a -----------------------
        cur_i, cur_j = self.current_location[0], self.current_location[1]
        if (self.map_real[cur_i][cur_j] is not None) and \
                (not self.map_real[cur_i][cur_j][RoomReal.Breeze]) and \
                (self.map_real[cur_i][cur_j][RoomReal.Stench]):  # Only shoot if current room is Stench and not Breeze

            relative_danger_rooms = deepcopy(adj_rooms)  # Keep only danger rooms
            relative_danger_rooms = self.toRelativeOrientation(relative_danger_rooms)
            for i in range(len(relative_danger_rooms)):
                if relative_danger_rooms[i] is not None:
                    room_i, room_j = relative_danger_rooms[i][0], relative_danger_rooms[i][1]
                    if (self.map_danger[room_i][room_j] is not None) and \
                            (not self.map_danger[room_i][room_j]):
                        relative_danger_rooms[i] = None

            for i in range(len(relative_danger_rooms)):
                if relative_danger_rooms[i] is not None:
                    if i == RelativeOrientation.Back:
                        actions.append(Action.TurnLeft)
                        actions.append(Action.TurnLeft)
                    if i == RelativeOrientation.Left:
                        actions.append(Action.TurnLeft)
                    if i == RelativeOrientation.Right:
                        actions.append(Action.TurnRight)
                    actions.append(Action.Shoot)

                    room_i, room_j = relative_danger_rooms[i][0], relative_danger_rooms[i][1]
                    self.map_danger[room_i][room_j] = False

                    return actions
        # ---------------------------------

        # Step 3b -----------------------
        path = self.BFS()  # Find a path to the nearest Safe and Unvisited room
        if path is None:
            if self.current_location == self.spawn_location:
                actions.append(Action.Climb)
                return actions

            path = self.BFS(self.spawn_location)  # Find a path to to spawn room

        return actions + path

    def printMap(self):
        # In format of [Breeze, Stench, Danger, Agent]
        map = [[[' '] * 4 for _ in range(self.map_size)] for _ in range(self.map_size)]

        for i in range(len(self.map_real)):
            for j in range(len(self.map_real)):
                if self.map_real[i][j] != [None] * 2:
                    map[i][j][0] = map[i][j][1] = 'x'
                    if self.map_real[i][j][RoomReal.Breeze]:
                        map[i][j][0] = 'B'
                    if self.map_real[i][j][RoomReal.Stench]:
                        map[i][j][1] = 'S'

        for i in range(len(self.map_danger)):
            for j in range(len(self.map_danger)):
                if self.map_danger[i][j]:
                    map[i][j][2] = 'D'

        if self.orientation == Orientation.Up:
            agent = '^'
        elif self.orientation == Orientation.Right:
            agent = '>'
        elif self.orientation == Orientation.Down:
            agent = 'v'
        else:
            agent = '<'
        map[self.current_location[0]][self.current_location[1]][3] = agent

        for i in range(len(map)):
            for j in range(len(map)):
                for k in range(4):
                    print(map[i][j][k], end='')
                print('.', end='')
            print()
