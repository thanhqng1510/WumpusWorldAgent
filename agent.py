from util import *


class Agent(object):
    def __init__(self):
        # Format of [Breeze, Stench]
        self.map_real = None

        # Check adjacency after every update
        # Save danger rooms
        self.map_danger = None

        self.map_size = None
        self.spawn_location = None
        self.current_location = None
        self.orientation = None

    def toRelativeOrientation(self, adj_rooms):
        """
        Param: array of surrounding rooms
        Return: Oxy position of each room corresponding in each direction, [Front, Right, Back, Left]
        """
        res = [None] * 4

        """
        front_room = None
        if self.orientation == Orientation.Up:
            front_room = adj_rooms[0]
        elif self.orientation == Orientation.Right:
            front_room = adj_rooms[1]
        elif self.orientation == Orientation.Down:
            front_room = adj_rooms[2]
        elif self.orientation == Orientation.Left:
            front_room = adj_rooms[3]
        """
        res[RelativeOrientation.Front] = adj_rooms[self.orientation]  # Front
        res[RelativeOrientation.Right] = adj_rooms[self.orientation - 3]  # Right = self + 1 = self - 3
        res[RelativeOrientation.Back] = adj_rooms[self.orientation - 2]  # Back = self + 2 = self - 2
        res[RelativeOrientation.Left] = adj_rooms[self.orientation - 1]  # Left = self - 1

        return res

    def updateMap(self, percepts):
        """
        Param: an array of Percepts format of [Glitter, Breeze, Stench, Scream]
        Return: nothing

        Update map base on agent's last perception
        """
        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])
        cur_i, cur_j = toCArrayIndex(self.map_size, self.current_location[0], self.current_location[1])

        self.map_real[cur_i, cur_j][RoomReal.Breeze] = percepts[Percept.Breeze]
        self.map_real[cur_i, cur_j][RoomReal.Stench] = percepts[Percept.Stench]

        for room in adj_rooms:
            if room is not None:
                room_i, room_j = toCArrayIndex(self.map_size, room[0], room[1])
                if (self.map_danger[room_i, room_j] is not None) and \
                        (not self.map_danger[room_i, room_j]):  # If this room is already Safe
                    continue
                self.map_danger[room_i, room_j] = (percepts[Percept.Breeze] or percepts[Percept.Stench])

    def process(self, percepts):
        """
        Param: Percept of [Glitter, Breeze, Stench, Scream]
        Return: an array of Action

        What do I need to do ???
        Steps:
            1. If there is gold -> Grab
            2. Go to Unvisited room with Safe prediction, maintain Orientation if possible
            3. All adjacent rooms are Visited/Danger
                a. Find Wumpus in adjacent rooms -> Shoot
                b. If none exist
                    ba. BFS to the nearest Unvisited room
                    bb. If none exist -> BFS to the spawn room
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

        safe_unvisited_rooms = adj_rooms  # Keep only save and unvisited rooms
        for i in range(len(safe_unvisited_rooms)):
            if safe_unvisited_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, safe_unvisited_rooms[i][0], safe_unvisited_rooms[i][1])
                if (self.map_real[room_i, room_j] is not None) or \
                        self.map_danger[room_i, room_j]:
                    safe_unvisited_rooms[i] = None

        relative_rooms = self.toRelativeOrientation(adj_rooms)
        relative_safe_unvisited_rooms = self.toRelativeOrientation(safe_unvisited_rooms)

        # If there is unvisited room
        if relative_safe_unvisited_rooms[RelativeOrientation.Front] is not None:
            actions.append(Action.GoForward)
        elif relative_safe_unvisited_rooms[RelativeOrientation.Right] is not None:
            actions.append(Action.TurnRight)
            actions.append(Action.GoForward)
        elif relative_safe_unvisited_rooms[RelativeOrientation.Left] is not None:
            actions.append(Action.TurnLeft)
            actions.append(Action.GoForward)
        # ---------------------------------

        # Step 3a -----------------------

        # ---------------------------------

        # Step 3b -----------------------

        # ---------------------------------
