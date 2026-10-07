from pawnChessGame import PawnChessGame
import random

# Basic bot
class RngBot:
    def __init__(self, board, player: str):
        pass
    def decide_move(self, board, availableMoves):
        return availableMoves[random.randint(0, len(availableMoves)-1)]
class DecisionBot:
    def __init__(self, board, player: str):
        pass
    def decide_move(self, board, options):
        highScore = { 'score': 0, 'opt': None }

        for opt in options:
            score = 1

            # If field is a enemie to capture do it
            if (board[opt['target']['y']][opt['target']['x']] != ' '):
                score += 2

            # If target is the other end == instant win
            if (len(board) == opt['target']['y']):
                score += 3

            # If running into free teretory == good
            if (len(board) == opt['target']['y']):
                for x in range(-1, 1):
                    if (opt['target']['x']+x < 0 or opt['target']['x']+x >= len(board[opt['target']['y']]) or board[opt['target']['y']][opt['target']['x']+x] == ' '):
                        score += 1
            
            # When same let the randomness decide
            if (score == highScore['score']):
                if (random.randint(0, len(options)) > 0):
                    highScore = { 'score': score, 'opt': opt.copy() }

            # If better choose this option
            if (score > highScore['score']):
                highScore = { 'score': score, 'opt': opt.copy() }

        return highScore['opt']

class PawnChessBotHarness:
    def __init__(self, game: PawnChessGame, player1Bot = 0, player2Bot = 0):
        self.game = game

        # Init bots
        self.bot1 = None
        self.bot2 = None

        if (player1Bot == 1): self.bot1 = RngBot(self.game.board, 'A')
        elif (player1Bot == 2): self.bot1 = DecisionBot(self.game.board, 'A')

        if (player2Bot == 1): self.bot2 = RngBot(self.game.board, 'B')
        elif (player2Bot == 2): self.bot2 = DecisionBot(self.game.board, 'B')

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
    size = 32
    bot1 = 1
    bot2 = 2
    games = 1

    scoreA = 0
    scoreB = 0

    game = PawnChessGame(size, size)
    harness = PawnChessBotHarness(game, bot1, bot2)

    for i in range(games):
        game = PawnChessGame(size, size)
        harness.game = game

        while (game.winner == ' '): harness.process_bots()
        print(f"Player {game.winner} won!\n\n\n")
        if (game.winner == 'A'): scoreA += 1
        elif (game.winner == 'B'): scoreB += 1

    print(f"Player A won {scoreA} times and player B {scoreB} times")

if __name__ == "__main__":
    main()
