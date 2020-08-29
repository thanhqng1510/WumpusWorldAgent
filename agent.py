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

    def process(self, percepts):
        """
        Param: an array of boolean with format of
        [ Glitter, Breeze, Stench, Scream, SunLight ]
        Return: an Action

        What do I need to do ???
        Rules: Go to Unknown room with safe prediction, maintain orientation if possible
        """
        adj_rooms = getAdjacents(self.map_size, self.current_location[0], self.current_location[1])

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
        front_room = adj_rooms[self.orientation]

        front_room_i, front_room_j = toCArrayIndex(self.map_size, front_room[0], front_room[1])
        if (self.map_real[front_room_i, front_room_j] == RoomReal.Unknown) and (self.map_predict[front_room_i, front_room_j] == RoomPredict.Safe):
            return Action.GoForward
        else:
            pass

# TODO: How to get back
