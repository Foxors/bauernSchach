import random
from time import sleep
import pyxel


class Bot:
    def make_move(self, board, options):
        rng = random.randint(0, len(options)-1)
        return options[rng]

    def lost(self):
        pass

    def won(self):
        pass


class Game:
    def __init__(self, width, height, bots):
        self.width = width;
        self.height = height;

        self.bots = bots # count of bots 0, 1 or 2
        self.timer = 0

        self.resset()

        pyxel.init(8*width+8*2, 8*height+8*2)
        pyxel.load("assets.pyxres")
        pyxel.run(self.update, self.draw)


    def init_bot(self):
        self.bot = Bot()
        self.bot2 = Bot()


    def resset(self):
        self.board = [[' ' for x in range(self.width)] for y in range(self.height)] 

        for x in range(self.width):
            self.board[0][x] = 'A'
            self.board[self.height-1][x] = 'B'

        self.BauerCountA = len(self.board[0])
        self.BauerCountB = len(self.board[0])

        self.currentlyPlaying = 'A'
        self.winner = ' '

        self.timer = 0

        self.selectedPos = []

        self.init_bot()


    def move(self, x1: int, y1: int, x2: int, y2: int):
        if (x1 < 0 or x1 >= self.width or
            y1 < 0 or y1 >= self.height or
            x2 < 0 or x2 >= self.width or
            y2 < 0 or y2 >= self.height):
            return False

        # Remove one bauer from player
        if (self.board[y2][x2] == 'A'): self.BauerCountA -= 1
        if (self.board[y2][x2] == 'B'): self.BauerCountB -= 1

        # Update board
        self.board[y2][x2] = self.board[y1][x1]
        self.board[y1][x1] = ' ';

        return True


    def available_moves(self, player: str):
        availableMoves = []

        for y in range(0, self.height):
            for x in range(0, self.width):
                bauer = self.board[y][x]

                if (player == bauer):
                    # Go through every move this bauer can do
                    for offsetX in range(-1, 2, 1):
                        # Figure out world coordinats
                        posX = x + offsetX;
                        posY = y;

                        # move up or down depending on player
                        if (player == 'A'):
                            posY += 1;
                        else:
                            posY -= 1;

                        # Check if on grid
                        if (posX < 0 or posX >= self.width or
                            posY < 0 or posY >= self.height):
                            continue

                        # Check if would bump into team mate
                        if (self.board[posY][posX] == player):
                            continue

                        # Check if bump into other bauer only when walking straight
                        # Or if there are bauers to capture on the sides
                        if (offsetX == -1):
                            if (self.board[posY][posX] == ' ' or self.board[posY][posX] == self.currentlyPlaying):
                                continue

                        elif (offsetX == 0):
                            if (self.board[posY][posX] != ' '):
                                continue

                        elif (offsetX == 1):
                            if (self.board[posY][posX] == ' ' or self.board[posY][posX] == self.currentlyPlaying):
                                continue

                        # If sucess add as posibilitie
                        availableMoves.append([x, y, posX, posY])

        return availableMoves


    def check_winner(self):
        # 1. When oponent does not have any bauer left
        if (self.BauerCountA <= 0): return 'B'
        if (self.BauerCountB <= 0): return 'A'

        # 2. Reached the other side
        if ('B' in self.board[0]): return 'B';
        if ('A' in self.board[self.height-1]): return 'A';

        # 3. No moves possible
        if (len(self.available_moves('A')) <= 0): return 'B'
        if (len(self.available_moves('B')) <= 0): return 'A'
        
        return ' '


    def print_board(self):
        for i in self.board:
            print(i)


    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if (self.winner == ' '):
            if (self.bots < 2):
                # Player vs bot or Player vs Player

                # Curso select
                mx = round(pyxel.mouse_x / 8)-1
                my = round(pyxel.mouse_y / 8)-1

                if (pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT)):
                    # Deselect when clicking in outer area
                    if (mx < 0 or my < 0 or mx > self.width-1 or my > self.height-1):
                        self.selectedPos = []

                    else:
                        # New selection if clicking on own bauern
                        if (self.selectedPos == []):
                            if (self.board[my][mx] == self.currentlyPlaying):
                                self.selectedPos = [mx, my]

                        # Complete move if clicking on valid target
                        else:
                            moves = self.available_moves(self.currentlyPlaying)
                            valid = False
                            for mov in moves:
                                if (mov[0] == self.selectedPos[0] and mov[1] == self.selectedPos[1]):
                                    if (mov[2] == mx and mov[3] == my):
                                        valid = True

                            if (valid):
                                # Make move
                                self.move(self.selectedPos[0], self.selectedPos[1], mx, my)

                                # Calculating if winning
                                self.winner = self.check_winner()
                                
                                # Check if playing with bots
                                if (self.bots >= 1):
                                    # Tell about if he won / lost
                                    if (self.winner == 'B'):
                                        self.bot.won()
                                    elif (self.winner == 'A'):
                                        self.bot.lost()

                                    else:
                                        self.currentPlaying = 'B'
                                        botsMove = self.bot.make_move(self.board, self.available_moves('B'))
                                        self.move(botsMove[0], botsMove[1], botsMove[2], botsMove[3])
                                        self.currentPlaying = 'A'
                                
                                else:
                                    # Switch who is now
                                    if (self.currentlyPlaying == 'A'):
                                        self.currentlyPlaying = 'B'
                                    else:
                                        self.currentlyPlaying = 'A'

                            self.selectedPos = []

            else:

                # Two bots play against each other
                self.timer += 1
                if (self.timer > 5):
                    self.timer = 0

                    self.currentPlaying = 'B'
                    botsMove = self.bot.make_move(self.board, self.available_moves('A'))
                    self.move(botsMove[0], botsMove[1], botsMove[2], botsMove[3])

                    self.winner = self.check_winner()
                    if (self.winner == 'B'):
                        self.bot.won()
                    elif (self.winner == 'A'):
                        self.bot.lost()

                    self.currentPlaying = 'A'
                    botsMove = self.bot2.make_move(self.board, self.available_moves('B'))
                    self.move(botsMove[0], botsMove[1], botsMove[2], botsMove[3])

                    self.winner = self.check_winner()
                    if (self.winner == 'B'):
                        self.bot.won()
                    elif (self.winner == 'A'):
                        self.bot.lost()

        if (pyxel.btnr(pyxel.KEY_R)):
            self.resset()


    def draw(self):
        pyxel.cls(0)

        # Background
        for y in range(0, self.height):
            for x in range(0, self.width):
                if (int((x + y + 1) % 2) == 0):
                    pyxel.blt(x*8+8, y*8+8, 0, 0, 0, 8, 8)
                else:
                    pyxel.blt(x*8+8, y*8+8, 0, 8, 0, 8, 8)

        # Characters
        for y in range(0, self.height):
            for x in range(0, self.width):
                elem = self.board[y][x]
                if (elem == 'A'):
                    pyxel.blt(x*8+8, y*8+8, 0, 0, 8, 8, 8, 0)
                elif (elem == 'B'):
                    pyxel.blt(x*8+8, y*8+8, 0, 8, 8, 8, 8, 0)

        # Frame
        for y in range(0, self.height+2):
            pyxel.blt(0, y*8, 0, 16, 24, 8, 8, 0)
            pyxel.blt((self.width+1)*8, y*8, 0, 0, 24, 8, 8, 0)

        for x in range(0, self.width+2):
            pyxel.blt(x*8, 0, 0, 8, 32, 8, 8, 0)
            pyxel.blt(x*8, (self.height+1)*8, 0, 8, 16, 8, 8, 0)

        pyxel.blt(0, 0, 0, 0, 16, 8, 8, 0)
        pyxel.blt((self.width+1)*8, 0, 0, 16, 16, 8, 8, 0)
        pyxel.blt((self.width+1)*8, (self.height+1)*8, 0, 16, 32, 8, 8, 0)
        pyxel.blt(0, (self.height+1)*8, 0, 0, 32, 8, 8, 0)

        # Cursor
        mx = round(pyxel.mouse_x / 8) * 8
        my = round(pyxel.mouse_y / 8) * 8
    
        pyxel.blt(mx, my, 0, 16, 8, 8, 8, 0)
        
        if (self.selectedPos != []):
            pyxel.blt(self.selectedPos[0]*8+8, self.selectedPos[1]*8+8, 0, 24, 8, 8, 8, 0)

            moves = self.available_moves(self.currentlyPlaying)
            for mov in moves:
                if (mov[0] == self.selectedPos[0] and mov[1] == self.selectedPos[1]):
                    pyxel.blt(mov[2]*8+8, mov[3]*8+8, 0, 32, 8, 8, 8, 0)

        # Winner text
        if (self.winner != ' '):
            pyxel.text(1, 1, f'{self.winner} wins!', random.randint(0, 1)+9)



Game(13, 13, 2)
