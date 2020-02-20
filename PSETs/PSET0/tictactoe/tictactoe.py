"""
Tic Tac Toe Player
"""

import math
import numpy as np
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    if any(any(itm != EMPTY for itm in row) for row in board):
        b = np.array(board)
        X_freq = (b == X).sum()
        O_freq = (b == O).sum()
        return O if X_freq > O_freq else X
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i, row in enumerate(board):
        for j, itm in enumerate(row):
            if itm is EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] != EMPTY:
        raise Exception("invalid board move")
    mark = player(board)
    new_board = deepcopy(board)
    new_board[i][j] = mark
    return new_board

def transpose(board):
    new_board = deepcopy(board)
    new_board = zip(*new_board)
    return new_board

def check_diagonal_winner(board, mark):
    off_diag = [board[i][i] for i in range(3)]
    main_diag = [board[i][2-i] for i in range(3)]
    return all(itm == mark for itm in off_diag) or all(itm == mark for itm in main_diag)

def winner_check(board, mark):
    return any(all(itm == mark for itm in row) for row in board)

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    transposed_board = transpose(board)
    if winner_check(board, X) or winner_check(transposed_board, X) or check_diagonal_winner(board, X):
        return X
    if winner_check(board, O) or winner_check(transposed_board, O) or check_diagonal_winner(board, O):
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) or all(all(itm != EMPTY for itm in row) for row in board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    p = winner(board)
    if p == X:
        return 1
    elif p == O:
        return -1
    else:
        return 0

def max_value(board):
    if terminal(board):
        return utility(board), None
    v = float("-inf")
    best = None
    for action in actions(board):
        min_v = min_value(result(board, action))[0]
        if min_v > v:
            v = min_v
            best = action
    return v, best

def min_value(board):
    if terminal(board):
        return utility(board), None
    v = float("inf")
    best = None
    for action in actions(board):
        max_v = max_value(result(board, action))[0]
        if max_v < v:
            v = max_v
            best = action
    return v, best

def minimax_without_alpha_beta_pruning(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        return max_value(board)[1]
    elif player(board) == O:
        return min_value(board)[1]
    else:
        raise Exception("bug in minimax algorithm")

def max_value_alpha_beta(board, alpha, beta):
    if terminal(board):
        return utility(board), None
    v = float("-inf")
    best = None
    for action in actions(board):
        min_v = min_value_alpha_beta(result(board, action), alpha, beta)[0]
        if min_v > v:
            v = min_v
            best = action
        alpha = max(alpha, v)
        if beta <= alpha:
            break
    return v, best

def min_value_alpha_beta(board, alpha, beta):
    if terminal(board):
        return utility(board), None
    v = float("inf")
    best = None
    for action in actions(board):
        max_v = max_value_alpha_beta(result(board, action), alpha, beta)[0]
        if max_v < v:
            v = max_v
            best = action
        beta = min(beta, v)
        if beta <= alpha:
            break
    return v, best

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        return max_value_alpha_beta(board, float("-inf"), float("inf"))[1]
    elif player(board) == O:
        return min_value_alpha_beta(board, float("-inf"), float("inf"))[1]
    else:
        raise Exception("bug in minimax algorithm")


    
