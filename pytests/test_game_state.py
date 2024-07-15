from typing import Dict, List, Tuple

import pytest
from src.game_state import GameState, Node, Sum

'''
Tests to be done
Functions to be tests
- check_if_node_in_grid
- getPossibleMoves
- getNextNode
- isBlockingMove 
- getMaxLookAheadSum
- _updateNegSlopeDiagLowerNextNodesSum
- _updatePosSlopeDiagUpperNextNodesSum
- _updateRowNextNodesSums

- _blockingConnection
- _getDigonalNodesToLeft
- update
- updateNodeCumulativeSum

2. Game State
    - lookahead sum
        - checking if for all 3 directions if it works as expected using different test cases
    - blocking
        - ensuring blocking is true for all possible grid state where there is a blocking move, and it correctly 
        identifies which move is blocking
    - ensuring left to right count of current node is correct
    - middle node update(right side update)
        - ensuring it correctly updates all 3 right side nodes for different cases (none, 1 node to right, 2 nodes to 
        right, 1 same node and next other node)
'''

@pytest.fixture
def game_state():
    # Setup code to create and return a GameState instance
    return GameState(4,4,1)


def create_grid_from_idx_and_sum(node_values: List[Tuple[int, int]], sums: List[Sum]) -> Dict[Tuple[int, int], Node]:
    return {
        (idx_player[0], idx_player[1]): Node(value=idx_player[2], row=idx_player[0], col=idx_player[1], cumulative_sum=s) for idx_player, s in zip(node_values, sums)
    }

def create_grid_from_idx(node_values: List[Tuple[int, int]]) -> Dict[Tuple[int, int], Node]:
    return {
        (idx_player[0], idx_player[1]): Node(value=idx_player[2], row=idx_player[0], col=idx_player[1]) for idx_player in node_values
    }

class TestGameState:

    @pytest.mark.parametrize(
        "node, expected_value",
        [
            (None, False),
            (Node(row=0, col=0), False),
            (Node(row=1, col=1), True),
            (Node(row=-1, col=0), False),
            (Node(row=0, col=1), False),
            (Node(row=3, col=3), True),
            (Node(row=5, col=4), False),
            (Node(row=10, col=1), False),
        ]
    )
    def test_check_if_node_in_grid(self, node: Node, expected_value: bool, game_state: GameState):
        assert game_state.check_if_node_in_grid(node) == expected_value

    @pytest.mark.parametrize(
        "edge_nodes, expected_value",
        [
            ([], []),
            (None, []),
            ([Node(row=1,col=1), Node(row=1, col=2)], [(2, 1), (2,2)]),
            ([Node(row=4, col=2)], []), # possible move is out of  grid
            ([Node(row=1,col=1), Node(row=1, col=2), (Node(row=3,col=3))], [(2, 1), (2,2)]) # last edge is final cell
        ]
    )
    def test_get_possible_moves(self, edge_nodes: List[Node], expected_value: List[Tuple[int, int]], game_state: GameState):
        game_state.edge_nodes = edge_nodes
        assert list(game_state.getPossibleMoves().keys()) == expected_value

    @pytest.mark.parametrize(
        "node, dir, grid_indices, expected_value",
        [
            (
                Node(row=1, col=1, value=1), (0, 1),
                [], None
            ), # empty grid
            (
                Node(row=1, col=1, value=1), (1, 0),
                [(1,1,1), (2, 1, 1)], Node(row=2, col=1, value=1)
            ),  # col next
            (
                Node(row=1, col=1, value=1), (0, 1),
                [(1, 1, 1), (1, 2, 1)], Node(row=1, col=2, value=1)
            ),  # row next
            (
                Node(row=1, col=1, value=1), (1, 1),
                [(1, 1, 1), (2, 2, 1)], Node(row=2, col=2, value=1)
            ),  # pos diag next
            (
                Node(row=2, col=2, value=1), (-1, -1),
                [(2, 2, 1), (1, 1, 1), (3, 3, 1)], Node(row=1, col=1, value=1)
            ),  # pos diag prev
            (
                Node(row=2, col=1, value=1), (-1, 1),
                [(1, 1, 1), (2, 2, 1), (1, 2, 1)], Node(row=1, col=2, value=1)
            ),  # neg diag next
            (
                Node(row=1, col=1, value=1), (-1, -1),
                [(1, 1, 1), (2, 2, 1), (0, 0, 1)], None
            ),  # out of grid
        ]
    )
    def test_get_next_node(self, node, dir, grid_indices, expected_value, game_state):
        game_state.grid = create_grid_from_idx(grid_indices)
        new_node = game_state.getNextNode(node.row, node.col, dir)
        assert new_node == expected_value


    @pytest.mark.parametrize(
        "node, grid_indices, sums, expected_value",
        [
            (
                Node(row=2, col=1, cumulative_sum=Sum(row_sum=1), value=1),
                [], [], [1]
            ), # empty grid only node
            (
                Node(row=1, col=1, cumulative_sum=Sum(row_sum=1), value=1),
                [(1, 2, 1), (1, 3, 1)], [Sum(row_sum=1), Sum(row_sum=2)], [1, 2, 3]
            ), # first node
            (
                Node(row=1, col=2, cumulative_sum=Sum(row_sum=2), value=1),
                [(1, 1, 1), (1, 3, 1)], [Sum(row_sum=1), Sum(row_sum=1)], [2, 3]
            ), # middle node
            (
                Node(row=2, col=3, cumulative_sum=Sum(row_sum=3), value=1),
                [(2, 1, 1), (2, 2, 1)], [Sum(row_sum=1), Sum(row_sum=2)], [3]
            ), # end node

        ]
    )
    def test_updateRowNextNodesSums(self, node, grid_indices, sums, expected_value, game_state):
        game_state.grid = create_grid_from_idx_and_sum(grid_indices, sums)
        game_state.current_player = node.value
        game_state._updateRowNextNodesSums(node)
        idx = 0
        while node and idx < len(expected_value):
            row, col = node.getIndexFromNode()
            new_node = game_state.getNextNode(row, col, (0, 1))
            assert node.cumulative_sum.row_sum == expected_value[idx], f"failure for {idx} for node: {new_node}, expected_value : {expected_value[idx]}"
            idx += 1
            node = new_node

    @pytest.mark.parametrize(
        "node, grid_indices, sums, expected_value",
        [
            (
                Node(row=2, col=1, cumulative_sum=Sum(pos_slope_diag_sum=1), value=1),
                [], [], [1]
            ), # empty grid only node
            (
                Node(row=1, col=1, cumulative_sum=Sum(pos_slope_diag_sum=1), value=1),
                [(2, 2, 1), (3, 3, 1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=2)], [1, 2, 3]
            ), # first node
            (
                Node(row=2, col=2, cumulative_sum=Sum(pos_slope_diag_sum=2), value=1),
                [(1, 1, 1), (3, 3, 1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=1)], [2, 3]
            ), # middle node
            (
                Node(row=3, col=3, cumulative_sum=Sum(pos_slope_diag_sum=3), value=1),
                [(1, 1, 1), (2, 2, 1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=2)], [3]
            ), # end node
            (
                Node(row=2, col=2, cumulative_sum=Sum(pos_slope_diag_sum=-2), value=-1),
                [(1, 1, -1), (3, 3, -1)], [Sum(pos_slope_diag_sum=-1), Sum(pos_slope_diag_sum=-1)], [-2, -3]
            ), # middle node negative player
            (
                Node(row=1, col=1, cumulative_sum=Sum(pos_slope_diag_sum=-1), value=-1),
                [(2, 2, -1), (3, 3, -1)], [Sum(pos_slope_diag_sum=-1), Sum(pos_slope_diag_sum=-2)], [-1, -2, -3]
            ), # first node negative player
            (
                Node(row=2, col=2, cumulative_sum=Sum(pos_slope_diag_sum=-1), value=-1),
                [(1, 1, 1), (3, 3, -1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=-1)], [-1, -2]
            ),  # middle and left is different but right is same
            (
                Node(row=2, col=2, cumulative_sum=Sum(pos_slope_diag_sum=2), value=1),
                [(1, 1, 1), (3, 3, -1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=-1)], [2, -1]
            ),  # middle and left is same but right is different
        ]
    )
    def test_updatePosSlopeDiagUpperNextNodesSum(self, node, grid_indices, sums, expected_value, game_state):
        game_state.grid = create_grid_from_idx_and_sum(grid_indices, sums)
        game_state.current_player = node.value
        game_state._updatePosSlopeDiagUpperNextNodesSum(node)
        idx = 0
        while node and idx < len(expected_value):
            row, col = node.getIndexFromNode()
            new_node = game_state.getNextNode(row, col, (1, 1))
            assert node.cumulative_sum.pos_slope_diag_sum == expected_value[idx], f"failure for {idx} for node: {new_node}, expected_value : {expected_value[idx]}"
            idx += 1
            node = new_node

    @pytest.mark.parametrize(
        "node, grid_indices, sums, expected_value",
        [
            (
                Node(row=2, col=1, cumulative_sum=Sum(neg_slope_diag_sum=1), value=1),
                [], [], [1]
            ), # empty grid only node
            (
                Node(row=3, col=1, cumulative_sum=Sum(neg_slope_diag_sum=1), value=1),
                [(2, 2, 1), (1, 3, 1)], [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=2)], [1, 2, 3]
            ), # first node
            (
                Node(row=2, col=2, cumulative_sum=Sum(neg_slope_diag_sum=2), value=1),
                [(3, 1, 1), (1, 3, 1)], [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=1)], [2, 3]
            ), # middle node
            (
                Node(row=1, col=3, cumulative_sum=Sum(neg_slope_diag_sum=3), value=1),
                [(3, 1, 1), (2, 2, 1)], [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=2)], [3]
            ), # end node
            (
                Node(row=2, col=2, cumulative_sum=Sum(neg_slope_diag_sum=-2), value=-1),
                [(3, 1, -1), (1, 3, -1)], [Sum(neg_slope_diag_sum=-1), Sum(neg_slope_diag_sum=-1)], [-2, -3]
            ), # middle node negative player
            (
                Node(row=2, col=2, cumulative_sum=Sum(neg_slope_diag_sum=-1), value=-1),
                [(3, 1, 1), (1, 3, -1)], [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=-1)], [-1, -2]
            ), # middle and left is different but right is same
            (
                Node(row=2, col=2, cumulative_sum=Sum(neg_slope_diag_sum=2), value=1),
                [(3, 1, 1), (1, 3, -1)], [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=-1)], [2, -1]
            ),  # middle and left is same but right is different
        ]
    )
    def test_updateNegSlopeDiagLowerNextNodesSum(self, node, grid_indices, sums, expected_value, game_state):
        game_state.grid = create_grid_from_idx_and_sum(grid_indices, sums)
        game_state.current_player = node.value
        game_state._updateNegSlopeDiagLowerNextNodesSum(node)
        idx = 0
        while node and idx < len(expected_value):
            row, col = node.getIndexFromNode()
            new_node = game_state.getNextNode(row, col, (-1, 1))
            assert node.cumulative_sum.neg_slope_diag_sum == expected_value[idx], f"failure for {idx} for node: {new_node}, expected_value : {expected_value[idx]}"
            idx += 1
            node = new_node

    @pytest.mark.parametrize(
        "node, dir, accessor_func, grid_indices, sums, expected_value, test_name",
        [
            (
                Node(row=1, col=1, value=1, cumulative_sum=Sum(row_sum=1)), (0,1),
                lambda cum_sum: cum_sum.row_sum if cum_sum else 0, [(1,2,1), (1,3,1)],
                [Sum(row_sum=2), Sum(row_sum=3)], 3, "first test, right lookahead"
            ),
            (
                Node(row=1, col=1, value=1, cumulative_sum=Sum(pos_slope_diag_sum=1)), (1, 1),
                lambda cum_sum: cum_sum.pos_slope_diag_sum if cum_sum else 0, [(2, 2, 1), (3, 3, -1)],
                [Sum(pos_slope_diag_sum=2), Sum(pos_slope_diag_sum=-1)], 2, "second test, diag pos lookahead"
            ),
            (
                Node(row=3, col=1, value=-1, cumulative_sum=Sum(neg_slope_diag_sum=-1)), (-1, 1),
                lambda cum_sum: cum_sum.neg_slope_diag_sum if cum_sum else 0, [(2, 2, -1), (1, 3, -1)],
                [Sum(neg_slope_diag_sum=-2), Sum(neg_slope_diag_sum=-3)], -3, "third test, neg diag lookahead"
            ),
            (
                Node(row=3, col=1, value=-1, cumulative_sum=Sum(neg_slope_diag_sum=-1)), (-1, 1),
                lambda cum_sum: cum_sum.neg_slope_diag_sum if cum_sum else 0, [],
                [], -1, "fourth test, empty grid"
            ),
        ]
    )
    def test_get_max_look_ahead_sum(self, node, dir, accessor_func, grid_indices, sums, expected_value, test_name, game_state):
        game_state.grid = create_grid_from_idx_and_sum(grid_indices, sums)
        assert game_state.getMaxLookAheadSum(node, dir, accessor_func) == expected_value, f"Failed for test case : {test_name}"

    @pytest.mark.parametrize(
        "node, grid_indices, sums, expected_value, test_name",
        [
            (
                Node(row=1, col=2, value=-1),
                [(1, 1, 1), (1, 3, 1), (1, 4, 1)], [Sum(row_sum=1), Sum(row_sum=1), Sum(row_sum=2)],
                True, "first test, row blocking"
            ),
            (
                Node(row=4, col=2, value=-1),
                [(1, 2, 1), (2, 2, 1), (3, 2, 1)], [Sum(col_sum=1), Sum(col_sum=2), Sum(col_sum=3)],
                True, "second test, col blocking"
            ),
            (
                Node(row=2, col=2, value=-1),
                [(1, 1, 1), (3, 3, 1), (4, 4, 1)], [Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=1), Sum(pos_slope_diag_sum=2)],
                True, "Third test, pos diag blocking"
            ),
            (
                Node(row=2, col=3, value=-1),
                [(4, 1, 1), (3, 2, 1), (1, 4, 1)],
                [Sum(neg_slope_diag_sum=1), Sum(neg_slope_diag_sum=2), Sum(neg_slope_diag_sum=1)],
                True, "Third test, pos diag blocking"
            ),

        ]
    )
    def test_is_blocking_move(self, node, grid_indices, sums, expected_value, test_name, game_state):
        game_state.grid = create_grid_from_idx_and_sum(grid_indices, sums)
        game_state.current_player = node.value
        assert game_state.isBlockingMove(node) == expected_value, f"Failed for test case : {test_name}"