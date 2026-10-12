import random
from bots.NoBot import NoBot

class RngBot(NoBot):
    def __init__(self, initBoard, player: str):
        pass
    def decide_move(self, board, options):
        print("RNG bot decided move")
        return options[random.randint(0, len(options)-1)]
