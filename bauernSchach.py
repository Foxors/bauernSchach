import random
from time import sleep
import pyxel

class Game:
    def __init__(self, width, height):
        self.board = [[0 for x in range(width)] for y in range(height)] 
        self.width = width;
        self.height = height;

        for x in range(width):
            self.board[0][x] = 'A'
            self.board[height-1][x] = 'B'

        self.BauerCountA = len(self.board[0])
        self.BauerCountB = len(self.board[0])

        self.currentlyPlaying = 'A'
        self.winner = ' '

        self.timer = 0

        pyxel.init(8*width, 8*height)
        pyxel.load("assets.pyxres")
        pyxel.run(self.update, self.draw)


    def move(self, x1: int, y1: int, x2: int, y2: int):
        if (x1 < 0 or x1 >= self.width or
            y1 < 0 or y1 >= self.height or
            x2 < 0 or x2 >= self.width or
            y2 < 0 or y2 >= self.height):
            return False

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
                        if (offsetX == 0):
                            if (self.board[posY][posX] != ' '):
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
            self.timer += 1

            if (self.timer > 5):
                self.timer = 0
                moves = self.available_moves(self.currentlyPlaying)

                nextMove = moves[random.randint(0, len(moves)) - 1]
                x1 = nextMove[0]
                y1 = nextMove[1]
                x2 = nextMove[2]
                y2 = nextMove[3]

                self.move(x1, y1, x2, y2)

                self.winner = self.check_winner()

                if (self.currentlyPlaying == 'A'):
                    self.currentlyPlaying = 'B'
                else:
                    self.currentlyPlaying = 'A'


    def draw(self):
        pyxel.cls(0)

        for y in range(0, self.height):
            for x in range(0, self.width):
                if (int((x + y + 1) % 2) == 0):
                    pyxel.blt(x*8, y*8, 0, 0, 0, 8, 8)
                else:
                    pyxel.blt(x*8, y*8, 0, 8, 0, 8, 8)

        for y in range(0, self.height):
            for x in range(0, self.width):
                elem = self.board[y][x]
                if (elem == 'A'):
                    pyxel.blt(x*8, y*8, 0, 0, 8, 8, 8, 0)
                elif (elem == 'B'):
                    pyxel.blt(x*8, y*8, 0, 8, 8, 8, 8, 0)

        if (self.winner != ' '):
            pyxel.text(1, 1, f'{self.winner} wins!', random.randint(0, 1)+9)


Game(6, 3)
