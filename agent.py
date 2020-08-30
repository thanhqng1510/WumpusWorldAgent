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
        self.alive = None
        self.got_out = None
        self.hit_wumpus_last_turn = None

    def toRelativeOrientationRoom(self, adj_rooms):
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

    def process(self):
        """
        Param: nothing
        Return: an array of Action

        What do I need to do ???
        Rules:
        1. If there is gold -> Grab
        2. Go to Unknown room with safe prediction, maintain orientation if possible
        3. If all room is known -> Go forward or Right or Left
        """
        cur_i, cur_j = toCArrayIndex(self.map_size, self.current_location[0], self.current_location[1])
        if RoomReal.Glitter in self.map_real[cur_i, cur_j]:
            return [Action.Grab]

        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])  # adjacent rooms of each orientation
        iden_rooms = self.toRelativeOrientationRoom(adj_rooms)  # adjacent rooms of each relative orientation

        # Safe rooms = Visited rooms + (Unvisited and safe rooms)

        iden_safe_rooms = iden_rooms  # only keep safe rooms
        for i in range(len(iden_safe_rooms)):
            if iden_safe_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, iden_safe_rooms[i][0], iden_safe_rooms[i][1])
                if RoomPredict.Safe not in self.map_predict[room_i, room_j]:
                    iden_safe_rooms[i] = None

        iden_safe_unvisited_rooms = iden_safe_rooms  # only keep safe and unvisited rooms
        for i in range(len(iden_safe_unvisited_rooms)):
            if iden_safe_unvisited_rooms[i] is not None:
                room_i, room_j = toCArrayIndex(self.map_size, iden_safe_unvisited_rooms[i][0], iden_safe_unvisited_rooms[i][1])
                if RoomReal.Unvisited not in self.map_real[room_i, room_j]:
                    iden_safe_unvisited_rooms[i] = None

        if iden_safe_unvisited_rooms[RelativeOrientation.Front] is not None:
            return [Action.GoForward]
        if iden_safe_unvisited_rooms[RelativeOrientation.Right] is not None:
            return [Action.TurnRight, Action.GoForward]
        if iden_safe_unvisited_rooms[RelativeOrientation.Left] is not None:
            return [Action.TurnLeft, Action.GoForward]

        # All rooms is visited
        if iden_safe_rooms[RelativeOrientation.Front] is not None:
            return [Action.GoForward]
        if iden_safe_rooms[RelativeOrientation.Right] is not None:
            return [Action.TurnRight, Action.GoForward]
        if iden_safe_rooms[RelativeOrientation.Left] is not None:
            return [Action.TurnLeft, Action.GoForward]

        return [Action.TurnLeft, Action.TurnLeft, Action.GoForward]

# TODO: How to know sunlight and scream, when to climb out
