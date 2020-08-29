from world import *
from agent import *


MAX_MOVES = 1000


def main():
    world = World.fromFile('map1.txt')
    agent = Agent()

    world.put(agent)

    num_moves = 0

    while (not world.isGameOver()) and (num_moves < MAX_MOVES):
        percepts = world.getPercept()
        print(percepts)

        action = agent.process(percepts)
        print(action)

        world.executeAction(agent, action)
        num_moves += 1
        print('--------------------')

    score = world.getScore()
    print('Your score is:', score)


main()