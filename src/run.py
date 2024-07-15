from collections import defaultdict
import random
from typing import Tuple, Type
import sys

from agents import agent
from game_state import GameState
from agents.keyboard_agent import KeyBoardAgent

NUM_ROWS = 3
NUM_COLS = 4

HUMAN_PLAYER = 1
AI_PLAYER = -1

PLAYER_PIECE_MAPPING = {
    HUMAN_PLAYER: ' x ',
    AI_PLAYER: ' o '
}

class Game:
    def __init__(self, computer_agent: str, human_agent: str="KeyBoardAgent",  num_rows=6, num_cols=7, verbose=False, agent_args={}):
        ''' The main game class that orchestrates the running of the game and encapsulates the core game logic and rules
        '''
        self.NUM_ROWS = num_rows
        self.NUM_COLS = num_cols
        self.verbose = verbose
        self.human_player = loadAgent(human_agent)(HUMAN_PLAYER) # assumes human agent is always keyboard agent for now
        self.computer_player = loadAgent(computer_agent)(AI_PLAYER, **agent_args)
        self._coinToss()
        self.game_state = GameState(num_rows=self.NUM_ROWS, num_cols=self.NUM_COLS, current_player=self.current_player.identifier)
        self.log = defaultdict(list)
        self.print_grid = defaultdict(list)
        self.game_state.verbose = verbose


    def _coinToss(self):
        self.current_player = random.choice([self.human_player, self.computer_player])
        print(f"Player {self.current_player.identifier} will start the game play")

    def alternateTurns(self):
        '''
        Main API that is exposed to the players. This API coordinates that entire game play.
        '''
        for turn in range(self.NUM_COLS*self.NUM_ROWS):
            action = self.current_player.getAction(self.game_state)
            print(f"chosen action by player {self.current_player.identifier} is {action}")
            if not self.validateAction(action):
                raise ValueError(f"Invalid Input")
            self.updateGameState(action)
            print("-*" * 50)
            print(f"Grid after {turn+1} turns")
            self.printGrid()
            print('-' * 50)
            if self.verbose:
                print("possible moves are :")
                self._printPossibleMoves()
                if self.current_player.identifier == AI_PLAYER:
                    node_input = input(f"Is there a node for which you want to check the node value : ").split(',')
                    if len(node_input) == 2:
                        row, col = int(node_input[0].strip()), int(node_input[1].strip())
                        print(f"printing node : {row, col}",self.game_state.grid.get((row, col), None))
            if self.checkWinner():
                print(f"Game Over. Player {self.current_player.identifier} has won the game")
                self.printGrid()
                break
            self.current_player = self.computer_player if self.current_player.identifier == HUMAN_PLAYER else self.human_player
            self.game_state.current_player = self.current_player.identifier
            print("-*" * 50)
            print(f"Current player after turn : {turn} is {self.current_player.identifier}")


    def validateAction(self, action: Tuple[int, int]) -> bool:
        '''Checks if the chosen action is an actual valid move based on computed possible moves'''
        return action in self.game_state.getPossibleMoves().keys()

    def updateGameState(self, action: Tuple[int, int]):
        self.game_state.update(self.current_player.identifier, action)
        print(f"Updated for action : {action}, player : {self.current_player.identifier}")

    def checkWinner(self) -> bool:
        return self.game_state.game_complete

    def printGrid(self):
        final_grid = [[] for _ in range(self.NUM_ROWS)]
        for row in range(self.NUM_ROWS-1, -1, -1):
            for col in range(self.NUM_COLS):
                node = self.game_state.grid.get((row+1, col+1), None)
                node_symbol = PLAYER_PIECE_MAPPING[node.value] if node else ' - '
                final_grid[row].append(node_symbol)
            print('|' + '|'.join(final_grid[row]))

    def _printPossibleMoves(self):
        for idx in self.game_state.getPossibleMoves():
            print(idx)

    def _updateLog(self):
        pass

    def undo(self, num_moves: int):
        pass

    def undoSingleTurn(self, turn_number: int):
        pass

    def _undoLastNLogsUpdates(self, num_actions: int):
        pass

    def _undoSpecificLogsUpdate(self, num_actions: int):
        pass

def loadAgent(agent_to_load: str) -> Type[agent.BaseAgent]:
    '''Loads the agent type as specified in args from the BaseAgent class'''
    if agent_to_load == "KeyBoardAgent":
        agent_class = KeyBoardAgent
    else:
        try:
            agent_class = getattr(agent, agent_to_load)
            if not issubclass(agent_class, agent.BaseAgent):
                raise TypeError(
                    f"The provided agent type of {agent_to_load} for the computer is not a valid class of BaseAgent"
                )
        except AttributeError:
            raise ValueError(f"The agent {agent_to_load} is not defined in any agents class or as a subclass of BaseAgent")

    return agent_class


def default(str):
  return str + ' [Default: %default]'

def readCommand(argv):
    """
    Processes the command used to run connect4 from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python run.py <options>
    EXAMPLES:   (1) python run.py -a GreedyAgent -d 2 -t 30 -v 
                (2) python run.py -a GreedyAgent
    """
    parser = OptionParser(usageStr)

    # parser.add_option('-n', '--numGames', dest='numGames', type='int',
    #                 help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    #TODO we can have a default auto mode. In this case the game will auto run and generate some stats.
    parser.add_option('-a', '--agent', dest='agent',
                    help=default('the agent TYPE for the computer player'),
                    default='RandomAgent')
    parser.add_option(
        '-d', '--depth', dest='depth', help=default('the depth for search algorithms'), default=2
    )
    parser.add_option(
        '-r', '--num_rows', dest='num_rows', type='int',
        help=default('the number of rows in the bord'), default=NUM_ROWS
    )
    parser.add_option(
        '-c', '--num_col', dest='num_cols', type='int',
        help=default('the number of cols in the bord'), default=NUM_COLS
    )
    parser.add_option(
        '-t', '--timeout', dest='timeout', type='int',
        help=default('Maximum length of time an agent can spend computing in a single game'), default=30
    )
    parser.add_option(
        '-v', '--verbose', action='store_true', dest='verbose',
        help=default('Print the board after every move and print every action from every player'), default=False
    )

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    return options



if __name__ == '__main__':
    """
    The main function called when run.py is run
    from the command line:
    See the usage string for more details. Currently, only greedy and random agent are supported

    > python run.py --help
    
    For default (standard game) configuration run
    > python run.py
    
    The standard game configuration can also be run using
    > python run.py -a GreedyAgent -r 6 -c 7
    """
    args = readCommand(sys.argv[1:])  # Get game components based on input
    # print(args)
    agent_args = {}
    agent_args['timeout'] = args.timeout
    agent_args['depth'] = args.depth
    game = Game(computer_agent=args.agent, num_rows=args.num_rows, num_cols=args.num_cols, verbose=args.verbose, agent_args=agent_args)
    print(f"Chosen first player: {game.current_player}")
    game.printGrid()
    game.alternateTurns()