from bots.NoBot import NoBot
from bots.RngBot import RngBot
from bots.TreeBot import TreeBot
from bots.DecisionBot import DecisionBot
from bots.LlmBot import LlmBot
from pawnChessGame import PawnChessGame
from pawnChessBotHarness import PawnChessBotHarness

class PawnChessTournament:
    def __init__(self):
        self.games = 1
        self.size = 3

        self.botHarness = None
        self.bots = []

    def add_bot(self, bot, name):
        self.bots.append({ 'wins': 0, 'bot': bot, 'name': name })

    # Selection of options
    def play(self):
        game = PawnChessGame(self.size, self.size)
        harness = PawnChessBotHarness(game, 1, 1)
      
        for i in range(self.games):
            for bot1 in self.bots:
                for bot2 in self.bots:
                    # Prep for round
                    game = PawnChessGame(self.size, self.size)
                    harness.game = game
                    harness.bot1 = bot1['bot']
                    harness.bot2 = bot2['bot']
                    harness.resset()
  
                    # Repeat until finish
                    while (game.winner == ' '): harness.process_bots()
                
                    if (game.winner == 'A'): bot1['wins'] += 1
                    elif (game.winner == 'B'): bot2['wins'] += 1
      
                    # Update scores
                    print(f"{bot1['name']} vs. {bot2['name']} - {game.winner} wins")

        for bot in self.bots:
            print(f"{bot['name']} - {bot['wins']} wins")

t = PawnChessTournament()
t.add_bot(TreeBot(None, 'A'), "Christmas Tree")
t.add_bot(RngBot(None, 'A'), "Gambler")
t.add_bot(DecisionBot(None, 'A'), "Smarter gambler")
#t.add_bot(LlmBot(None, 'A'), "Word predictor")
t.play()
