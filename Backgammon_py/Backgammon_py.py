import random

# Constants for game board size and number of pieces
BOARD_SIZE = 24
NUM_PIECES = 15

# Player class 
class Player:
    def __init__(self):
        self.__color = 'WHITE'

    # Function to switch current player 
    def switch(self):
        if self.__color == 'WHITE':
            self.__color = 'BLACK'
        else:
            self.__color = 'WHITE'
    
    # Function to print player color when print() is called on instance of class
    def __str__(self):
        return self.__color

    # Function to return current player 
    def __eq__(self, other):
        return self.__color == other

    # Reset player 
    def newGame(self):
        self.__color = 'WHITE'

# diceRoll class 
class diceRoll:
    def __init__(self):
        self._diceNums = []
    
    # Roll dice function, adds two more dice of the same value if doubles are rolled
    def rollDice(self):
        self._diceNums.append(random.randint(1,6))
        self._diceNums.append(random.randint(1,6))
        if self._diceNums[0] == self._diceNums[1]:
            self._diceNums.append(self._diceNums[0])
            self._diceNums.append(self._diceNums[0])
    
    # Swap function, swaps dice for player
    def swap(self):
        if len(self._diceNums) > 2 or len(self._diceNums) == 1:
            return
        temp = self._diceNums[1]
        self._diceNums[1] = self._diceNums[0]
        self._diceNums[0] = temp

# gameState class
class gameState:
    def __init__(self):
        self.__board = [0] * 24
        self.__move = [0] * 2
        self.__whiteBar = 0
        self.__blackBar = 0
        self.__whiteGoal = 0
        self.__blackGoal = 0
        self.__message = ''
        self.__currentPlayer = Player()
        self.__dice = diceRoll()
    
    def initGame(self):
        for i in range(BOARD_SIZE):
            self.__board[i] = 0
        
        self.__board[0] = 2
        self.__board[11] = 5
        self.__board[16] = 3
        self.__board[18] = 5

        self.__board[23] = -2
        self.__board[12] = -5
        self.__board[7] = -3
        self.__board[5] = -5

        self.__whiteBar = 0
        self.__whiteGoal = 0
        self.__blackBar = 0
        self.__blackGoal = 0

        self.__currentPlayer.newGame()

    def update_move(self, fromPoint, toPoint):
        self.__move[0] = fromPoint
        self.__move[1] = toPoint

    def printBoard(self):
        print('===========================================================================')

        # Show current dice (moves)
        id = 1
        for dice in self.__dice._diceNums:
            print('Dice ' + str(id) + ': ' + str(dice))
            id += 1

        tempBoardTop = ''
        tempBoardBottom = ''
        count = 0

        for index in range(12, BOARD_SIZE):
            if count == 6:
                tempBoardTop += '| | '
                tempBoardBottom += '| | '
            tempBoardTop += '( ' + str(self.__board[index]) + ') '
            tempBoardBottom += '( ' + str(self.__board[23 - index]) + ') '
            count += 1

        print('\n' + tempBoardTop + '\n')
        print(tempBoardBottom + '\n')
        print('White Bar: ' + str(self.__whiteBar))
        print('Black Bar: ' + str(self.__blackBar))

        if self.__whiteGoal or self.__blackGoal:
            print('\nWhite Goal: ' + str(self.__whiteGoal))
            print('Black Goal: ' + str(self.__blackGoal))
        print('===========================================================================')

    def isGameOver(self):
        return self.__whiteGoal == NUM_PIECES or self.__blackGoal == NUM_PIECES

    def getWinner(self):
        if self.__whiteGoal == NUM_PIECES:
            return 'WHITE'
        else:
            return 'BLACK'

    def canBearOff(self):
        total = 0
        if self.__currentPlayer == 'WHITE':
            if self.__whiteGoal:
                return True
            for i in range(6):
                if self.__board[i] < 0:
                    total+=abs(self.__board[i])
        else:
            if self.__blackGoal:
                return True
            for i in range(6):
                if self.__board[i] > 0:
                    total+=abs(self.__board[i])
        return total == NUM_PIECES

    def checkMove(self):
        # If the player has barred pieces but didn't try to move them 
        if self.__move[0] != -1 and self.__currentPlayer == 'WHITE' and self.__whiteBar or \
            self.__move[0] != -1 and self.__currentPlayer == 'BLACK' and self.__blackBar:
            self.__message = ' has at least one barred piece'
            return False

        # If the player doesn't have barred pieces but tried to move them 
        if self.__move[0] == -1 and self.__currentPlayer == 'WHITE' and not self.__whiteBar or \
            self.__move[0] == -1 and self.__currentPlayer == 'BLACK' and not self.__blackBar:
            self.__message = ' does not have any barred pieces'
            return False

        # If the player is trying to bear off but can't
        if self.__move[1] == 24 and not self.canBearOff():
            self.__message = ' cannot bear off'
            return False

        # If the player is trying to move from bar but can't 
        if self.__currentPlayer == 'WHITE' and self.__move[0] == -1:
            if self.__board[self.__move[1]] > 1 or BOARD_SIZE - self.__move[1] != self.__dice._diceNums[0]:
                self.__message = ' cannot move from bar to point ' + str(self.__move[1] + 1)
                return False
        if self.__currentPlayer == 'BLACK' and self.__move[0] == -1:
            if self.__board[self.__move[1]] < -1 or self.__move[1] + 1 != self.__dice._diceNums[0]:
                self.__message = ' cannot move from bar to point ' + str(self.__move[1] + 1)
                return False

        # If the player is trying to bear off but can't 
        if self.__currentPlayer == 'WHITE' and self.__move[1] == 24:
            if self.__move[0] + 1 > self.__dice._diceNums[0] or self.__board[self.__move[0]] > -1:
                self.__message = ' cannot bear off from here, the piece is too far from home or you have no pieces at point ' + str(self.__move[0] + 1)
                return false
            elif self.__move[0] + 1 < self.__dice._diceNums[0]:
                for i in range(self.__move[0] + 1, 6):
                    if self.__board[i] < 0:
                        self.__message = ' cannot bear off from point ' + str(self.__move[0] + 1) + ' there are pieces in higher positions in your home'
                        return False
        if self.__currentPlayer == 'BLACK' and self.__move[1] == 24:
            if 24 - self.__move[0] > self.__dice._diceNums[0] or self.__board[self.__move[0]] < 1:
                self.__message = ' cannot bear off from here, the piece is too far from home or you have no pieces at point ' + str(self.__move[0] + 1)
                return false
            elif 24 - self.__move[0] < self.__dice._diceNums[0]:
                for i in range(self.__move[0] - 1, 17, -1):
                    if self.__board[i] > 0:
                        self.__message = ' cannot bear off from point ' + str(self.__move[0] + 1) + ' there are pieces in higher positions in your home'
                        return False

        # If the player is trying to move (not from bar or bear off) and can't
        if self.__move[0] != -1 and self.__move[1] != 24:
            if self.__currentPlayer == 'WHITE':
                if self.__board[self.__move[0]] > -1 or self.__board[self.__move[1]] > 1 or self.__move[0] - self.__move[1] != self.__dice._diceNums[0]:
                    self.__message = ' cannot move from point ' + str(self.__move[0] + 1) + ' to point ' + str(self.__move[1] + 1)
                    return False
            else:
                if self.__board[self.__move[0]] < 1 or self.__board[self.__move[1]] < -1 or self.__move[0] - self.__move[1] != self.__dice._diceNums[0] * -1:
                    self.__message = ' cannot move from point ' + str(self.__move[0] + 1) + ' to point ' + str(self.__move[1] + 1)
                    return False

        # If the function has not returned the move is valid, check if there is a hit if the player is not bearing off
        if self.__move[1] != 24 and self.__currentPlayer == 'WHITE':
            if self.__board[self.__move[1]] == 1:
                self.__blackBar += 1
                self.__board[self.__move[1]] -= 1
                print('WHITE hit at point ' + str(self.__move[1] + 1))
        if self.__move[1] != 24 and self.__currentPlayer == 'BLACK':
            if self.__board[self.__move[1]] == -1:
                self.__whiteBar += 1
                self.__board[self.__move[1]] += 1
                print('BLACK hit at point ' + str(self.__move[1] + 1))

        # Make move
        # If the player is moving from bar 
        if self.__move[0] == -1:
            if self.__currentPlayer == 'WHITE':
                self.__whiteBar -= 1
                self.__board[self.__move[1]] -= 1
                self.__message = ' moved from bar to point ' + str(self.__move[1] + 1)
            else:
                self.__blackBar -= 1
                self.__board[self.__move[1]] += 1
                self.__message = ' moved from bar to point ' + str(self.__move[1] + 1)
        # If the player is bearing off
        elif self.__move[1] == 24:
            if self.__currentPlayer == 'WHITE':
                self.__whiteGoal += 1
                self.__board[self.__move[0]] += 1
                self.__message = ' beared off from point ' + str(self.__move[0] + 1)
            else:
                self.__blackGoal += 1
                self.__board[self.__move[0]] -= 1
                self.__message = ' beared off from point ' + str(self.__move[1] + 1)
        # Otherwise it is a normal move 
        else:
            if self.__currentPlayer == 'WHITE':
                self.__board[self.__move[0]] += 1
                self.__board[self.__move[1]] -= 1
                self.__message = ' moved from point ' + str(self.__move[0] + 1) + ' to point ' + str(self.__move[1] + 1)
            else:
                self.__board[self.__move[0]] -= 1
                self.__board[self.__move[1]] += 1
                self.__message = ' moved from point ' + str(self.__move[0] + 1) + ' to point ' + str(self.__move[1] + 1)
        return True

    # Adjust dice based on available moves, called before the player enters their move 
    def adjustDice(self):
        # If the player cannot enter their piece(s) from the bar 
        if self.__currentPlayer == 'WHITE' and self.__whiteBar:
            # If the player cannot enter their piece from the bar with dice one
            if self.__board[BOARD_SIZE - self.__dice._diceNums[0]] >= 2:
                # If the player only has one dice or the dice is doubles 
                if len(self.__dice._diceNums) == 1 or len(self.__dice._diceNums) > 2:
                    self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                    self.__dice._diceNums.clear()
                    return
                # If the player cannot move from the bar with the dice two either 
                elif self.__board[BOARD_SIZE - self.__dice._diceNums[1]] >= 2:
                    self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                    self.__dice._diceNums.clear()
                    return
                # Otherwise the player will have to use dice two to move first 
                else:
                    self.__dice.swap()
                    return
            # Otherwise the player can move with dice one 
            return
        # If the player cannot enter their piece(s) from the bar (BLACK)
        if self.__currentPlayer == 'BLACK' and self.__blackBar:
            if self.__board[self.__dice._diceNums[0] - 1] <= -2:
                if len(self.__dice._diceNums) == 1 or len(self.__dice._diceNums) > 2:
                    self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                    self.__dice._diceNums.clear()
                    return
                elif self.__board[self.__dice._diceNums[1] - 1] <= -2:
                    self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                    self.__dice._diceNums.clear()
                    return
                else:
                    self.__dice.swap()
                    return
            return

        # If the player has no barred pieces but can't move any of their pieces (excluding bearing off)
        if self.__currentPlayer == 'WHITE' and not self.canBearOff():
            # Find all points player can move from 
            froms = []
            for point in range(24):
                if self.__board[point] < 0:
                    froms.append(point)
            # For the points that the player can move from 
            for point in froms:
                # If moving from the "point" using dice one is out of range of the board continue
                if point - self.__dice._diceNums[0] < 0:
                    continue
                else:
                    if self.__board[point - self.__dice._diceNums[0]] < 2:
                        return

            # If we didn't return that means there are no valid moves using dice one 
            # If there is only one dice or the dice is doubles
            if len(self.__dice._diceNums) == 1 or len(self.__dice._diceNums) > 2:
                self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                self.__dice._diceNums.clear()
                return

            # If there is more than one dice (excluding doubles) check if there are valid moves using dice two, if there is, swap() the dice, the player will have to use dice two first 
            for point in froms:
                if point - self.__dice._diceNums[1] < 0:
                    continue
                else:
                    if self.__board[point - self.__dice._diceNums[1]] < 2:
                        self.__dice.swap()
                        return

            # If we didn't return that means there are no valid moves using dice one or two
            self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
            self.__dice._diceNums.clear()
            return
        # If the player has no barred pieces but can't move any of their pieces (BLACK)
        if self.__currentPlayer == 'BLACK' and not self.canBearOff():
            froms = []
            for point in range(24):
                if self.__board[point] > 0:
                    froms.append(point)
            for point in froms:
                if point + self.__dice._diceNums[0] > 23:
                    continue
                else:
                    if self.__board[point + self.__dice._diceNums[0]] > -2:
                        return
            if len(self.__dice._diceNums) == 1 or len(self.__dice._diceNums) > 2:
                self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
                self.__dice._diceNums.clear()
                return
            for point in froms:
                if point + self.__dice._diceNums[1] > 23:
                    continue
                else:
                    if self.__board[point + self.__dice._diceNums[1]] > -2:
                        self.__dice.swap()
                        return
            self.__message += '~ has no valid moves, voiding turn, diceOne: ' + str(self.__dice._diceNums[0]) + ' diceTwo: ' + str(self.__dice._diceNums[1])
            self.__dice._diceNums.clear()
            return
        return

    def playGame(self):
        # Display game information
        print('Welcome to the wonderful game of Backgammon!\n1. from = 0 to move from bar\n2. to = 25 to bear off\n3. from = -2 to swap dice\n')

        # While the game is not over keep switching players 
        while not self.isGameOver():
            # Roll the dice
            self.__dice.rollDice()

            # Check to make sure the player has possible moves
            self.adjustDice()

            # While there is still a move available and the game is not over 
            while len(self.__dice._diceNums) > 0 and not self.isGameOver():
                # Print the board
                self.printBoard()

                # Create variables for the player's move (from, to)
                fromPoint = -5
                toPoint = 0

                # While the player has entered values that are out of range prompt them for their move 
                while fromPoint < -1 or fromPoint > 23 or toPoint < 0 or toPoint > 25:
                    print('from = -3 to view game information\n\n' + '> ' + str(self.__currentPlayer) + '\'s turn <')
                    fromPoint = int(input('Enter the point you want to move from: '))
                    toPoint = int(input('Enter the point you want to move to: '))
                    if fromPoint == -2:
                        self.__dice.swap()
                        print('\nThe dice have been swapped, please enter your move:\nDice One: ' + str(self.__dice._diceNums[0]) + '\nDice Two: ' + str(self.__dice._diceNums[1]) + '\n\n')
                    elif fromPoint == -3:
                        print('1. from = 0 to move from bar\n2. to = 25 to bear off\n3. from = -2 to swap dice')
                    fromPoint -= 1
                    toPoint -= 1

                # Update current move 
                self.__move[0] = fromPoint
                self.__move[1] = toPoint

                # If the move is valid, remove dice (move) from diceNums and check to make sure the player 
                    # still has a valid move 
                if self.checkMove():
                    self.__dice._diceNums.pop(0)
                    if len(self.__dice._diceNums) != 0:
                        self.adjustDice()

                # Display result of player's move, clear message 
                print('\n' + str(self.__currentPlayer) + self.__message)
                self.__message = ''

            # Display result of player's turn if adjustDice found there is no available moves for player 
            if len(self.__message) != 0:
                print('\n' + str(self.__currentPlayer) + self.__message)

            # Switch players 
            self.__currentPlayer.switch()

        # When the game is over, print the board one last time
        self.printBoard()

        # Display winner
        print(self.getWinner() + ' is the winner!')

# Runner 
game = gameState()
game.initGame()
game.playGame()