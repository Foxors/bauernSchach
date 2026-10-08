import pyxel
import matplotlib.pyplot as plt
import numpy as np
import json

class PawnChessVisualizer:
    def __init__(self):
        self.menu = 0
        self.scrollX = 0
        self.scrollY = 0

        saveDir = "gamesResults.json"
        self.saveData = []
        with open(saveDir, "r") as f:
            self.saveData = json.load(f)
        self.selectedRun = 0

        pyxel.init(120, 120, "Pawn Chess - Data Visualizer", 30)
        pyxel.load("assets.pyxres")
        pyxel.run(self.update, self.draw)

    def plot_win_ratio(self):
        plt.style.use('_mpl-gallery')

        y = []
        perc = 0
        highest = 0
        lowest = 0
        for g in self.saveData[self.selectedRun]['games']:
            if (g['winner'] == 'A'): perc -= 1
            if (g['winner'] == 'B'): perc += 1
            y.append(perc)

            if (perc > highest): highest = perc
            if (perc < lowest): lowest = perc

        fig, ax = plt.subplots()
        ax.stairs(y, linewidth=2.5)
        ax.set(xlim=(0, self.saveData[self.selectedRun]['playedGames']), xticks=np.arange(1, self.saveData[self.selectedRun]['playedGames']),
               ylim=(lowest, highest), yticks=np.arange(lowest, highest))

        plt.show()

    def update(self):
        if (self.menu == 0):
            if (pyxel.btnr(pyxel.KEY_UP)): self.scrollY -= 1
            if (self.scrollY < 0) :self.scrollY = len(self.saveData)-1
            if (pyxel.btnr(pyxel.KEY_DOWN)): self.scrollY += 1
            if (self.scrollY >= len(self.saveData)): self.scrollY = 0

            if (pyxel.btnr(pyxel.KEY_RETURN)):
                self.selectedRun = self.scrollY
                self.menu = 1

        elif (self.menu == 1):
            if (pyxel.btnr(pyxel.KEY_Q)):
                self.scrollY = self.selectedRun
                self.menu = 0

            if (pyxel.btnr(pyxel.KEY_UP)): self.scrollY -= 1
            if (self.scrollY < 0) :self.scrollY = 2
            if (pyxel.btnr(pyxel.KEY_DOWN)): self.scrollY += 1
            if (self.scrollY >= 2): self.scrollY = 0

            if (pyxel.btnr(pyxel.KEY_RETURN)):
                if (self.scrollY == 0):
                    self.plot_win_ratio()


    def draw(self):
        pyxel.cls(0)

        # Background
        for y in range(0, 120, 8):
            for x in range(0, 120, 8):
                if (int((x/8 + y/8 + 1) % 2) == 0):
                    pyxel.blt(x, y, 0, 0, 0, 8, 8)
                else:
                    pyxel.blt(x, y, 0, 8, 0, 8, 8)
        # Frame
        for x in range(1, round(120/8)):
            pyxel.blt(x*8, 0, 0, 8, 32, 8, 8, 0)
            pyxel.blt(x*8, 120-8, 0, 8, 16, 8, 8, 0)
        for y in range(1, round(120/8)):
            pyxel.blt(0, y*8, 0, 16, 24, 8, 8, 0)
            pyxel.blt(120-8, y*8, 0, 0, 24, 8, 8, 0)
        pyxel.blt(0, 0, 0, 0, 16, 8, 8, 0)
        pyxel.blt(120-8, 0, 0, 16, 16, 8, 8, 0)
        pyxel.blt(120-8, 120-8, 0, 16, 32, 8, 8, 0)
        pyxel.blt(0, 120-8, 0, 0, 32, 8, 8, 0)

        if (self.menu == 0):
            for i in range(len(self.saveData)):
                text = f"{self.saveData[i]['bot1']}vs{self.saveData[i]['bot2']} {self.saveData[i]['scoreA']}:{self.saveData[i]['scoreB']} in {self.saveData[i]['playedGames']} games"
                pyxel.text(8+1, i*8+8+1, text, 0)
                pyxel.text(8, i*8+8,   text, 7)

            pyxel.blt(0, self.scrollY*8+8, 0, 8, 56, 8, 8, 0)

        elif (self.menu == 1):
            y = 8
            text = f"Bot1 type: {self.saveData[self.selectedRun]['bot1']}"
            pyxel.text(8+1, y+1, text, 0)
            pyxel.text(8, y,   text, 7)

            y += 8
            text = f"Bot2 type: {self.saveData[self.selectedRun]['bot2']}"
            pyxel.text(8+1, y+1, text, 0)
            pyxel.text(8, y,   text, 7)

            y += 8
            text = f"Played Games: {self.saveData[self.selectedRun]['playedGames']}"
            pyxel.text(8+1, y+1, text, 0)
            pyxel.text(8, y,   text, 7)

            y += 8
            text = f"End score: {self.saveData[self.selectedRun]['scoreA']}:{self.saveData[self.selectedRun]['scoreB']}"
            pyxel.text(8+1, y+1, text, 0)
            pyxel.text(8, y, text, 7)

            y += 16
            pyxel.blt(0, self.scrollY*8+y, 0, 8, 56, 8, 8, 0)

            text = f"Show win ratio"
            pyxel.text(8+1, y+1, text, 0)
            pyxel.text(8, y, text, 7)


if __name__ == "__main__":
    PawnChessVisualizer()
