from util import *
import numpy as np
from random import randrange


class World(object):
    def __init__(self, map):
        self.map = map
        self.map_size = len(map)
        self.agent_current_location = None
        self.agent_orientation = None
        self.agent_alive = None
        self.agent_got_out = None
        self.agent_hit_wumpus_last_turn = None
        self.total_score = None
        self.remain_wumpus = 0
        self.remain_gold = 0

        # Count the number of wumpus and gold
        # Find the spawn location in the map if existed
        for i in range(self.map_size):
            for j in range(self.map_size):
                if "G" in map[i, j]:
                    self.remain_gold += 1
                if "W" in map[i, j]:
                    self.remain_wumpus += 1
                if "A" in map[i, j]:
                    x, y = toOxyIndex(self.map_size, i, j)
                    self.agent_current_location = [x, y]

    @classmethod
    def fromFile(cls, file_path):
        """
        Param: path to a txt file
        Return: a World instance

        Generate map from file
        """
        file_object = open(file_path)

        n = int(file_object.readline())
        map = np.zeros((n, n), dtype=object)

        for i in range(n):
            line = file_object.readline().split('.')
            line[-1] = line[-1][:-1]

            for j in range(int(n)):
                map[i, j] = line[j]

        file_object.close()
        return cls(map)

    def put(self, agent, x=None, y=None):
        """
        Param: an Agent instance, Oxy position to put agent to
        Return: nothing

        Put an agent to the map
        at a desired position or at random
        """
        # Generate agent spawn location if not provided in the map
        if self.agent_current_location is None:
            i, j = toCArrayIndex(self.map_size, x, y)
            while (i is None) or (j is None) or ("G" in self.map[i, j]) or ("P" in self.map[i, j]) or ("W" in self.map[i, j]) or ("B" in self.map[i, j]) or ("S" in self.map[i, j]):  # nothing in the spawn location
                x = randrange(1, self.map_size + 1)
                y = randrange(1, self.map_size + 1)
                i, j = toCArrayIndex(self.map_size, x, y)

            self.agent_current_location = [x, y]

        self.agent_orientation = Orientation.Right
        self.agent_alive = True
        self.agent_got_out = False
        self.agent_hit_wumpus_last_turn = False
        self.total_score = 0

        # Map to save the real data (agent's point of view)
        agent.map_real = np.full((self.map_size, self.map_size, 1), [RoomReal.Unvisited], dtype=object)

        # Map to save the agent's predictions
        agent.map_predict = np.full((self.map_size, self.map_size, 1), [RoomPredict.Unknown], dtype=object)

        agent.map_size = self.map_size
        agent.spawn_location = agent.current_location = self.agent_current_location
        agent.orientation = Orientation.Right

        # The spawn location is (of course) safe
        agent_spawn_i, agent_spawn_j = toCArrayIndex(self.map_size, agent.spawn_location[0], agent.spawn_location[1])

        agent.map_real[agent_spawn_i, agent_spawn_j] = [RoomReal.Safe]
        agent.map_predict[agent_spawn_i, agent_spawn_j] = [RoomPredict.Safe]

    def isGameOver(self):
        """
        Param: nothing
        Return: boolean

        Is the game over yet ???
        I don't care if Lose or Win
        """
        return (not self.agent_alive) or (self.remain_wumpus == 0 and self.remain_gold == 0) or self.agent_got_out

    def getPercept(self):
        """
        Param: nothing
        Return: an array of boolean with format of
        [Glitter, Breeze, Stench, Scream]

        What do I know up till now ???
        """
        res = [False, False, False, False]

        if self.agent_hit_wumpus_last_turn:
            res[Percept.Scream] = True

        i, j = toCArrayIndex(self.map_size, self.agent_current_location[0], self.agent_current_location[1])
        if "G" in self.map[i, j]:
            res[Percept.Glitter] = True

        adj_rooms = getAdjacents(self.map_size, self.agent_current_location[0], self.agent_current_location[1])
        for room in adj_rooms:
            if room is not None:
                room_i, room_j = toCArrayIndex(self.map_size, room[0], room[1])
                if "P" in self.map[room_i, room_j]:
                    res[Percept.Breeze] = True
                if "W" in self.map[room_i, room_j]:
                    res[Percept.Stench] = True

        self.agent_hit_wumpus_last_turn = False
        return res

    def execute(self, agent, action):
        """
        Param: an agent and an Action to perform
        Return: nothing
        
        Let's go !!!
        Step:
            1. Insert/Remove data to agent (important: map)
            2. Check for Breeze or Stench around current tile (on map_predict) -> If exists, can we identify Pit or Wumpus ?
            3. Update score and other variables
            4. Adjust map_predict for each assignment in this map
                a. Check the assigned tile with its adjacents in map_real (except for Safe assignment)
                b. Safe rules !!!
                c. Do not run this step if this tile is visited
        """
        pass

    def getScore(self):
        """
        Param: nothing
        Return: get the score of this game

        How well do I perform ???
        """
        return self.total_score
