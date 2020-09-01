from world import *
from agent import *


MAX_MOVES = 1000


def main():
    world = World.fromFile('map1.txt')
    agent = Agent()

    world.put(agent)

    num_moves = 0
    step = 1
    result = None

    while (result is None) and (num_moves < MAX_MOVES):
        print('Step:', step)
        step += 1

        print('Current score:', world.getScore())

        percepts = world.getPercept()
        printPercept(percepts)

        actions = agent.process(percepts)
        agent.printMap()
        printAction(actions)

        world.execute(agent, actions)
        num_moves += 1
        print('--------------------')

        result = world.isGameOver()

    if result == GameOver.Dead:
        print('Agent has been killed')
    elif result == GameOver.ExploredAll:
        print('Agent has grabbed all gold and killed all wumpus')
    else:  # Agent climb out
        print('Agent has climbed out')

    score = world.getScore()
    print('Agent\'s score:', score)


main()
