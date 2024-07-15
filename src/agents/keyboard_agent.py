from typing import Tuple
from .agent import BaseAgent


class KeyBoardAgent(BaseAgent):

    def _checkInputValid(self, input):
        if input == '':
            return False
        if len(input) != 2:
            print(f"Provided less than 2 positions")
            return False

        try:
            _ = int(input[0].strip())
        except ValueError:
            print('not an integer {}'.format(input[0]))
            return False

        return True

    def getAction(self, game_state: "GameState") -> Tuple[int, int]:
        moves = game_state.getPossibleMoves()
        print('Possible moves for keyboard agent are {}'.format(list(moves.keys())))
        count = 5
        while count > 0:
            move_input = input(
                'Enter the row number (integer) and column number (integer) for the next move separated with comma.\nFor ex. 3,5: ').split(',')
            if self._checkInputValid(move_input):
                row_num, col_num = int(move_input[0].strip()), int(move_input[1].strip())
                move = (row_num, col_num)
                if move in moves.keys():
                    return move
                else:
                    count -= 1
                    input(
                        f'The chosen move: {(row_num, col_num)} is invalid. Please try again and choose a move from {list(moves.keys())}')
                return move

            else:
                count -= 1
                print("Invalid input, please enter the input in appropriate format as instructed. You have {} attempts "
                      "left".format(count))
        raise TimeoutError('Exceeded the maximum number of attempts')