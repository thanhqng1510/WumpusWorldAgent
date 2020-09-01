from util import *
from random import randrange
from copy import deepcopy


class World(object):
    def __init__(self, map):
        """
        Constructor of class World

        :param map: an nparray map
        """
        self.map = map
        self.map_size = len(map)
        self.agent_current_location = None
        self.agent_orientation = None
        self.agent_alive = None
        self.agent_got_out = None
        self.total_score = None
        self.remain_wumpus = 0
        self.remain_gold = 0

        # Count the number of wumpus and gold
        # Find the spawn location in the map if existed
        for i in range(self.map_size):
            for j in range(self.map_size):
                if "G" in map[i][j]:
                    self.remain_gold += 1
                if "W" in map[i][j]:
                    self.remain_wumpus += 1
                if "A" in map[i][j]:
                    self.agent_current_location = [i, j]

    @classmethod
    def fromFile(cls, file_path):
        """
        A factory function of class World

        :param file_path: path to a text-file map
        :return: an instance of class World
        """
        file_object = open(file_path)

        n = int(file_object.readline())
        map = [['' for _ in range(n)] for _ in range(n)]

        for i in range(n):
            rooms = file_object.readline().split('.')
            rooms[-1] = rooms[-1][:-1]

            for j in range(int(n)):
                map[i][j] = rooms[j]

        file_object.close()
        return cls(map)

    def put(self, agent, i=None, j=None):
        """
        Put an agent to the map

        :param agent: an Agent instance
        :param i: desired location of agent on x coordinate
        :param j: desired location of agent on y coordinate
        """
        # Generate agent spawn location if not provided in the map
        if self.agent_current_location is None:
            while (i is None) or (j is None) or \
                    ("G" in self.map[i][j]) or \
                    ("P" in self.map[i][j]) or \
                    ("W" in self.map[i][j]) or \
                    ("B" in self.map[i][j]) or \
                    ("S" in self.map[i][j]):  # nothing in the spawn location
                i = randrange(0, self.map_size)
                j = randrange(0, self.map_size)

            self.agent_current_location = [i, j]

        self.agent_orientation = Orientation.Right
        self.agent_alive = True
        self.agent_got_out = False
        self.total_score = 0

        # Map to save the real data (agent's point of view), format of [Breeze, Stench]
        agent.map_real = [[[None, None] for _ in range(self.map_size)] for _ in range(self.map_size)]

        # Map to save the agent's predictions
        agent.map_danger = [[None for _ in range(self.map_size)] for _ in range(self.map_size)]

        agent.map_size = self.map_size
        agent.spawn_location = deepcopy(self.agent_current_location)
        agent.current_location = deepcopy(self.agent_current_location)
        agent.orientation = Orientation.Right

        # The spawn location is (of course) not danger
        agent_spawn_i, agent_spawn_j = agent.spawn_location[0], agent.spawn_location[1]
        agent.map_danger[agent_spawn_i][agent_spawn_j] = False

    def isGameOver(self):
        """
        To tell when the game is over

        :return: tell how the game ends (None of the game is not over yet)
        """
        if not self.agent_alive:
            return GameOver.Dead
        if self.remain_wumpus == 0 and self.remain_gold == 0:
            return GameOver.ExploredAll
        if self.agent_got_out:
            return GameOver.GotOut
        return None

    def getPercept(self):
        """
        Get to know the environment of this room

        :return: an array of Percept in format of [Glitter, Breeze, Stench]
        """
        res = [False] * 3
        cur_i, cur_j = self.agent_current_location[0], self.agent_current_location[1]

        res[Percept.Glitter] = ("G" in self.map[cur_i][cur_j])

        adj_rooms = getAdjacents(self.map_size, cur_i, cur_j)
        for room in adj_rooms:
            if room is not None:
                room_i, room_j = room[0], room[1]
                if "P" in self.map[room_i][room_j]:
                    res[Percept.Breeze] = True
                if "W" in self.map[room_i][room_j]:
                    res[Percept.Stench] = True

        return res

    def execute(self, agent, actions):
        score_table = {
            Action.GoForward: -10,
            Action.TurnLeft: 0,
            Action.TurnRight: 0,
            Action.Grab: 100,
            Action.Shoot: -100,
            Action.Climb: 10
        }

        direction_table = {
            3: Orientation.Left,
            2: Orientation.Down,
            1: Orientation.Right,
            0: Orientation.Up,
            -1: Orientation.Left,
            -2: Orientation.Down,
            -3: Orientation.Right
        }

        for action in actions:
            self.total_score += score_table[action]

            if action == Action.Climb:
                self.agent_got_out = True

            elif action == Action.Shoot:
                front_room = deepcopy(self.agent_current_location)
                if self.agent_orientation == Orientation.Up:
                    front_room[0] -= 1
                elif self.agent_orientation == Orientation.Right:
                    front_room[1] += 1
                elif self.agent_orientation == Orientation.Down:
                    front_room[0] += 1
                else:
                    front_room[1] -= 1
                front_i, front_j = front_room[0], front_room[1]
                if "W" in self.map[front_i][front_j]:
                    self.map[front_i][front_j] = self.map[front_i][front_j].replace("W", "")
                    self.remain_wumpus -= 1

            elif action == Action.Grab:
                self.remain_gold -= 1

            elif action == Action.TurnRight:
                agent.orientation = self.agent_orientation = direction_table[self.agent_orientation - 3]

            elif action == Action.TurnLeft:
                agent.orientation = self.agent_orientation = direction_table[self.agent_orientation - 1]

            else:  # GoForward
                if self.agent_orientation == Orientation.Up:
                    self.agent_current_location[0] -= 1
                elif self.agent_orientation == Orientation.Right:
                    self.agent_current_location[1] += 1
                elif self.agent_orientation == Orientation.Down:
                    self.agent_current_location[0] += 1
                else:
                    self.agent_current_location[1] -= 1
                agent.current_location = deepcopy(self.agent_current_location)

    def getScore(self):
        """
        Retrieve the total score of this try

        :return: total score
        """
        return self.total_score
