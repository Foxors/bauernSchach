import pyxel
import random
from time import sleep

from pawnChessGame import PawnChessGame
from pawnChessBotHarness import PawnChessBotHarness

class PawnChessGui:
    def __init__(self):
        self.width = 3
        self.height = 3

        self.widthPx = 120
        self.heightPx = 120
        self.gridSize = 8

        self.menu = 0

        self.mouseCellPosX = 0
        self.mouseCellPosY = 0
        self.staticMouseCellPosX = 0
        self.staticMouseCellPosY = 0
        self.selectedPos = []

        self.playerModes = [ "Human", "RNG", "Decis", "Llm" ]
        self.playMode1 = 0
        self.playMode2 = 0

        self.game = None
        self.botHarness = None

        pyxel.init(self.widthPx, self.heightPx, "Pawn Chess", 30)
        pyxel.load("assets.pyxres")
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        # Cursor position -> in gridSize cells
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
                    self.game = PawnChessGame(self.width, self.height)
                    self.botHarness = PawnChessBotHarness(self.game, self.playMode1, self.playMode2)
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
                    if (self.playMode1-1 < 0): self.playMode1 = len(self.playerModes)-1
                    else: self.playMode1 -= 1
                if (self.staticMouseCellPosX == 40 and self.staticMouseCellPosY == 24):
                    if (self.playMode1+1 >= len(self.playerModes)): self.playMode1 = 0
                    else: self.playMode1 += 1

                if (self.staticMouseCellPosX == 8 and self.staticMouseCellPosY == 32):
                    if (self.playMode2-1 < 0): self.playMode2 = len(self.playerModes)-1
                    else: self.playMode2 -= 1
                if (self.staticMouseCellPosX == 40 and self.staticMouseCellPosY == 32):
                    if (self.playMode2+1 >= len(self.playerModes)): self.playMode2 = 0
                    else: self.playMode2 += 1

        elif (self.menu == 1):
            if (self.game.winner == ' '):
                # Process optional bots
                if (self.playMode1 > 0 or self.playMode2 > 0):
                    self.botHarness.process_bots()
                
                # Process player when at least one player is not a bot
                if (not(self.playMode1 > 0 and self.playMode2 > 0)):
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
                                if (self.game.board[my][mx] == self.game.currentlyPlaying):
                                    self.selectedPos = [mx, my]

                            # Complete move if clicking on valid target
                            else:
                                moves = self.game.available_moves(self.game.currentlyPlaying)

                                # Make move
                                try: self.game.move_pawn(self.game.currentlyPlaying, self.selectedPos[0], self.selectedPos[1], mx, my)
                                except:
                                    # When error just exit out of selection
                                    pass

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
            mode = self.playerModes[self.playMode1]
            pyxel.blt(8+smallOffsetX, y, 0, 0, 56, 8, 8, 0)
            pyxel.text(8*2+3+smallOffsetX, y+2, mode, 0)
            pyxel.text(8*2+2+smallOffsetX, y+1, mode, 7)
            pyxel.blt(8*5+smallOffsetX, y, 0, 8, 56, 8, 8, 0)

            # Button change Player 2 mode
            y += 8
            mode = self.playerModes[self.playMode2]
            pyxel.blt(8+smallOffsetX, y, 0, 0, 56, 8, 8, 0)
            pyxel.text(8*2+3+smallOffsetX, y+2, mode, 0)
            pyxel.text(8*2+2+smallOffsetX, y+1, mode, 7)
            pyxel.blt(8*5+smallOffsetX, y, 0, 8, 56, 8, 8, 0)

        elif (self.menu == 1):
            # Characters
            for y in range(0, self.height):
                for x in range(0, self.width):
                    elem = self.game.board[y][x]
                    if (elem == 'A'):
                        pyxel.blt(x*8+8+offsetX, y*8+8+offsetY, 0, 0, 8, 8, 8, 0)
                    elif (elem == 'B'):
                        pyxel.blt(x*8+8+offsetX, y*8+8+offsetY, 0, 8, 8, 8, 8, 0)

            if (self.selectedPos != []):
                # Available moves
                moves = self.game.available_moves(self.game.currentlyPlaying)
                for mov in moves:
                    if (mov['origin']['x'] == self.selectedPos[0] and mov['origin']['y'] == self.selectedPos[1]):
                        pyxel.blt(mov['target']['x']*8+8+offsetX, mov['target']['y']*8+8+offsetY, 0, 16, 48, 8, 8, 0)

            # Winner text
            if (self.game.winner != ' '):
                if (self.game.winner == 'A'):
                    pyxel.blt(0, 0, 0, 0, 40, 8, 8, 0)

                else:
                    pyxel.blt(0, 0, 0, 8, 40, 8, 8, 0)
                
                pyxel.blt(8, 0, 0, 16, 40, 8, 8, 0)
        
        # Cursor
        if (self.selectedPos == []):
            pyxel.blt(self.mouseCellPosX, self.mouseCellPosY, 0, 0, 48, 8, 8, 0)
        else:
            pyxel.blt(self.selectedPos[0]*8+8+offsetX, self.selectedPos[1]*8+8+offsetY, 0, 8, 48, 8, 8, 0)

# If run alone it is headless without any GUI
def main():
    gameUi = PawnChessGui()
if __name__ == "__main__":
    main()
