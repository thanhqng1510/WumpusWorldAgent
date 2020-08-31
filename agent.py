from util import *


class Agent(object):
    def __init__(self):
        # Can be [Unknown, Safe, Breeze, Stench] save the room already discovered
        # Glitter and SunLight is also Save
        self.map_real = None

        # Can be [Unknown, Safe, Pit, Wumpus, MaybePit, MaybeWumpus]
        # Check adjacency after every update
        self.map_predict = None

        self.map_size = None
        self.spawn_location = None
        self.current_location = None
        self.orientation = None

    def toRelativeOrientation(self, adj_rooms):
        """
        Param: array of surrounding rooms
        Return: Oxy position of each room corresponding in each direction, [Front, Right, Back, Left]
        """
        res = [None, None, None, None]

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

    def process(self, percepts):
        """
        Param: Percept of [Glitter, Breeze, Stench, Scream]
        Return: an array of Action

        What do I need to do ???
        Rules:
            1. If there is gold -> Grab
            2. Go to Unvisited room with safe prediction, maintain orientation if possible
            3. If this is the spawn room -> Climb
            4. From all rooms which are known and safe -> Go Forward or Right or Left
            5. Go Backward
        """
        cur_i, cur_j = toCArrayIndex(self.map_size, self.current_location[0], self.current_location[1])

        if percepts[Percept.Breeze] is True:
            self.map_real[cur_i, cur_j] = RoomReal.Breeze



        



        if percepts[Percept.Glitter] is True:
            return [Action.Grab]





        # All adjacents of spawn room
        adj_rooms = getAdjacents(self.map_size, agent.spawn_location[0], agent.spawn_location[1])

        # Room next to spawn room is (of course) predict to be safe
        for room in adj_rooms:
            if room is not None:
                room_i, room_j = toCArrayIndex(self.map_size, room[0], room[1])
                agent.map_predict[room_i, room_j] = [RoomPredict.Safe]








        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])  # adjacent rooms of each orientation
        rel_rooms = self.toRelativeOrientation(adj_rooms)  # adjacent rooms of each relative orientation

        # Safe rooms = Visited rooms + (Unvisited and safe rooms)

        rel_safe_rooms = rel_rooms  # only keep safe rooms
        for i in range(len(rel_safe_rooms)):
            if rel_safe_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, rel_safe_rooms[i][0], rel_safe_rooms[i][1])
                if RoomPredict.Safe not in self.map_predict[room_i, room_j]:
                    rel_safe_rooms[i] = None

        rel_safe_unvisited_rooms = rel_safe_rooms  # only keep safe and unvisited rooms
        for i in range(len(rel_safe_unvisited_rooms)):
            if rel_safe_unvisited_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, rel_safe_unvisited_rooms[i][0], rel_safe_unvisited_rooms[i][1])
                if RoomReal.Unvisited not in self.map_real[room_i, room_j]:
                    rel_safe_unvisited_rooms[i] = None

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
# TODO: BFS searching for unvisited room
