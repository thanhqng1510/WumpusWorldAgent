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
        cur_i, cur_j = toCArrayIndex(self.map_size, self.current_location[0], self.current_location[1])
        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])

        if (not percepts[Percept.Breeze]) and (not percepts[Percept.Stench]):  # This room is safe
            self.map_real[cur_i, cur_j] = [False] * 2
            for room in adj_rooms:
                if room is not None:
                    room_i, room_j = toCArrayIndex(self.map_size, room[0], room[1])
                    self.map_danger[room_i, room_j] = False

        else:  # This room is not safe (don't know why)
            if percepts[Percept.Breeze] and percepts[Percept.Stench]:  # This room is Breeze and Stench
                self.map_real[cur_i, cur_j] = [True] * 2
            elif percepts[Percept.Breeze]:  # This room is Breeze only
                self.map_real[cur_i, cur_j][RoomReal.Breeze] = True
                self.map_real[cur_i, cur_j][RoomReal.Stench] = False
            else:  # This room is Stench only
                self.map_real[cur_i, cur_j][RoomReal.Breeze] = False
                self.map_real[cur_i, cur_j][RoomReal.Stench] = True

            for room in adj_rooms:
                if room is not None:
                    room_i, room_j = toCArrayIndex(self.map_size, room[0], room[1])
                    if (self.map_danger[room_i, room_j] is not None) and (not self.map_danger[room_i, room_j]):
                        # If this room is already Safe
                        continue
                    self.map_danger[room_i, room_j] = True

    def process(self, percepts):
        """
        Param: Percept of [Glitter, Breeze, Stench, Scream]
        Return: an array of Action

        What do I need to do ???
        Steps:
            1. If there is gold -> Grab
            2. Go to Unvisited room with Safe prediction, maintain Orientation if possible
            3. All adjacent rooms are Visited/Danger
                a. Find Wumpus -> Shoot
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
        safe_rooms = getAdjacents(self.map_size, self.current_location[0],
                                  self.current_location[1])  # Adjacent rooms of each orientation

        for i in range(len(safe_rooms)):
            if safe_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, safe_rooms[i][0], safe_rooms[i][1])
                if not self.map_danger[room_i, room_j]:
                    safe_rooms[i] = None

        safe_unvisited_rooms = safe_rooms  # Safe and unvisited rooms
        for i in range(len(rel_safe_unvisited_rooms)):
            if rel_safe_unvisited_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, rel_safe_unvisited_rooms[i][0],
                                               rel_safe_unvisited_rooms[i][1])
                if RoomReal.Unvisited not in self.map_real[room_i, room_j]:
                    rel_safe_unvisited_rooms[i] = None

        relative_rooms = self.toRelativeOrientation(adj_rooms)  # adjacent rooms of each relative orientation

        # If there is unvisited room
        if rel_safe_unvisited_rooms[RelativeOrientation.Front] is not None:
            return [Action.GoForward]
        if rel_safe_unvisited_rooms[RelativeOrientation.Right] is not None:
            return [Action.TurnRight, Action.GoForward]
        if rel_safe_unvisited_rooms[RelativeOrientation.Left] is not None:
            return [Action.TurnLeft, Action.GoForward]

        # Climb out
        if self.current_location == self.spawn_location:
            return [Action.Climb]

        # All rooms is visited
        if rel_safe_rooms[RelativeOrientation.Front] is not None:
            return [Action.GoForward]
        if rel_safe_rooms[RelativeOrientation.Right] is not None:
            return [Action.TurnRight, Action.GoForward]
        if rel_safe_rooms[RelativeOrientation.Left] is not None:
            return [Action.TurnLeft, Action.GoForward]

        # No more way -> Go back
        return [Action.TurnLeft, Action.TurnLeft, Action.GoForward]

# TODO: When to shoot
# TODO: How to know when scream -> use hit_wumpus_last_turn
