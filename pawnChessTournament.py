import json
import time
import os

from bots.NoBot import NoBot
from bots.RngBot import RngBot
from bots.TreeBot import TreeBot
from bots.DecisionBot import DecisionBot
from bots.NnBot import NnBot
from bots.LlmBot import LlmBot
from bots.ExploreBot import ExploreBot
from pawnChessGame import PawnChessGame
from pawnChessBotHarness import PawnChessBotHarness

totalSize = 8

class PawnChessTournament:
    def __init__(self):
        self.games = 5000
        self.size = totalSize

        self.botHarness = None
        self.bots = []
        self.winners = []

    def add_bot(self, bot, name):
        self.bots.append({ 'wins': 0, 'bot': bot, 'name': name })

    # Selection of options
    def play(self):
        game = PawnChessGame(self.size, self.size)
        harness = PawnChessBotHarness(game, 1, 1)
      
        for i in range(self.games):
            for bot1 in self.bots:
                for bot2 in self.bots:

                    if (bot1 == bot2): continue

                    # Prep for round
                    game = PawnChessGame(self.size, self.size)
                    harness.game = game
                    harness.bot1 = bot1['bot']
                    harness.bot2 = bot2['bot']
                    harness.resset()
  
                    # Repeat until finish
                    while (game.winner == ' '): harness.process_bots()
                
                    if (game.winner == 'A'):
                        bot1['wins'] += 1
                        self.winners.append(bot1['name'])

                    elif (game.winner == 'B'):
                        bot2['wins'] += 1
                        self.winners.append(bot2['name'])
      
                    # Update scores
                    print(f"{bot1['name']} vs. {bot2['name']} - {game.winner} wins")

        for bot in self.bots:
            print(f"{bot['name']} - {bot['wins']} wins")

def main():
    saveDir = "tournamentResults.json"

    # Making sure file exists
    if not os.path.exists(saveDir):
        with open(saveDir, 'w') as file:
            file.write("[]")

    savedData = []
    with open(saveDir, "r") as f:
        savedData = json.load(f)

    t = PawnChessTournament()
    #t.add_bot(TreeBot(None, 'A'), "Christmas Tree")
    t.add_bot(RngBot(None, 'A'), "Gambler")
    t.add_bot(DecisionBot(None, 'A'), "Smarter gambler")
    t.add_bot(NnBot(PawnChessGame(totalSize, totalSize).board, 'A'), "School kid")
    t.add_bot(ExploreBot(PawnChessGame(totalSize, totalSize).board, 'A'), "Advanturer")
    t.play()

    # Finally write everything down
    botStats = []
    for bot in t.bots: botStats.append({ 'name': bot['name'], 'wins': bot['wins'] })
    savedData.append({ 'date': time.localtime(), 'gamesPlayed': t.games, 'size': t.size, 'results': botStats, 'winnerTimeline': t.winners })
    json_str = json.dumps(savedData)
    with open(saveDir, "w") as f:
        f.write(json_str)

if __name__ == "__main__":
    main()
