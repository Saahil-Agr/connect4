from typing import Callable, Dict, Optional, Tuple, List, Type
import attr

WINNING_PIECES = 4

@attr.s
class Sum:
    row_sum: int=attr.ib(default=0)
    col_sum: int=attr.ib(default=0)
    pos_slope_diag_sum: int=attr.ib(default=0)
    neg_slope_diag_sum: int=attr.ib(default=0)

@attr.s
class Node:
    col: int = attr.ib()
    row: int = attr.ib()
    value: int = attr.ib(default=0)
    cumulative_sum: Sum = attr.ib(default=Sum())

    def getIndexFromNode(self) -> Tuple[int, int]:
        return (self.row, self.col)

class GameState:
    def __init__(self, num_rows, num_cols, current_player: int):
        self.move_numer = 0
        self.current_player = current_player
        self.num_rows = num_rows
        self.num_cols = num_cols
        # A list of tuple containing the (row, col) for all the edge nodes. By definition number of edge nodes is upper
        # bounded by number of columns
        self.edge_nodes = [Node(col=col, row=0, value=0) for col in range(1, self.num_cols+1)]
        self.grid = {} # key is a tuple of row and col
        self.centre_col = int(self.num_cols // 2)
        self.game_complete = False

    def check_if_node_in_grid(self, node: Node) -> bool:
        ''' Checks if the node is within the specfic grid of 7X6.
        '''
        if node is None:
            return False
        return not (node.col <= 0 or node.row <= 0 or node.col > self.num_cols or node.row > self.num_rows)

    def check_if_index_in_grid(self, row, col) -> bool:
        return not (row <= 0 or col <= 0 or col > self.num_cols or row > self.num_rows)

    def getPossibleMoves(self) -> Dict[Tuple[int, int],  Node]:
        ''' Fina a list of places where the player could possibly play their next move. By definiton of the game, these
        are restricted to be the nodes that are 1 above the edge nodes in the grid where edge node is the highest filled
        row in any given column for every column.
        '''
        possible_moves = {}
        if self.edge_nodes is None:
            return possible_moves

        for edge_node in self.edge_nodes:
            new_node = Node(col=edge_node.col, row=edge_node.row+1)
            if not self.check_if_node_in_grid(new_node):
                continue
            possible_moves[(new_node.row, new_node.col)] = new_node

        return possible_moves

    def getNextNode(self, row, col, dir: Tuple[int, int]):
        if self.check_if_index_in_grid(row + dir[0], col + dir[1]):
            return self.grid.get((row + dir[0], col + dir[1]), None)
        return None

    def create_sum_from_prev_nodes_all_dirs(self, row, col) -> Sum:
        '''Modify the existing node to overwrite it's cumulative sum field with corresponding previous nodes'''
        col_node = self.grid.get((row-1, col), None)
        pos_diag_node = self.grid.get((row - 1, col-1), None)
        row_node = self.grid.get((row, col-1), None)
        neg_diag_node = self.grid.get((row + 1, col-1), None)
        return Sum(
            row_sum=row_node.cumulative_sum.row_sum if row_node else 0,
            col_sum=col_node.cumulative_sum.col_sum if col_node else 0,
            pos_slope_diag_sum = pos_diag_node.cumulative_sum.pos_slope_diag_sum if pos_diag_node else 0,
            neg_slope_diag_sum = neg_diag_node.cumulative_sum.neg_slope_diag_sum if neg_diag_node else 0,
        )


    def _gameOver(self, node: Node):
        print(f"Checking if for game over with node : {node.row, node.col}")
        print(node.cumulative_sum)
        if abs(node.cumulative_sum.row_sum) >= WINNING_PIECES or abs(node.cumulative_sum.col_sum) >= WINNING_PIECES or abs(node.cumulative_sum.pos_slope_diag_sum) >= WINNING_PIECES or abs(node.cumulative_sum.neg_slope_diag_sum) >= WINNING_PIECES:
            return True
        return False

    def _getDigonalNodesToLeft(self, node) -> Tuple[Optional[Node], Optional[Node]]:
        '''Given all sum computation are right to left, get the upper left node for negative slop diagonal and the ]
        lower left node for the positive slop diagonal'''
        pos_slope_diagonal_node = self.grid.get((node.row-1, node.col-1), None) # r-1, c-1
        neg_slope_diagonal_node = self.grid.get((node.row + 1, node.col - 1), None) # r+1, c-1
        return pos_slope_diagonal_node, neg_slope_diagonal_node

    def _updateRowNextNodesSums(self, node):
        right_node = self.grid.get((node.row, node.col + 1), None)
        if right_node is None or right_node.value != node.value:
            print(f"terminating row update at : {right_node}")
            # no need to update anything since the right node anyways started with 1 or -1 value for row_sum since it's left was empty
            return
        else:
            right_node.cumulative_sum.row_sum = node.cumulative_sum.row_sum + self.current_player
            if self._gameOver(right_node):
                self.game_complete = True
                return
            return self._updateRowNextNodesSums(right_node)


    def _updatePosSlopeDiagUpperNextNodesSum(self, node):
        '''
        '''
        pos_slope_diag_upper_node = self.grid.get((node.row + 1, node.col + 1), None) # r+1, c+1
        if pos_slope_diag_upper_node is None or pos_slope_diag_upper_node.value != node.value:
            print(f"Existing pos slop lookahead sum : {pos_slope_diag_upper_node}")
            return
        else:
            pos_slope_diag_upper_node.cumulative_sum.pos_slope_diag_sum = node.cumulative_sum.pos_slope_diag_sum + self.current_player
            if self._gameOver(pos_slope_diag_upper_node):
                self.game_complete = True
                return
            return self._updatePosSlopeDiagUpperNextNodesSum(pos_slope_diag_upper_node)

    def _updateNegSlopeDiagLowerNextNodesSum(self, node):
        neg_slope_diag_lower_node = self.grid.get((node.row - 1, node.col + 1), None) # r-1, c+1
        if neg_slope_diag_lower_node is None or neg_slope_diag_lower_node.value != node.value:
            print(f"Existing neg slop lookahead sum : {neg_slope_diag_lower_node}")
            return
        else:
            neg_slope_diag_lower_node.cumulative_sum.neg_slope_diag_sum = node.cumulative_sum.neg_slope_diag_sum + self.current_player
            if self._gameOver(neg_slope_diag_lower_node):
                self.game_complete = True
                return
            return self._updateNegSlopeDiagLowerNextNodesSum(neg_slope_diag_lower_node)


    def _updateForMiddleNode(self, node: Node):
        '''if the enter node is in between 2 nodes for a row or a diagonal, we do the following iteratively:
        1. Check if the value of the new node is same as next.
        2. If no do nothing,
        3. if yes, update the value of the corresponding sum for the next node by 1
        3. Check if the game is over
        4. if yes, exit
        5. If not, repeat above for next node
        Repeat above steps for row, and both diagonals
        '''
        print(f"Updating middle node")
        self._updateRowNextNodesSums(node)
        if self.game_complete:
            return
        # Update the lower nodes corresponding to negative slop diagonal (nodes to the right)
        self._updateNegSlopeDiagLowerNextNodesSum(node)
        if self.game_complete:
            return
        # update the upper nodes corresponding to positive slop diagonal (nodes to the right)
        self._updatePosSlopeDiagUpperNextNodesSum(node)
        print(f"Finished updating for middle node")
        return

    def updateNodeCumulativeSum(self, player_number: int, action: Tuple[int, int]) -> Sum:
        curr_node = Node(row=action[0], col=action[1])
        col_prev_node = self.edge_nodes[action[1] - 1]  # since grid is 1 indexed
        # print(f"printing previous col node: {col_prev_node}")
        assert col_prev_node.row == action[0] - 1 and col_prev_node.col == action[1], f"Move is not a valid move"
        # if the player plays a blocking move then the most recent node starts with a new sum else we add to the sum
        # from previous node for both row and col
        if player_number != col_prev_node.value:
            new_col_sum = player_number
        else:
            new_col_sum = player_number + col_prev_node.cumulative_sum.col_sum

        row_prev_node = self.grid.get((action[0], action[1]-1), None)  # only to check for game begining
        if row_prev_node is None or player_number != row_prev_node.value:
            new_row_sum = player_number
        else:
            new_row_sum = player_number + row_prev_node.cumulative_sum.row_sum

        pos_slope_diagonal, neg_slope_diagonal = self._getDigonalNodesToLeft(curr_node)
        pos_slope_diag_sum = player_number
        neg_slope_diagonal_sum = player_number
        if pos_slope_diagonal is not None and player_number == pos_slope_diagonal.value:
            pos_slope_diag_sum = player_number + pos_slope_diagonal.cumulative_sum.pos_slope_diag_sum

        # verify this logic again
        if neg_slope_diagonal is not None and player_number == neg_slope_diagonal.value:
            neg_slope_diagonal_sum = player_number + neg_slope_diagonal.cumulative_sum.neg_slope_diag_sum

        curr_cumulative_sum = Sum(
            row_sum=new_row_sum,
            col_sum=new_col_sum,
            neg_slope_diag_sum=neg_slope_diagonal_sum,
            pos_slope_diag_sum=pos_slope_diag_sum
        )
        return curr_cumulative_sum


    def update(self, player_number, action: Tuple[int, int]):
        '''
        remove the edge node corresponding to the new node from edge nodes
        add the new node as edge node.
        Compute the cumulative sum value for the new node for rows, cols and each diagonal.
        Check if game over and set the state accordingly.
        Update the right row counts, positive slope diagonal and negative slope diagonal counts recursively if it is a middle node
        '''
        self.move_numer += 1
        curr_cumulative_sum = self.updateNodeCumulativeSum(player_number, action)
        print(f"after playing action, the sum of the played node is : {curr_cumulative_sum}")
        curr_node = Node(row=action[0], col=action[1], value=player_number, cumulative_sum=curr_cumulative_sum)
        self.edge_nodes[action[1]-1] = curr_node
        self.grid[(action[0], action[1])] = curr_node
        if self._gameOver(curr_node):
            self.game_complete = True
            return

        # In case the current move being played is a position that was between 2 existing played positions either
        # rowwise, or either diagonally, specially if nodes existed to the right of the new node, the cum sum for right
        # nodes need to be updated
        self._updateForMiddleNode(curr_node)
        return


    def getMaxLookAheadSum(self, node: Node, dir: List[int], sum_accessor_fn: Callable):
        ''' Recursively find the length of the max continuous series for same player as for the <node> that exists to
        the right of the node in as per the directions specified. The directions could be [0, 1], [1, 1], [-1, 1]'''
        next_node = self.grid.get((node.row + dir[0], node.col + dir[1]), None)
        if next_node is None or next_node.value != node.value:
            return sum_accessor_fn(node.cumulative_sum)
        else:
            return self.getMaxLookAheadSum(next_node, dir, sum_accessor_fn)


    def _blockingConnection(self, prev_node: Optional[Node], next_node: Optional[Node], dir: Tuple[int, int], sum_accessor_func: Callable):
        '''
        #TODO Don't need to compute maxlookahead here as long as it is called from agents score function, since all max
        lookaheads are already computed. so  room for potential optimization
        '''
        is_blocking = False
        if prev_node is not None:
            print(f"checking prev node for blocking : {-1*self.current_player*sum_accessor_func(prev_node.cumulative_sum)}")
            print(-1*self.current_player)
            is_blocking = -1*self.current_player*sum_accessor_func(prev_node.cumulative_sum) == WINNING_PIECES-1

        if next_node is not None:
            max_lookahead_sum = self.getMaxLookAheadSum(next_node, dir, sum_accessor_func)
            print(f"next node was not none and the max lookahead sum is : {max_lookahead_sum}")
            if prev_node:
                is_blocking = -1*self.current_player*(sum_accessor_func(prev_node.cumulative_sum) + max_lookahead_sum) >= WINNING_PIECES-1
            else:
                is_blocking = -1*self.current_player*max_lookahead_sum >= WINNING_PIECES-1

        return is_blocking

    def isBlockingMove(self, node: Node) -> bool:
        ''' For a node checks for the row, col and both diagonals if the sum of cumulative sum of prev and next node in
        each direction will be equal to 4 for the opposite player.
        '''
        # col Check
        # Ideally below node would always be present but for the first row that's not true.
        below_node = self.grid.get((node.row-1, node.col), None)
        if below_node and -1*self.current_player*below_node.cumulative_sum.col_sum == WINNING_PIECES-1:
            print(f"Col blocking move : {node.row, node.col}")
            return True

        # row check
        left_node = self.grid.get((node.row, node.col-1), None)
        right_node = self.grid.get((node.row, node.col+1), None)
        print(f"left node while checking for blocking: {left_node}")
        blocking_row = self._blockingConnection(
            left_node, right_node, (0,1), lambda cum_sum: cum_sum.row_sum if cum_sum else 0
        )
        print(f"row blocking is : {blocking_row}")
        if blocking_row:
            print(f"Row blocking move : {node.row, node.col}")
            return blocking_row

        # positive slope diag check
        left_node = self.grid.get((node.row-1, node.col - 1), None)
        right_node = self.grid.get((node.row + 1, node.col + 1), None)
        ### Print stuff to be removed later
        print(f"checking for positive slop blocking,left node: {left_node}\nright_node: {right_node}")
        blocking_pos_diag = self._blockingConnection(
            left_node, right_node, (1, 1), lambda cum_sum: cum_sum.pos_slope_diag_sum if cum_sum else 0
        )
        if blocking_pos_diag:
            print(f"Positive diagonal blocking move : {node.row, node.col}")
            return blocking_pos_diag

        # Negative slope diag check
        left_node = self.grid.get((node.row + 1, node.col - 1), None)
        right_node = self.grid.get((node.row - 1, node.col + 1), None)
        blocking_neg_diag = self._blockingConnection(
            left_node, right_node, (-1, 1), lambda cum_sum: cum_sum.neg_slope_diag_sum if cum_sum else 0
        )
        if blocking_neg_diag:
            print(f"Negative Diagonal blocking move : {node.row, node.col}")
            return blocking_neg_diag

        return False