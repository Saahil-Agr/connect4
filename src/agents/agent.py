import random
from typing import Tuple, TYPE_CHECKING
WINNING_PIECES = 4

if TYPE_CHECKING:
    from src.game_state import GameState, Node

class BaseAgent:
    def __init__(self, player_number, **kwargs):
        self.identifier = player_number
        self.BLOCKING_WEIGHT = (10**WINNING_PIECES)/2
        self.WEIGHTS = {num_pieces: 10 ** num_pieces for num_pieces in range(WINNING_PIECES + 1)}
        self.CENTRE_COL_WEIGHT = 2
        print(f"Weights are: {self.WEIGHTS}")

    def getAction(self, game_state: "GameState") -> Tuple[int, int]:
        """
        The Agent will receive a GameState (scotlandyard.py) and
        must return an action from one of the valid actions
        """
        raise NotImplementedError

    def scoreMove(self, game_state: "GameState", move: "Node") -> int:
        ''' Score current move. The score is base on whether the move is blocking opposite player, or advancing self
        game. Scoring is agnosting of the player and assumes both player are utilizing the same scoring function which
        is a simplifying assumption. Hence score will also be a positive value.

        Scoring of the current action has to be evaluated using only the state of the board after taking this particular
        action and nothing else. Using depth and other optimization is the job of algorithm and should not be done here
        '''
        score = 0
        if move.col == game_state.centre_col:
            score += self.CENTRE_COL_WEIGHT

        # Get the longest continuous streak created by the current move
        max_row_lookahead_sum = self.identifier*(
            game_state.getMaxLookAheadSum(move, [0, 1], lambda sum_: sum_.row_sum if sum_ else 0)
            if game_state.getNextNode(move.row, move.col, [0, 1])
            else 0
        )
        max_row_sum = max(self.identifier*move.cumulative_sum.row_sum, max_row_lookahead_sum)
        max_pos_slope_diag_lookahead_sum = self.identifier*(
            game_state.getMaxLookAheadSum(move, [1, 1], lambda sum_: sum_.pos_slope_diag_sum if sum_ else 0)
            if game_state.getNextNode(move.row, move.col, [1, 1])
            else 0
        )
        max_pos_slope_sum = max(self.identifier*move.cumulative_sum.pos_slope_diag_sum, max_pos_slope_diag_lookahead_sum)
        max_neg_slope_diag_lookahead_sum = self.identifier*(
            game_state.getMaxLookAheadSum(move, [-1, 1], lambda sum_: sum_.neg_slope_diag_sum if sum_ else 0)
            if game_state.getNextNode(move.row, move.col, [-1, 1])
            else 0
        )
        max_neg_slope_sum = max(self.identifier*move.cumulative_sum.neg_slope_diag_sum, max_neg_slope_diag_lookahead_sum)
        print(f"Checking if move : {move.row, move.col} is blocking")
        if game_state.isBlockingMove(move):
            score += self.BLOCKING_WEIGHT

        # print(f"printing best sums for move")
        print(max_row_sum, self.identifier*move.cumulative_sum.col_sum, max_pos_slope_sum, max_neg_slope_sum)
        score += (
            self.WEIGHTS[max_row_sum] + self.WEIGHTS[self.identifier*move.cumulative_sum.col_sum] +
            self.WEIGHTS[max_pos_slope_sum] + self.WEIGHTS[max_neg_slope_sum]
        )
        return score


class RandomAgent(BaseAgent):
    def getAction(self, game_state: "GameState") -> Tuple[int, int]:
        """Returns a random move from the set of possible moves"""
        moves = game_state.getPossibleMoves()
        return random.choice(list(moves.keys()))

class GreedyAgent(BaseAgent):
    def getAction(self, game_state: "GameState") -> Tuple[int, int]:
        assert game_state.current_player == -1
        moves = game_state.getPossibleMoves()
        best_score = float('-inf')
        best_move = None
        for move, move_node in moves.items():
            print('-'*20 + f'{move}' + '-'*20)
            move_node.cumulative_sum = game_state.updateNodeCumulativeSum(self.identifier, move)
            print(f"Current sums of the move: {move_node.cumulative_sum}")
            score = self.scoreMove(game_state, move_node)
            print(f"Score for the move is :{score}")
            if score > best_score:
                best_score = score
                best_move = move
        print(f"best score is : {best_score}")
        return best_move

class MinMaxAgent(BaseAgent):
    def getAction(self, game_state:"GameState"):
        pass

class AlphaBetaAgent(BaseAgent) :
    def getAction(self, game_state: "GameState"):
        pass




