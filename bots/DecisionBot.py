import random
from bots.NoBot import NoBot

class DecisionBot(NoBot):
    def __init__(self, initBoard, player: str):
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
