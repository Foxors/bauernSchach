import random

from bots.NoBot import NoBot
from treeBuilder import build_tree

class TreeBot(NoBot):
    def __init__(self, initBoard, player):
        self.tree = build_tree()

        self.player = player
        self.elem = self.tree

    def resset(self, initBoard, player):
        self.elem = self.tree
        self.player = player

    def decide_move(self, board, options):
        if (self.elem['branches'] is None):
            print(f"No more sub branches found by bot {self.player}")
            return options[random.randint(0, len(options)-1)]

        # Find best move
        topChild = self.elem['branches'][0]
        topChildWinPerc = 0
        for branch in self.elem['branches']:
            if (branch['winner'] is None or branch['winner'] == ' '):
                if ('aWins' in branch and 'bWins' in branch):
                    # calculate propability
                    aWins = branch['aWins']
                    bWins = branch['bWins']
                    totalWins = aWins + bWins
                    percA = aWins / totalWins
                    percB = bWins / totalWins
                    perc = 0
                    if (self.player == 'A'):
                        perc = percA
                    if (self.player == 'B'):
                        perc = percB

                    #print(f"Perc: {perc} vs {topChildWinPerc}")

                    # Deciding if better or worse
                    if (perc > topChildWinPerc):
                        topChild = branch
                        topChildWinPerc = perc

            else:
                # If only bot can win now
                if (branch['winner'] == self.player):
                    topChild = branch
                    break


        self.elem = topChild

        # Already lost
        if (not 'moveMade' in topChild):
            print(f"Bot {self.player} already lost")
            return options[random.randint(0, len(options)-1)]
        
        # Make move
        return topChild['moveMade']

    def board_changed(self, board):
        if (self.elem['branches'] is None):
            print(f"No more sub branches found by bot {self.player}")
            return

        for branch in self.elem['branches']:
            if (branch['board'] == board):
                self.elem = branch
                return

    def won(self):
        pass

    def lost(self):
        pass

    def info_print(self):
        pass
