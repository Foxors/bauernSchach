from pawnChessGame import PawnChessGame

from bots.RngBot import RngBot
from bots.DecisionBot import DecisionBot
from bots.LlmBot import LlmBot

import json
import copy

class PawnChessBotHarness:
    def __init__(self, game: PawnChessGame, player1Bot = 0, player2Bot = 0):
        self.game = game

        # Init bots
        self.bot1 = None
        self.bot2 = None

        if (player1Bot == 1): self.bot1 = RngBot(self.game.board, 'A')
        elif (player1Bot == 2): self.bot1 = DecisionBot(self.game.board, 'A')
        elif (player1Bot == 3): self.bot1 = LlmBot(self.game.board, 'A')

        if (player2Bot == 1): self.bot2 = RngBot(self.game.board, 'B')
        elif (player2Bot == 2): self.bot2 = DecisionBot(self.game.board, 'B')
        elif (player2Bot == 3): self.bot2 = LlmBot(self.game.board, 'B')

    def process_bots(self):
        turnOf = self.game.currentlyPlaying
        availableMoves = self.game.available_moves(turnOf)

        # Tell Bot 1 to make move, if is a bot
        if ((not (self.bot1 is None)) and turnOf == 'A'): 
            pos = self.bot1.decide_move(self.game.board, availableMoves)
            self.game.move_pawn('A',pos['origin']['x'],pos['origin']['y'],pos['target']['x'],pos['target']['y'])

        # Tell Bot 2 to make move, if is a bot
        if ((not (self.bot2 is None)) and turnOf == 'B'):
            pos = self.bot2.decide_move(self.game.board, availableMoves)
            self.game.move_pawn('B',pos['origin']['x'],pos['origin']['y'],pos['target']['x'],pos['target']['y'])


# If run alone it is headless without any GUI
def main():
    # Selection of options
    saveDir = "gamesResults.json"

    scoreA = 0
    scoreB = 0
    gamesData = []
    saveData = []
    with open(saveDir, "r") as f:
        saveData = json.load(f)

    size = -99
    while (size < 3): size = int(input("Board size (3-nearly infinite): "))
    bot1 = -99
    while (bot1 < 1 or bot1 > 3): bot1 = int(input("Bot A (1-3): "))
    bot2 = -99
    while (bot2 < 1 or bot2 > 3): bot2 = int(input("Bot B (1-3): "))
    games = -99
    while (games < 1): games = int(input("Games to play (1-infinite): "))

    game = PawnChessGame(size, size)
    harness = PawnChessBotHarness(game, bot1, bot2)

    for i in range(games):
        log = []
        game = PawnChessGame(size, size)
        harness.game = game

        # Start positions
        log.append({ "board": copy.deepcopy(game.board), "turnOf": game.currentlyPlaying })

        # Repeat until finished and log everything
        while (game.winner == ' '):
            harness.process_bots()
            log.append({ "board": copy.deepcopy(game.board), "turnOf": game.currentlyPlaying })

        # Update scores
        print(f"Player {game.winner} won!\n\n")
        if (game.winner == 'A'): scoreA += 1
        elif (game.winner == 'B'): scoreB += 1

        gamesData.append({'winner': game.winner, 'logs': copy.deepcopy(log) })

    # Finally write everything down
    print(f"Player A won {scoreA} times and player B {scoreB} times")
    saveData.append({ 'bot1': bot1, 'bot2': bot2, 'scoreA': scoreA, 'scoreB': scoreB, 'games': copy.deepcopy(gamesData), 'size': size, 'playedGames': games })

    json_str = json.dumps(saveData)
    with open(saveDir, "w") as f:
        f.write(json_str)


if __name__ == "__main__":
    main()
