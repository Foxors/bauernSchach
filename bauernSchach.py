import pyxel
import random

class NoBot:
    def __init__(self, board):
        pass
    def make_move(self, board, options):
        pass
    def lost(self):
        pass
    def won(self):
        pass
class Bot(NoBot):
    def __init__(self, board):
        pass
    def make_move(self, board, options):
        if (len(options) <= 0): return [0, 0, 0, 0]
        rng = random.randint(0, len(options)-1)
        return options[rng]

    def lost(self):
        pass

    def won(self):
        pass
class BestDecisionBot(NoBot):
    def __init__(self, board):
        pass
    def make_move(self, board, options):
        highScore = { 'score': 0, 'opt': [] }

        for opt in options:
            score = 1

            # If field is a enemie to capture do it
            if (board[opt[3]][opt[2]] != ' '):
                score += 2

            # If target is the other end == instant win
            if (len(board) == opt[3]):
                score += 3

            # If running into free teretory == good
            if (len(board) == opt[3]):
                for x in range(-1, 1):
                    if (opt[2]+x < 0 or opt[2]+x >= len(board[opt[3]]) or board[opt[3]][opt[2]+x] == ' '):
                        score += 1
            
            # When same let the randomness decide
            if (score == highScore['score']):
                if (random.randint(0, len(options)) > 0):
                    highScore = { 'score': score, 'opt': opt.copy() }

            # If better choose this option
            if (score > highScore['score']):
                highScore = { 'score': score, 'opt': opt.copy() }

        return highScore['opt']

    def lost(self):
        pass
    def won(self):
        pass

class App:
    def __init__(self):
        self.width = 3
        self.height = 3

        self.widthPx = 120
        self.heightPx = 120

        self.gridSize = 8

        self.maxPlayerMode = 2
        self.player1Mode = 0
        self.player2Mode = 0
        self.bot1 = NoBot(None)
        self.bot2 = NoBot(None)

        self.scoreA = 0
        self.scoreB = 0

        self.menu = 0

        self.mouseCellPosX = 0
        self.mouseCellPosY = 0
        self.staticMouseCellPosX = 0
        self.staticMouseCellPosY = 0

        self.game_resset()

        pyxel.init(self.widthPx, self.heightPx, "Pawn Chess", 30)
        pyxel.load("assets.pyxres")
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        # Cursor position
        offsetX = 0
        cursorCorrectionX = 0.5
        if (self.width%2 == 0):
            offsetX = round(self.gridSize/2)
            cursorCorrectionX = 1
        offsetY = 0
        cursorCorrectionY = 0.5
        if (self.height%2 == 0):
            offsetY = round(self.gridSize/2)
            cursorCorrectionY = 1
        self.mouseCellPosX = round(pyxel.mouse_x / 8 - cursorCorrectionX) * 8 + offsetX
        self.mouseCellPosY = round(pyxel.mouse_y / 8 - cursorCorrectionY) * 8 + offsetY

        if (self.width%2 != 0): self.staticMouseCellPosX = self.mouseCellPosX + self.gridSize
        else: self.staticMouseCellPosX = self.mouseCellPosX + self.gridSize / 2
        if (self.height%2 != 0): self.staticMouseCellPosY = self.mouseCellPosY + self.gridSize
        else: self.staticMouseCellPosY = self.mouseCellPosY + self.gridSize / 2
        self.staticMouseCellPosX -= 8
        self.staticMouseCellPosY -= 8

        if (self.menu == 0):
            # Main menu settings buttons
            if (pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT)):
                if (self.staticMouseCellPosX <= 32 and self.staticMouseCellPosX >= 8 and self.staticMouseCellPosY == 8):
                    self.game_resset()

                    if (self.player1Mode == 0): self.bot1 = NoBot(self.board)
                    if (self.player1Mode == 1): self.bot1 = Bot(self.board)
                    if (self.player1Mode == 2): self.bot1 = BestDecisionBot(self.board)
                    if (self.player2Mode == 0): self.bot2 = NoBot(self.board)
                    if (self.player2Mode == 1): self.bot2 = Bot(self.board)
                    if (self.player2Mode == 2): self.bot2 = BestDecisionBot(self.board)

                    self.menu = 1

                if (self.staticMouseCellPosX == 8 and self.staticMouseCellPosY == 16):
                    self.width -= 1
                    self.height -= 1
                    if (self.width <= 2):
                        self.width = 3
                    if (self.height <= 2):
                        self.height = 3

                if (self.staticMouseCellPosX == 32 and self.staticMouseCellPosY == 16):
                    self.width += 1
                    self.height += 1
                    if (self.width >= self.widthPx / self.gridSize):
                        self.width = round(self.widthPx / self.gridSize)
                    if (self.height >= self.heightPx / self.gridSize):
                        self.height = round(self.heightPx / self.gridSize)

                if (self.staticMouseCellPosX == 8 and self.staticMouseCellPosY == 24):
                    self.player1Mode -= 1
                    if (self.player1Mode < 0): self.player1Mode = self.maxPlayerMode
                if (self.staticMouseCellPosX == 40 and self.staticMouseCellPosY == 24):
                    self.player1Mode += 1
                    if (self.player1Mode > self.maxPlayerMode): self.player1Mode = 0

                if (self.staticMouseCellPosX == 8 and self.staticMouseCellPosY == 32):
                    self.player2Mode -= 1
                    if (self.player2Mode < 0): self.player2Mode = self.maxPlayerMode
                if (self.staticMouseCellPosX == 40 and self.staticMouseCellPosY == 32):
                    self.player2Mode += 1
                    if (self.player2Mode > self.maxPlayerMode): self.player2Mode = 0

        elif (self.menu == 1):
            if (self.winner == ' '):
                # Bot or human interact
                if ((self.currentlyPlaying == 'A' and self.player1Mode > 0) or (self.currentlyPlaying == 'B' and self.player2Mode > 0)):
                    moves = self.available_moves(self.currentlyPlaying)

                    # Make bot do a move
                    mov = []
                    if (self.currentlyPlaying == 'A'):
                        mov = self.bot1.make_move(self.board, moves)
                    if (self.currentlyPlaying == 'B'):
                        mov = self.bot2.make_move(self.board, moves)
                    if (len(mov) < 4):
                        mov = [0, 0, 0, 0]
                        print("Bot gave incorect move")
                    self.move(mov[0], mov[1], mov[2], mov[3])

                    # Calculating if winning
                    self.game_check_winner()
                        
                    # Switch who is now
                    if (self.currentlyPlaying == 'A'):
                        self.currentlyPlaying = 'B'
                    else:
                        self.currentlyPlaying = 'A'
                    
                
                else:
                    # Curso select
                    mx = self.staticMouseCellPosX/8 - (self.widthPx/2 - (self.width+2)*8/2)/8
                    my = self.staticMouseCellPosY/8 - (self.heightPx/2 - (self.height+2)*8/2)/8
                    if (self.width%2 == 0): mx -= 0.5
                    else: mx -= 1
                    if (self.height%2 == 0): my -= 0.5
                    else: my -= 1
                    mx = round(mx)
                    my = round(my)

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
                                    self.game_check_winner()
                                    
                                    # Switch who is now
                                    if (self.currentlyPlaying == 'A'):
                                        self.currentlyPlaying = 'B'
                                    else:
                                        self.currentlyPlaying = 'A'

                                self.selectedPos = []

            if (pyxel.btnr(pyxel.KEY_Q)):
                self.menu = 0

    def draw(self):
        pyxel.cls(0)

        # Offset when not n%2 good number (forgot english)
        smallOffsetX = 0
        if (self.width%2 == 0): smallOffsetX = round(self.gridSize/2)
        smallOffsetY = 0
        if (self.height%2 == 0): smallOffsetY = round(self.gridSize/2)

        # Background
        for y in range(-smallOffsetY, self.heightPx+smallOffsetY, self.gridSize):
            for x in range(-smallOffsetX, self.widthPx+smallOffsetX, self.gridSize):
                if (int((x/self.gridSize + y/self.gridSize + 1) % 2) == 0):
                    pyxel.blt(x, y, 0, 0, 0, 8, 8)
                else:
                    pyxel.blt(x, y, 0, 8, 0, 8, 8)
        # Frame
        offsetX = (self.widthPx/2 - (self.width+2)*8/2)
        offsetY = (self.heightPx/2 - (self.height+2)*8/2)
        for x in range(1, self.width+1):
            pyxel.blt(offsetX+x*8, offsetY, 0, 8, 32, 8, 8, 0)
            pyxel.blt(offsetX+x*8, offsetY+self.height*8+8, 0, 8, 16, 8, 8, 0)
        for y in range(1, self.height+1):
            pyxel.blt(offsetX, offsetY+y*8, 0, 16, 24, 8, 8, 0)
            pyxel.blt(offsetX+self.width*8+8, offsetY+y*8, 0, 0, 24, 8, 8, 0)
        pyxel.blt(offsetX, offsetY, 0, 0, 16, 8, 8, 0)
        pyxel.blt(offsetX+(self.width+1)*8, offsetY, 0, 16, 16, 8, 8, 0)
        pyxel.blt(offsetX+(self.width+1)*8, offsetY+(self.height+1)*8, 0, 16, 32, 8, 8, 0)
        pyxel.blt(offsetX, offsetY+(self.height+1)*8, 0, 0, 32, 8, 8, 0)

        # Outer frame background
        for x in range(0, self.widthPx, 8):
            for y in range(0, round(offsetY)):
                pyxel.blt(x, y-7, 0, 8, 24, 8, 8, 0)
                pyxel.blt(x, y + self.heightPx/2+((self.height+2)*8/2), 0, 8, 24, 8, 8, 0)
        for x in range(0, round(offsetX), 8):
            for y in range(0, (self.height+2)*8, 8):
                pyxel.blt(x, offsetY+y, 0, 8, 24, 8, 8, 0)
                pyxel.blt(x+round(offsetX)+(self.width+2)*8, offsetY+y, 0, 8, 24, 8, 8, 0)

        if (self.menu == 0):
            y = 8+smallOffsetY

            # Button start
            pyxel.blt(8+smallOffsetX, y, 0, 16, 56, 8, 8, 0)
            pyxel.text(8*2+2+smallOffsetX, y+2, "Start", 0)
            pyxel.text(8*2+1+smallOffsetX, y+1, "Start", 7)

            # Button change Scale
            y += 8
            pyxel.blt(8+smallOffsetX, y, 0, 0, 56, 8, 8, 0)
            pyxel.text(8*2+3+smallOffsetX, y+2, f'{self.width}', 0)
            pyxel.text(8*2+2+smallOffsetX, y+1, f'{self.width}', 7)
            pyxel.blt(8*4+smallOffsetX, y, 0, 8, 56, 8, 8, 0)

            # Button change Player 1 mode
            y += 8
            mode = ""
            if (self.player1Mode == 0): mode = "P1 Hu"
            if (self.player1Mode == 1): mode = "P1 ra"
            if (self.player1Mode == 2): mode = "P1 De"
            pyxel.blt(8+smallOffsetX, y, 0, 0, 56, 8, 8, 0)
            pyxel.text(8*2+3+smallOffsetX, y+2, mode, 0)
            pyxel.text(8*2+2+smallOffsetX, y+1, mode, 7)
            pyxel.blt(8*5+smallOffsetX, y, 0, 8, 56, 8, 8, 0)

            # Button change Player 2 mode
            y += 8
            mode = ""
            if (self.player2Mode == 0): mode = "P2 Hu"
            if (self.player2Mode == 1): mode = "P2 ra"
            if (self.player2Mode == 2): mode = "P2 De"
            pyxel.blt(8+smallOffsetX, y, 0, 0, 56, 8, 8, 0)
            pyxel.text(8*2+3+smallOffsetX, y+2, mode, 0)
            pyxel.text(8*2+2+smallOffsetX, y+1, mode, 7)
            pyxel.blt(8*5+smallOffsetX, y, 0, 8, 56, 8, 8, 0)

        elif (self.menu == 1):
            # Characters
            for y in range(0, self.height):
                for x in range(0, self.width):
                    elem = self.board[y][x]
                    if (elem == 'A'):
                        pyxel.blt(x*8+8+offsetX, y*8+8+offsetY, 0, 0, 8, 8, 8, 0)
                    elif (elem == 'B'):
                        pyxel.blt(x*8+8+offsetX, y*8+8+offsetY, 0, 8, 8, 8, 8, 0)

            if (self.selectedPos != []):
                # Available moves
                moves = self.available_moves(self.currentlyPlaying)
                for mov in moves:
                    if (mov[0] == self.selectedPos[0] and mov[1] == self.selectedPos[1]):
                        pyxel.blt(mov[2]*8+8+offsetX, mov[3]*8+8+offsetY, 0, 16, 48, 8, 8, 0)

            # Winner text
            if (self.winner != ' '):
                if (self.winner == 'A'):
                    pyxel.blt(8, 0, 0, 0, 40, 8, 8, 0)

                else:
                    pyxel.blt(8, 0, 0, 8, 40, 8, 8, 0)
                
                pyxel.blt(16, 0, 0, 16, 40, 8, 8, 0)

            # Scores
            pyxel.text(2, 2, f'{self.scoreA}', 8)
            pyxel.text(2, 10, f'{self.scoreB}', 3)

        # Cursor
        if (self.selectedPos == []):
            pyxel.blt(self.mouseCellPosX, self.mouseCellPosY, 0, 0, 48, 8, 8, 0)
        else:
            pyxel.blt(self.selectedPos[0]*8+8+offsetX, self.selectedPos[1]*8+8+offsetY, 0, 8, 48, 8, 8, 0)


    # ====================
    #  GAME CODE
    # ====================

    def game_resset(self):
        # Resset board
        self.board = [[' ' for x in range(self.width)] for y in range(self.height)] 
        for x in range(self.width):
            self.board[0][x] = 'A'
            self.board[self.height-1][x] = 'B'

        # Resset how many pawns each player has
        self.BauerCountA = len(self.board[0])
        self.BauerCountB = len(self.board[0])
    
        # Resset who is now and who won
        self.currentlyPlaying = 'A'
        self.winner = ' '

        self.timer = 0
    
        # Resset which pawn is selected/or if even one is selected
        self.selectedPos = []

    def game_check_winner(self):
        # 1. When oponent does not have any bauer left
        if (self.BauerCountA <= 0): self.winner = 'B'
        if (self.BauerCountB <= 0): self.winner = 'A'

        # 2. Reached the other side
        if ('B' in self.board[0]): self.winner = 'B';
        if ('A' in self.board[self.height-1]): self.winner = 'A';

        # 3. No moves possible
        if (len(self.available_moves('A')) <= 0): self.winner = 'B'
        if (len(self.available_moves('B')) <= 0): self.winner = 'A'

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

App()
