import math
import Backgammon_py
# Artifical intelligence agent skeleton
# Assume the agent is always playing as black 

def agent (state):
    move = find_best_move(state)
    if move is not None:
        make_move(state, move)
        if state.isGameOver():
            return winner
    else:
        return False

def find_best_move(state):
    moves = all_moves(state)
    best_move = None
    best_score = -math.inf
    for move in moves:
        score = evaluate_move(state, move)
        if score > best_score:
            best_move = move
            best_score = score
    return best_move

def make_move(state, move):
    # make move function for ai
    # update the move for gameState instance
    state.update_move(move[0], move[1])

    # call checkMove from gameState instance to make the move 
    state.checkMove()

def all_moves(state):
    # find all possible moves for ai
    moves = []
    #for 

#def evaluate_move(state, move):
    # evaluate an individual move for ai 