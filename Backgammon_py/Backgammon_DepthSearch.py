import random
import pygame
from time import sleep
import sys
import string
import math 

'''
V8
- Board is list of ints instead of Point objects to improve efficiency (positive ints are white pieces, negative ints are black pieces)
- Moved get_all_moves function to Controller class to improve efficiency 
- Fixed bug in can_bear_off() function where black could never bear off (negative number of pieces because of board representation never met bearing off criteria) 
- Removed get_risk() function because it wasn't being used 
'''
# Constants for game board size and number of pieces
BOARD_SIZE = 24
NUM_PIECES = 15

# General functions 
def has_punctuation(word):
    for character in word:
        if character in string.punctuation:
            return True
    return False

# Define a text class that inherits from pygame.sprite.Sprite to display text on gameboard
class gameText(pygame.sprite.Sprite):
    def __init__(self, _text, coords, size, color = (0, 0, 0), bold = False):
        super().__init__()
        self.bold = bold
        self.color = color
        self.font = pygame.font.SysFont(None, size, self.bold)
        self.text = self.font.render(str(_text), True, color)
        self.image = self.text
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

# Define a Piece class that inherits from pygame.sprite.Sprite to represent pieces on board 
class Piece(pygame.sprite.Sprite):
    def __init__(self, team, coords):
        super().__init__()
        self.image = pygame.image.load(self.get_team(team))
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def get_team(self, team):
        if team >= 1:
            return "whitePieceV2.png"
        else:
            return "blackPieceV2.png"

class Player(object):
    """description of class"""
    # set player's name, pieces on bar and in goal, and team (1, -1; white or black respectively)
    def __init__(self, name, team):
        self.name = name
        self.bar = 0
        self.goal = 0
        self.team = team

    def get_home(self):
        if self.team == 1:
            return [0, 1, 2, 3, 4, 5, 6]
        else:
           return [0, 24, 23, 22, 21, 20, 19]

    def get_team_color(self):
        if self.team == 1:
            return "White"
        else: 
            return "Black"

    def get_team(self):
        return self.team

    def get_name(self):
        return self.name

    def reset(self, new_team):
        self.bar = 0
        self.goal = 0
        self.team = new_team

    def get_bar(self):
        return self.bar

    def get_goal(self):
        return self.goal

    def add_bar(self):
        self.bar += 1

    def remove_bar(self):
        self.bar -= 1

    def add_goal(self):
        self.goal += 1

    def remove_goal(self):
        self.goal -= 1

# AI backgammon player
class salami_bot(Player):
    def __init__(self, name, team, weights = [1, 1, 1, 1]):
        super().__init__(name, team)
        # store the sequence of moves maximize_turn finds, the stack is empty at the beginning of the bot's turn, but stores all the moves for the bots subsequent turns, so maximize_turn is only called once each turn 
        self.best_move_sequence = []

        # list to store weights for scoring function heuristics 
        self.weights = weights

        # heuristic values for optimization 
        self.old_heuristics = None
        self.new_heuristics = None

    def get_hVals(self):
        return self.old_heuristics

    def turn(self, game):

        # standard turn function for smart bot and default bot, just calls the find_best_move function which is different for each bot
        move = self.find_best_move(game)

        # adjust game dice and move 
        game.update_move(move[0], move[1])
        game.update_dice(move[2])

    def find_best_move(self, game):
        # the maximize_turn function fills the move stack with the optimal sequence of moves for the bot's turn. It should only be called once, at the beginning of the bot's turn
        # it should then pull the move from the stack and pass the move to the controller 
        if len(self.best_move_sequence) == 0:
            # when the turn function is first called for the bot, moveStack has the bot's last move made in its previous turn and all the moves from the opponent's turn, so it has to be cleared 
            # the bot's last move from its last turn is in the move stack because, although it is undone in the maximize turn function, it is added back to the stack when the move is committed to the board 
            game.moveStack.clear()

            # self.maximize_turn(game, depth), where depth is how many moves ahead the function is going to look, maximum is four (double dice), minumum is 1 (adjust dice sees there is only one available move), the function becomes too complex when trying to optimize for four moves ahead, so the maximum depth will be two moves, therefore, depth = len(dice) if the length of the dice is <= 2, otherwise it is 2
            depth = len(game.dice) if len(game.dice) <= 2 else 2 

            # call maximize_turn to fill move stack 
            self.maximize_turn(game, depth)
        #game.printBoard()
        move = self.best_move_sequence.pop()
        return move

    # function to find all possible unique moves for current gamestate
    def get_all_moves(self, game):

        all_moves = []
        # if the player has barred pieces don't check all From points, player can only move from bar 
        if game.currentPlayer.get_bar() > 0:
            opponent_home = game.opponent.get_home()
            # check if the player can move from bar with first dice 
            if game.board[opponent_home[game.dice[0]]] >= -1 and game.opponent.get_team() < 0 or game.board[opponent_home[game.dice[0]]] <= 1 and game.opponent.get_team() > 0:
                all_moves.append([0, game.opponent.get_home()[game.dice[0]], game.dice[0]])

            # check to see if there is another dice and if there is check if it is a valid move 
            if len(game.dice) > 1 and game.dice[0] != game.dice[1]:
                if game.board[opponent_home[game.dice[1]]] >= -1 and game.opponent.get_team() < 0 or game.board[opponent_home[game.dice[1]]] <= 1 and game.opponent.get_team() > 0:
                    all_moves.append([0, game.opponent.get_home()[game.dice[1]], game.dice[1]])

            return all_moves

        # get all moves available on board 
        fromPoints = [index for index in range(1, BOARD_SIZE + 1) if game.board[index] > 0 and game.currentPlayer.get_team() > 0 or game.board[index] < 0 and game.currentPlayer.get_team() < 0]

        # sentinel to track how dice checks
        check = 1
        while check:
            # for each point in the list 
            for point in fromPoints:
                toPoint = point - game.dice[0] * game.currentPlayer.get_team()
                # change To point to 25 if the dice moves the player to the goal 
                if toPoint <= 0 or toPoint >= 25:
                    toPoint = 25
                game.update_move(point, toPoint)
                # if the move is valid add the move to the all moves list 
                if game.check_move():
                    all_moves.append([point, toPoint, game.dice[0]])
                    continue

            # once we have iterated through all possible from positions using dice one, if there is only one dice or they are doubles, exit while loop
            if len(game.dice) == 1 or len(game.dice) > 2 or game.dice[0] == game.dice[1]:
                break
            else:
                if check == 1:
                    check += 1
                    game.swap_dice()
                else:
                    #swap dice back and break from while loop
                    game.swap_dice()
                    break

        game.message = ''
        return all_moves

    # this function will evaluate the player's turn, to a maximum depth of two moves, considering all possible moves and returning the optimal move, the function considers what the player can do next after making the first move by recursively calling the function  
    def maximize_turn(self, game, depth):
       
        alpha = -math.inf
        max_score = -math.inf

        moves = game.get_all_moves()
        for move in moves:
            #print(f'\nMAXIMIZE TURN\nChecking move: {move[0]}, {move[1]}, {move[2]}\n\n')
            game.update_dice(move[2])
            game.update_move(move[0], move[1])
            game.make_move()

            # have to check for special case where a) depth = 2 but the player only has one move left (i.e. final piece to bear off) or b) the player's first move negates the second move, in either case a call to score_turn will return -inf and the function will not load any moves to best_move_sequence 
            if depth == 2 and len(game.get_all_moves()) == 0:
                # call utility function to evaluate value of first move 
                score = self.utility(game.board, game.currentPlayer, game.opponent)
                # if this move has a better score clear the best_move_sequence 
                if max_score < score:
                    self.best_move_sequence.clear()
            # otherwise call score function 
            else:
                score = self.score_turn(game, depth - 1, alpha)

           # if the score for the current sequence of moves is better than the previous, update max_score, insert move into stack
            #print(f'If {max_score} is less than {score}') 
            if max_score < score:
                #print(f'Append to best move sequence')
                max_score = alpha = score
                self.best_move_sequence.append(move)

            #print(f'\nMAXIMIZE TURN\nUndo Move\n\n')
            #print(f'Best move sequence: {len(self.best_move_sequence)}')
            game.undo_move()

    def score_turn(self, game, depth, alpha):
        if depth == 0:
            return self.utility(game.board, game.currentPlayer, game.opponent)

        max_score = alpha

        moves = game.get_all_moves()
        for move in moves:
            #print(f'\SCORE TURN\nChecking move: {move[0]}, {move[1]}, {move[2]}\n\n')
            game.update_dice(move[2])
            game.update_move(move[0], move[1])
            game.make_move()

            score = self.score_turn(game, depth - 1, alpha)

            # if the score for the current sequence of moves is better than the previous, update max_score, insert move into stack 
            if max_score < score:
                max_score = score
                # if there is already a sequence of moves in the stack it has to be cleared 
                if len(self.best_move_sequence) >= depth:
                    self.best_move_sequence.clear()
                self.best_move_sequence.append(move)
                # update heuristics list 
                self.old_heuristics = self.new_heuristics

            #print(f'\nSCORE TURN\nUndo Move\n\n')
            game.undo_move()

        # assign max_score to alpha, which will keep track of the maximum score for the previous iterations through the first moves 
        alpha = max_score
        return alpha

    # evaluate player's position on board 
    def utility(self, board, cPlayer, oPlayer):
        # how many pips do they control (i.e. 2 or more pieces on pip)
        cPips = [index for index in range(1, BOARD_SIZE + 1) if board[index] >= 2 and cPlayer.get_team() > 0 or board[index] <= -2 and cPlayer.get_team() < 0]
        h1 = len(cPips) * self.weights[0]

        # how many pieces are in the goal 
        cGoal = cPlayer.get_goal()
        h2 = cGoal * self.weights[1]

        # how many opponent pieces are on the bar 
        oBar = oPlayer.get_bar()
        h3 = oBar * self.weights[2]

        # how many blots 
        cBlots = [index for index in range(1, BOARD_SIZE + 1) if board[index] == 1 and cPlayer.get_team() == 1 or board[index] == -1 and cPlayer.get_team() == -1]
        h4 = len(cBlots) * self.weights[3]

        # calculate total score by weighing each factor 
        score = h1 + h2 + h3 - h4

        # create list of heuristics
        new_hVals = [h1, h2, h3, h4]
        if self.old_heuristics == None:
            self.old_heuristics = new_hVals
        self.new_heuristics = new_hVals

        #print(f'UTILITY\nteam: {game.currentPlayer.get_team()}\nScore: {score}\n')
        return score

# bot class for default version 
class default_bot(salami_bot):
    def __init__(self, name, team):
        super().__init__(name, team, [])

    def find_best_move(self, game):
        # get all moves for bot, moves is a 2d list[[from, to, dice], ]
        moves = game.get_all_moves()

        # choose random move
        move = random.randint(0, len(moves) - 1)
        return moves[move]

class Controller(object):
    """description of class"""
    # initialize current player to player 1, opponent to player 2, empty move, empty message, empty dice, empty board, call new game fxn 
    def __init__(self):
        self.mode = 0
        self.currentPlayer = None
        self.opponent = None
        self.move = [0, 0]
        self.message = ''
        self.dice = []
        self.board = []
        self.new_game()
        self.moveStack = []

    def debugger(self):
        print(f"current player: {self.currentPlayer.get_team_color()}")
        print(f"opponent player: {self.opponent.get_team_color()}")
        print(f"current moves: {self.move[0]} and {self.move[1]}")
        print(f"message: {self.message}")
        for i, val in enumerate(self.dice):
            print(f"dice {i+1}: {val}")

    # new game fxn, fills board with empty point objects 
    def new_game(self):
        # initialize board with 0 pieces per point
        self.board = []
        self.board = [0 for i in range(25)]

        # reset game attributes 
        self.mode = 0
        self.currentPlayer = None
        self.opponent = None
        self.move = [0, 0]
        self.message = ''
        self.dice = []
        
        # assigns starting points with their team and count 
        self.board[0] = None
        self.board[1] = -2
        self.board[12] = -5
        self.board[17] = -3
        self.board[19] = -5

        self.board[24] = 2
        self.board[13] = 5
        self.board[8] = 3
        self.board[6] = 5
    
    def printBoard(self):
        print('===========================================================================')

        # Show current dice (moves)
        id = 1
        for dice in self.dice:
            print(f'Dice {id}: {dice}')
            id += 1

        tempBoardTop = ''
        tempBoardBottom = ''
        count = 0

        for index in range(13, BOARD_SIZE + 1):
            if count == 6:
                tempBoardTop += '| | '
                tempBoardBottom += '| | '
            if self.board[index] >= 1:
                team = ''
            elif self.board[index] <= -1:
                team = '-'
            else:
                team = ''
            if self.board[25 - index] >= 1:
                team2 = ''
            elif self.board[25 - index] <= -1:
                team2 = '-'
            else:
                team2 = ''
            tempBoardTop += '( ' + team + str(self.board[index]) + ') '
            tempBoardBottom += '( ' + team2 + str(self.board[25 - index]) + ') '
            count += 1

        print(f'\n {tempBoardTop}\n')
        print(f'{tempBoardBottom}\n')
        print(f'{self.currentPlayer.get_team_color()} bar: {self.currentPlayer.get_bar()}')
        print(f'{self.opponent.get_team_color()} bar: {self.opponent.get_bar()}')

        print(f'\n{self.currentPlayer.get_team_color()} goal: {self.currentPlayer.get_goal()}')
        print(f'{self.opponent.get_team_color()} goal: {self.opponent.get_goal()}')
        print('===========================================================================')

    # dice functions 
    # Roll dice function, adds two more dice of the same value if doubles are rolled
    def roll_dice(self):
        self.dice.append(random.randint(1,6))
        self.dice.append(random.randint(1,6))
        if self.dice[0] == self.dice[1]:
            self.dice.append(self.dice[0])
            self.dice.append(self.dice[0])

    # Swap function, swaps dice for player
    def swap_dice(self):
        if len(self.dice) > 2 or len(self.dice) == 1:
            return
        temp = self.dice[1]
        self.dice[1] = self.dice[0]
        self.dice[0] = temp

    # If the bot is not using dice[0] to make its move, the dice needs to be removed and inserted back into 0 position, all controller functions assume dice[0] is being used 
    def update_dice(self, dice):
        if self.dice[0] != dice:
            self.dice.remove(dice)
            self.dice.insert(0, dice)

    # game controller functions 

            # function to find all possible unique moves for current gamestate
    def get_all_moves(self):

        all_moves = []
        # if the player has barred pieces don't check all From points, player can only move from bar 
        if self.currentPlayer.get_bar() > 0:
            opponent_home = self.opponent.get_home()
            # check if the player can move from bar with first dice 
            if self.board[opponent_home[self.dice[0]]] >= -1 and self.opponent.get_team() < 0 or self.board[opponent_home[self.dice[0]]] <= 1 and self.opponent.get_team() > 0:
                all_moves.append([0, self.opponent.get_home()[self.dice[0]], self.dice[0]])

            # check to see if there is another dice and if there is check if it is a valid move 
            if len(self.dice) > 1 and self.dice[0] != self.dice[1]:
                if self.board[opponent_home[self.dice[1]]] >= -1 and self.opponent.get_team() < 0 or self.board[opponent_home[self.dice[1]]] <= 1 and self.opponent.get_team() > 0:
                    all_moves.append([0, self.opponent.get_home()[self.dice[1]], self.dice[1]])

            return all_moves

        # get all moves available on board 
        fromPoints = [index for index in range(1, BOARD_SIZE + 1) if self.board[index] > 0 and self.currentPlayer.get_team() > 0 or self.board[index] < 0 and self.currentPlayer.get_team() < 0]

        # sentinel to track how dice checks
        check = 1
        while check:
            # for each point in the list 
            for point in fromPoints:
                toPoint = point - self.dice[0] * self.currentPlayer.get_team()
                # change To point to 25 if the dice moves the player to the goal 
                if toPoint <= 0 or toPoint >= 25:
                    toPoint = 25
                self.update_move(point, toPoint)
                # if the move is valid add the move to the all moves list 
                if self.check_move():
                    all_moves.append([point, toPoint, self.dice[0]])
                    continue

            # once we have iterated through all possible from positions using dice one, if there is only one dice or they are doubles, exit while loop
            if len(self.dice) == 1 or len(self.dice) > 2 or self.dice[0] == self.dice[1]:
                break
            else:
                if check == 1:
                    check += 1
                    self.swap_dice()
                else:
                    #swap dice back and break from while loop
                    self.swap_dice()
                    break

        self.message = ''
        return all_moves

    def isGameOver(self):
        return self.currentPlayer.get_goal() == NUM_PIECES or self.opponent.get_goal() == NUM_PIECES

    def get_winner(self):
        if self.currentPlayer.get_goal() == NUM_PIECES:
            return self.currentPlayer
        else:
            return self.opponent

    def get_loser(self):
        if self.currentPlayer.get_goal() == NUM_PIECES:
            return self.opponent
        else:
            return self.currentPlayer

    def update_move(self, fromPoint, toPoint):
        # check if the function is being called from collision point check loop
        if fromPoint == 25 or fromPoint == 26:
            self.move[0] = 0
        else:
            self.move[0] = fromPoint
        # check if the function is being called from collision point check loop
        if toPoint == 100:
            # if the player is bearing off the to point will be the dice value corresponding to opponent's home 
            if self.move[0] == 0:
                self.move[1] = self.opponent.get_home()[self.dice[0]]
            # if the player is trying to bear off 
            elif fromPoint - self.dice[0] * self.currentPlayer.get_team() > 24 or fromPoint - self.dice[0] * self.currentPlayer.get_team() < 1:
                self.move[1] = 25
            else:
                self.move[1] = fromPoint - self.dice[0] * self.currentPlayer.get_team()
        else:
            self.move[1] = toPoint

    # switch players after turn is over 
    def switch_players(self):
        temp = self.currentPlayer
        self.currentPlayer = self.opponent
        self.opponent = temp

    # returns if the player can bear off 
    def can_bear_off(self):
        # count all the pieces in the player's home 
        total = 0
        for i in self.currentPlayer.get_home():
            if i == 0:
                continue
            if self.board[i] > 0 and self.currentPlayer.get_team() > 0 or self.board[i] < 0 and self.currentPlayer.get_team() < 0:
                total += abs(self.board[i])
        if self.currentPlayer.get_goal() == 0:
            return total == NUM_PIECES
        else:
            totalCount = total + self.currentPlayer.get_goal()
            return totalCount == NUM_PIECES

    # returns if the player hit on their move 
    def check_hit(self):
        if self.board[self.move[1]] == self.opponent.get_team():
            return True

    def check_move(self, fromPoint = 0, toPoint = 0):
        # check if different From and To points were provided 
        if fromPoint == 0 and toPoint == 0:
            fromPoint = self.move[0]
            toPoint = self.move[1]

        # if the player has barred pieces but didn't try to move them 
        if fromPoint != 0 and self.currentPlayer.get_bar() > 0:
            self.message = ' has at least one barred piece'
            return False 

        # if the player doesn't have barred pieces but tried to move them 
        if fromPoint == 0 and self.currentPlayer.get_bar() == 0:
            self.message = ' does not have any barred pieces'
            return False

        # if the player is trying to bear off but can't
        if toPoint == 25 and not self.can_bear_off():
            self.message = ' cannot bear off'
            return False

        # final check to move from bar
        if fromPoint == 0:
            # have to check the position they are moving to is not occupied
                # by the opponent 
            # have to check the dice rolled allow that move 
            if self.board[toPoint] >= 2 and self.opponent.get_team() > 0 or self.board[toPoint] <= -2 and self.opponent.get_team() < 0:
                self.message = f' cannot move from bar to point {toPoint}. There are too many opponent piece there'
                return False
            elif toPoint not in self.opponent.get_home() or self.opponent.get_home().index(toPoint) != self.dice[0]:
                self.message = f' cannot move from bar to point {toPoint} with dice'
                return False
            else:
                return True
            
        # final check to bear off 
        if toPoint == 25:
            # if the player does not have pieces at from point 
            if self.board[fromPoint] <= 0 and self.currentPlayer.get_team() > 0 or self.board[fromPoint] >= 0 and self.currentPlayer.get_team() < 0:
                self.message = f' cannot bear off, does not have any pieces at point {fromPoint}'
                return False
            # if the dice does not allow it 
            elif self.currentPlayer.get_home().index(fromPoint) > self.dice[0]:
                self.message = ' cannot bear off, piece is too far from home'
                return False
            # if the dice allows it, but there are pieces in higher positions still
            elif self.currentPlayer.get_home().index(fromPoint) < self.dice[0]:
                for otherFromPoint in reversed(self.currentPlayer.get_home()):
                    if fromPoint == otherFromPoint:
                        return True
                    if self.board[otherFromPoint] > 0 and self.currentPlayer.get_team() > 0 or self.board[otherFromPoint] < 0 and self.currentPlayer.get_team() < 0:
                        self.message = ' cannot bear off, there are pieces in higher positions'
                        return False
            # else player can bear off
            else:
                return True
        # check for player making a regular move 
        # check the player has a piece at from point, the player is not moving backwards and the dice rolled allow move, and there isn't more than one opponent piece at the to point
        if self.board[fromPoint] <= 0 and self.currentPlayer.get_team() > 0 or self.board[fromPoint] >= 0 and self.currentPlayer.get_team() < 0:
            self.message = f' cannot move from point {fromPoint} to point {toPoint}. You have no pieces there'
            return False
        elif fromPoint - toPoint != self.dice[0] * self.currentPlayer.get_team():
            self.message = f' cannot move from point {fromPoint} to point {toPoint} using dice one'
            return False
        elif self.board[toPoint] <= -2 and self.opponent.get_team() < 0 or self.board[toPoint] >= 2 and self.opponent.get_team() > 0:
            self.message = f' cannot move from point {fromPoint} to point {toPoint}. There are too many opponent pieces there'
            return False
        else:
            return True

    def add_piece(self, point, team):
        self.board[point] += team

    def remove_piece(self, point, team):
        self.board[point] -= team

    # function to undo move on board by popping most recent move added to moveStack 
    def undo_move(self):
        self.message = ''

        # team, From point, To point, dice, hit 
        move = self.moveStack.pop()

        # get current and opponent player 
        cTeam = move[0]
        oTeam = 1 if move[0] == -1 else -1 

        # check if the move was bearing off 
        if move[2] == 25:
            # remove piece from player's goal 
            if self.currentPlayer.get_team() == cTeam:
                self.currentPlayer.remove_goal()
            else:
                self.opponent.remove_goal()
            # add piece back to from point
            self.add_piece(move[1], cTeam)
        # if the player is moving from bar or making a normal move
        else:
            # check if the player was moving from the bar 
            if move[1] == 0:
                # add piece back to bar 
                if self.currentPlayer.get_team() == cTeam:
                    self.currentPlayer.add_bar()
                else:
                    self.opponent.add_bar()
                # remove piece from To point 
                self.remove_piece(move[2], cTeam)
            # otherwise normal move 
            else:
                # add piece back to From point 
                self.add_piece(move[1], cTeam)
                # remove piece from To point
                self.remove_piece(move[2], cTeam)

            # check if there was a hit at the To point 
            if move[4]:
                # if there was a hit need to add opponent piece at point 
                self.add_piece(move[2], oTeam)
                # remove piece from opponent's bar 
                if self.currentPlayer.get_team() == cTeam:
                    self.opponent.remove_bar()
                else:
                    self.currentPlayer.remove_bar()

        # add dice back to list of dice 
        self.dice.insert(0, move[3])

    # function to make move on board 
    def make_move(self):
        self.message = ''

        # assign From point and To point variables
        fromPoint = self.move[0]
        toPoint = self.move[1]
        hit = False

        # if the player is bearing off, do not need to check for hit before making move
        if toPoint == 25:
            self.currentPlayer.add_goal() 
            self.remove_piece(fromPoint, self.currentPlayer.get_team())
            self.message = f' beared off from point {fromPoint}' 
        # if the player is moving from bar or making a normal move, first check for hit 
        else:
            if self.check_hit():
                hit = True
                self.opponent.add_bar()
                self.board[toPoint] = 0
                self.message = f' hit at point {toPoint}.'

            # if player is moving from bar 
            if fromPoint == 0:
                self.currentPlayer.remove_bar()
                self.add_piece(toPoint, self.currentPlayer.get_team())
                self.message += f' Moved from bar to point {toPoint} '
            # otherwise make regular move 
            else:
                team = self.currentPlayer.get_team()
                self.remove_piece(fromPoint, team)
                self.add_piece(toPoint, team)
                self.message += f' Moved from point {fromPoint} to point {toPoint}'

        # add move to the stack 
        self.moveStack.append([self.currentPlayer.get_team(), fromPoint, toPoint, self.dice[0], hit])

        # remove dice being used 
        self.dice.pop(0)

    # adjust dice based on available moves, does not return a value, but will clear the list of dice (moves) if there are no available moves, effectively ending the players turn 
    def adjust_dice(self):
        # check if the player has pieces on the bar 
        if self.currentPlayer.get_bar() > 0:
            # if the player has pieces on the bar, check if dice one allows player to move their piece from bar to position on board allowed by the dice 
            opponent_home = self.opponent.get_home()
            if self.board[opponent_home[self.dice[0]]] >= 2 and self.opponent.get_team() > 0 or self.board[opponent_home[self.dice[0]]] <= -2 and self.opponent.get_team() < 0:
                # if there is only one dice or the dice is doubles
                if len(self.dice) == 1 or len(self.dice) > 2:
                    self.message = f' only has one move: {self.dice[0]} this is not a valid move. Voiding turn'
                    self.dice.clear()
                    return
                # else if the player cannot move from the bar with their second dice
                elif self.board[opponent_home[self.dice[1]]] >= 2 and self.opponent.get_team() > 0 or self.board[opponent_home[self.dice[1]]] <= -2 and self.opponent.get_team() < 0:
                    self.message = f' has no valid moves, dice one: {self.dice[0]}, dice two: {self.dice[1]}. Voiding turn'
                    self.dice.clear()
                    return
                # else the player will have to use the second dice first 
                else:
                    self.swap_dice()
                    return 
            # else the player can move with their first dice 
            else:
                return

        # check if the player has any valid moves on the board 
        check = 1

        # find all points current player can move from 
        fromPoints = [index for index in range(1, BOARD_SIZE + 1) if self.board[index] > 0 and self.currentPlayer.get_team() > 0 or self.board[index] < 0 and self.currentPlayer.get_team() < 0]

        while check:
            # for each point in the list 
            for point in fromPoints:
                toPoint = point - self.dice[0] * self.currentPlayer.get_team()
                # change To point to 25 if the dice moves the player to the goal 
                if toPoint <= 0 or toPoint >= 25:
                    toPoint = 25
                self.update_move(point, toPoint)
                # if the move is valid add the move to the all moves list 
                if self.check_move():
                    self.message = ''
                    return

            # if we didn't return there were no valid moves using dice one, if there is only one dice or they are doubles, void turn 
            if len(self.dice) == 1 or len(self.dice) > 2 or self.dice[0] == self.dice[1]:
                self.message = f' only has one move: {self.dice[0]}, this is not a valid move. Voiding turn'
                self.dice.clear()
                return
            else:
                if check == 1:
                    check += 1
                    self.swap_dice()
                else:
                    self.message = f' has no valid moves, dice one: {self.dice[0]}, dice two: {self.dice[1]}. Voiding turn'
                    self.dice.clear()
                    return

class gameBoard(object):
    def __init__(self):
        pygame.init()
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

        # screen for game
        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Backgammon")

        # initialize board image 
        self.board_image = pygame.image.load("boardV2.jpg")
        self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))    
        
        self.point_coords = {1: (1324, 880), 2: (1220, 880), 3: (1118, 880), 4: (1016, 880), 5: (914, 880), 6: (812, 880), 7: (641, 880), 8: (539, 880), 9: (437, 880), 10: (335, 880), 11: (233, 880), 12: (131, 880), 13: (131,10), 14: (233, 10), 15: (335, 10), 16: (437, 10), 17: (539, 10), 18: (641, 10), 19: (812, 10), 20: (914, 10), 21: (1016, 10), 22: (1118, 10), 23: (1220, 10), 24: (1324, 10), 25: (727, 400), 26: (727, 500), 27: (1436, 28), 28: (1436, 860), 29: (756, 425), 30: (756, 525)}
        self.all_pieces = pygame.sprite.Group()
        self.smallFont = pygame.font.SysFont(None, 25)
        self.collisionCheck = []

    def draw_text(self, info):
        # create white box to display info
        box = pygame.Surface((500, 300))
        box.fill((255, 255, 255))  # fill with white color
        box_rect = box.get_rect(center=(self.width/2, self.height/2))

        # split text into separate lines 
        words = info.split()
        renderList = []
        tempStr = ''
        for word in words:
            if has_punctuation(word):
                tempStr += word
                tempObj = self.smallFont.render(tempStr, True, (0, 0, 0))
                renderList.append(tempObj)
                tempStr = ''
                continue
            tempStr += word + ' '
        tempObj = self.smallFont.render(tempStr, True, (0, 0, 0))
        renderList.append(tempObj)
        
        # blit background and box 
        self.screen.blit(self.board_image, (0, 0))
        self.screen.blit(box, box_rect)

        for i, sentence in enumerate(renderList):
            sentence_rect = sentence.get_rect()
            sentence_rect.center = box_rect.center
            sentence_rect.move_ip(0, 20 * i - 100)
            self.screen.blit(sentence, sentence_rect)
            
        pygame.display.flip()

    def draw_screen(self, game):
        print("\n~~~~~~~~~~~~~~~~\n")
        # clear group of pieces
        self.all_pieces.empty()

        # get which player is white and black 
        if game.currentPlayer.get_team() == 1:
            p1 = game.currentPlayer
            p2 = game.opponent
        else:
            p1 = game.opponent
            p2 = game.currentPlayer

        # get game message and player's turn 
        self.draw_turn(game)

        # iterate through board and create sprite for each piece on board and an underlying rect object to check for collisions when the player has to enter their move 
        for point in range(1, 25):
            # draw underlying rect and add to list to check for collisions 
            width = 70
            height = 70
            rect = pygame.Rect(self.point_coords[point][0], self.point_coords[point][1], width, height)
            self.collisionCheck.append(rect)

            # draw pieces on board 
            if game.board[point] != 0:
                for eachPiece in range(abs(game.board[point])):
                    coords = list(self.point_coords[point])
                    if point >= 13:
                        coords[1] += eachPiece * 40
                    else:
                        coords[1] -= eachPiece * 40
                    # get team color
                    piece = Piece(game.board[point], coords)
                    self.all_pieces.add(piece)
        # need to add two rect objects for the bar positions and the dice 
        rect = pygame.Rect(727, 400, 70, 70)
        self.collisionCheck.append(rect)
        rect = pygame.Rect(727, 500, 70, 70)
        self.collisionCheck.append(rect)
        rect = pygame.Rect(914, 450, 50, 50)
        self.collisionCheck.append(rect)

        # create sprite for pieces on bar 
        if p1.get_bar() > 0:
            piece = Piece(p1.get_team(), self.point_coords[25])
            self.all_pieces.add(piece)     
            text = gameText(p1.get_bar(), self.point_coords[29], 30)
            self.all_pieces.add(text)
        if p2.get_bar() > 0:
            piece = Piece(p2.get_team(), self.point_coords[26])
            self.all_pieces.add(piece)
            text = gameText(p2.get_bar(), self.point_coords[30], 30, (255, 255, 255))
            self.all_pieces.add(text)

        # create sprite for pieces in goal 
        if p1.get_goal() > 0:
            for piece in range(p1.get_goal()):
                coords = list(self.point_coords[28])
                coords[1] -= piece * 25
                piece = Piece(p1.get_team(), coords)
                self.all_pieces.add(piece)
        if p2.get_goal() > 0:
            for piece in range(p2.get_goal()):
                coords = list(self.point_coords[27])
                coords[1] += piece * 25
                piece = Piece(p2.get_team(), coords)
                self.all_pieces.add(piece)

        # draw underlying rect objects and draw board background on top 
        for obj in self.collisionCheck:
            pygame.draw.rect(self.screen, (0, 0, 0), obj, 3)
        self.screen.blit(self.board_image, (0, 0))

        # draw dice 
        font = pygame.font.SysFont(None, 45, True)
        boX = 914
        boY = 450
        for move in game.dice:
            box = pygame.Surface((50, 50))
            box.fill((255, 255, 255))  # fill with white color
            box_rect = box.get_rect()
                
            text = font.render(str(move), True, (0, 0, 0))
            self.screen.blit(box, (boX, boY))
            self.screen.blit(text, (boX + 15, boY + 14))
            rect = pygame.Rect(boX, boY, 50, 50)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 4)
            boX += 100

        # draw all pieces
        self.all_pieces.draw(self.screen)
        pygame.display.flip()

    def get_name(self, player):
        # create white box to display info
        box = pygame.Surface((500, 300))
        box.fill((255, 255, 255))  # fill with white color
        box_rect = box.get_rect(center=(self.width/2, self.height/2))

        # set up the text input
        input_box = pygame.Rect(0, 0, 140, 32)
        input_box.center = box_rect.center
        text = ''
        active = False
        color = pygame.Color('lightskyblue3')

        # loop to get player name
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        # toggle the active variable
                        active = not active
                    else:
                        active = False
                    # change the current color of the input box
                    color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            # store the entered name and exit the loop
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            # render the white background box
            self.screen.blit(box, box_rect)
            # render the text to tell user to enter name 
            font = pygame.font.SysFont(None, 30, True)
            instruction = font.render(player + " player name: ", True, (0, 0, 0), )
            instruct_rect = instruction.get_rect()
            instruct_rect.center = box_rect.center
            instruct_rect.move_ip(0, -50)
            self.screen.blit(instruction, instruct_rect)
            # render input box 
            pygame.draw.rect(self.screen, color, input_box)
            txt_surface = self.smallFont.render(text, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            
            pygame.display.flip()

        return text

    # intro function to display introduction information and set game.mode, game.opponent, and game.currentPlayer
    def intro(self, game):
        # create text to display
        message = 'Welcome to the wonderful game of Backgammon! Press enter to continue'

        # call function to display text 
        self.draw_text(message)

        # create loop to display intro text until user presses enter 
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False

        # get gamemode
        message = 'Please select gamemode: Enter 1 for Two player. Enter 2 for One player.'
        self.draw_text(message)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == '1':
                        game.mode = 1
                        running = False
                    elif event.unicode == '2':
                        game.mode = 2
                        running = False

        # return user's selection
        message = 'One player selected. Press enter to continue' if game.mode == 2 else 'Two player selected. Press enter to continue'
        self.draw_text(message)
        # create loop to display text until user presses enter 
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False

        # create players 
        # if the user chose one player 
        if game.mode == 2:
            pTwo = default_bot('Salami Bot', -1)
            pOneName = self.get_name("White")
            pOne = Player(pOneName, 1)
        # if the user chose two player 
        else:
            pOneName = self.get_name("White")
            pOne = Player(pOneName, 1)
            pTwoName = self.get_name("Black")
            pTwo = Player(pTwoName, -1)

        # get who moves first
        game.roll_dice()
        if game.dice[0] >= game.dice[1]:
            message = "White moves first"
            messageObj = gameText(message, (0,0), 15)
            game.currentPlayer = pOne
            game.opponent = pTwo
        else:
            message = "Black moves first"
            messageObj = gameText(message, (0,0), 15)
            game.currentPlayer = pTwo
            game.opponent = pOne
        game.dice.clear()

        # draw images to screen
        self.screen.blit(self.board_image, (0, 0))
        self.all_pieces.draw(self.screen)
        pygame.display.flip()

    def draw_turn(self, game):
        yCoord = 440
        if game.message:
            # if there is a game message check if the text is too long for one line (we know there will be two lines max)
            words = game.message.split()
            renderList = []
            tempStr = ' '
            for word in words:
                if '.' in word:
                    tempStr += word
                    renderList.append(tempStr)
                    tempStr = ''
                    continue
                tempStr += word + ' '
            renderList.append(tempStr)

            if len(renderList) > 1:
                message = gameText(renderList[1], (133, yCoord), 30)
                yCoord -= 40
                self.all_pieces.add(message)
            message = gameText(game.currentPlayer.get_name() + renderList[0], (133, yCoord), 30)
            self.all_pieces.add(message)
        tempTurn = game.currentPlayer.get_name() + "\'s turn"
        turn = gameText(tempTurn, (133, 480), 45, (0, 0, 0), True)
        self.all_pieces.add(turn)

def regular():
    # create instance of controller to run game and gameBoard to display game
    board = gameBoard()
    game = Controller()

    # call intro function to get game mode and create players
    board.intro(game)

    # while the game is not over keep switching players 
    while not game.isGameOver():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # roll the dice
        game.roll_dice()

        # adjust dice 
        game.adjust_dice()

        # print board 
        board.draw_screen(game)
        game.debugger()

        # while there is still a move available and the game is not over 
        while len(game.dice) > 0 and not game.isGameOver():
            # if it is two player mode or it is one player mode and the current player is the user 
            if game.mode == 1 or game.mode == 2 and game.currentPlayer.get_team() == 1:
                # while the player still needs to enter a valid move 
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                pos = pygame.mouse.get_pos()
                                # iterate through collision objects to check player's click
                                for point, obj in enumerate(board.collisionCheck):
                                    # if there is a collision 
                                    if obj.collidepoint(pos):
                                        # check if the player clicked the dice to switch the order 
                                        if point == 26:
                                            game.swap_dice()
                                            board.draw_screen(game)
                                            break
                                        # update the move, using 100 as a sentinel to tell the function to figure out where the player is trying to go 
                                        game.update_move(point + 1, 100)
                                        # if the move is valid 
                                        if game.check_move():
                                            # make the move and remove the dice that was used 
                                            game.make_move()
                                            # redraw screen 
                                            board.draw_screen(game)
                                            game.message = ''
                                            # switch sentinel
                                            running = False
                                            # adjust dice 
                                            if len(game.dice) != 0:
                                                game.adjust_dice()
                                            # break out of loop 
                                            break 
                                        # if the move was not valid, redraw board with error message, break out of collide point check loop, player needs to enter another move 
                                        board.draw_screen(game)
                                        game.message = ''
                                        break 
            # else it is one player and it is the bot's turn 
            else:
                # slow the game so player can see computer's moves
                sleep(2)

                # calls bot functions to find move
                game.currentPlayer.turn(game)

                # make move and remove the dice used to make that move 
                game.make_move()

                # print board and reset game message 
                board.draw_screen(game)
                game.message = ''

                # slow the game so player can see computer's moves
                sleep(1)

                if len(game.dice) != 0:
                    game.adjust_dice()

        # Display result of player's turn if adjustDice found there is no available moves for player 
        if len(game.message) > 0 and not game.isGameOver():
            board.draw_screen(game)
            game.message = ''
        sleep(2)

        # Switch players 
        game.switch_players()

    # Display winner
    winner = game.get_winner()
    board.draw_text(winner.get_name() + ' is the winner!')
    sleep(5)

def testing(iters):
    # visualize game
    #board = gameBoard()

    # create dic to hold wins
    player_wins = {
        'Smarty Pance' : 0,
        'Dumbo' : 0}

    # create instance of game controller 
    game = Controller()

    # create two bots to play
    p1 = default_bot('Smarty Pance', 1)
    p2 = default_bot('Dumbo', -1)

    for i in range(iters):
        # reset game 
        game.new_game()

        # reset players goals, bars, and teams
        choose_team = [1, -1]
        team1 = random.choice(choose_team)
        team2 = 1 if team1 == -1 else -1
        p1.reset(team1)
        p2.reset(team2)

        # decide who goes first
        first_turn = random.choice(choose_team)
        if first_turn == 1:
            game.currentPlayer = p2
            game.opponent = p1
        else:
            game.currentPlayer = p1
            game.opponent = p2

        # while the game is not over keep switching players 
        while not game.isGameOver():

            #for event in pygame.event.get():
            #    if event.type == pygame.QUIT:
            #        running = False

            # roll the dice
            game.roll_dice()
            #board.draw_screen(game)

            # adjust dice 
            game.adjust_dice()

            # debugging 
            #game.debugger()

            # while there is still a move available and the game is not over 
            while len(game.dice) > 0 and not game.isGameOver():

                # get move 
                game.currentPlayer.turn(game)

                # wait for user to press enter 
                #running = True
                #while running:
                #    for event in pygame.event.get():
                #        if event.type == pygame.QUIT:
                #            pygame.quit()
                #            sys.exit()
                #        elif event.type == pygame.KEYDOWN:
                #            if event.key == pygame.K_RETURN:
                #                running = False

                # make move and remove the dice that was used 
                game.make_move()

                # debugging
                #print(f'{game.message}')
                #game.printBoard()
                
                # print board and reset game message 
                #board.draw_screen(game)
                #game.message = ''

                # check if number of pieces is correct 
                #wPieces = sum(game.board[i].get_count() for i in range(1, BOARD_SIZE + 1) if game.board[i].get_team() == 1)
                #bPieces = sum(game.board[i].get_count() for i in range(1, BOARD_SIZE + 1) if game.board[i].get_team() == -1)
                #if game.currentPlayer.get_team() == 1:
                #    wPieces += game.currentPlayer.get_goal()
                #    bPieces += game.opponent.get_goal()
                #else:
                #    bPieces += game.currentPlayer.get_goal()
                #    wPieces += game.opponent.get_goal()
                #if bPieces > NUM_PIECES or wPieces > NUM_PIECES:
                #    print(f'White pieces: {wPieces}\nBlack pieces: {bPieces}')
                #    raise ValueError('Error')
                # wait for user to press enter 
                    #running = True
                    #while running:
                    #    for event in pygame.event.get():
                    #        if event.type == pygame.QUIT:
                    #            pygame.quit()
                    #            sys.exit()
                    #        elif event.type == pygame.KEYDOWN:
                    #            if event.key == pygame.K_RETURN:
                    #                running = False

                if len(game.dice) != 0:
                    game.adjust_dice()

            # Switch players 
            game.switch_players()

        # Get winner and loser, returns Player object of winner
        #print(f'Team: {game.currentPlayer.get_team()}    Goals: {game.currentPlayer.get_goal()}')
        #print(f'Team: {game.opponent.get_team()}    Goals: {game.opponent.get_goal()}')
        winner = game.get_winner()
        loser = game.get_loser()

        # Calculate score 
        score = 1
        #if loser.get_goal() == 0:
        #    score += 1

        # Update player's overall score 
        player_wins[winner.get_name()] += score
        #print(f'{winner.get_name()} is the winner')
    # Get last values for h0, h1, h2, h3
    hVals = p1.get_hVals()

    for p, v in player_wins.items():
        print(p + ": " + str(v))

    return player_wins, hVals

import cProfile
import pstats

cProfile.run('testing(1000)', 'stats')
p = pstats.Stats('stats')
p.sort_stats('time').print_stats(10)
#regular()

# calculate the gradient of the scoring function with respect to each weight 
def calculate_gradient():
    # there are four heuristics for the scoring function. Use a for loop with x number of iterations to evaluate the gradient score of each individual weight at increments of 0.01 from 0 to 100
    iterations = 10
    optimal_weights = [0, 0, 0, 0]

    # for each of the four different heuristics 
    for heuristic in range(4):
        # initialize the weight stack with integers and the increment to 0
        weight_stack = [1, 1, 1, 1]
        increment = 0
        total = 0
        max_score = 0

        # insert increment variable into weight_stack in the subsequent heuristic position
        weight_stack.insert(heuristic, increment)

        # remove last item in weight_stack
        weight_stack.pop()
        
        for each_weight in range(0, 101):
            # call function to simulate games
            wins = testing(iterations, weight_stack)

            # increase increment by 0.01
            increment += 0.01

            # get salami bot's score for number of iterations (how many games it won)
            score = wins['Smarty Pance']

            # add actual score/maximum score to accumulator, i.e. how the bot performed with this given weight
            total += score / 20 * 100

            # update optimal weight
            if score > max_score:
                max_score = score
                optimal_weights[heuristic] = increment

        # average the bots performance with each different weight 
        print(f'Gradient for heuristic {heuristic}: {total / 101}')

    # print optimal gradients
    print(f'{optimal_weights}')

#calculate_gradient()

def optimization(alpha, new_weights, y_true, depth):
    # search depth limit reached 
    if depth == 0:
        return 'Done'

    # iterations
    iterations = 100

    # Predict 
        # evaluate weights and calculate win percentage 
    wins, hVals = testing(iterations, new_weights)
    new_score = wins['Smarty Pance']
    y_pred = round(new_score / 100 * 100, 2)

    # outcome of previous optimization
    print(f'\nNew Win Rate: {y_pred}\nNew weights: {new_weights}\n')

    # mse loss
        # loss fxn, change is positive if the win rate improved compared to y_pred
    mse = (y_true - y_pred)**2
    print(f'MSE: {mse}\n')

    # gradient(x1, x2, x3, x4, y_true, y_pred)
    dL_dw0 = (2/iterations) * ((y_pred - y_true) * hVals[0])
    print(f'dL_dw0: {dL_dw0}\n')

    # update_weights
    new_weights[0] = round((new_weights[0] - alpha * dL_dw0), 2)

    # after optimization
    print(f'\nRe-optimized weights: {new_weights}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # call function again
    optimization(alpha, new_weights, 100, depth - 1)

#learning_rate = 0.01
#w = optimization(learning_rate, [0.50, 1, 1, 1], 100, 100)
#print(w)