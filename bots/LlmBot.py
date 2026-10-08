from bots.NoBot import NoBot
from ollama import Client
import json
import re
import random

class LlmBot(NoBot):
    def __init__(self, initBoard, player):
        self.messages = [
                {
                  'role': 'system',
                  'content': f'Answear only in json syntax. No other words outside of that syntax. Follow precisly what is wanted from you. Do not respond to this message, respond to the game ones but in json format. You are playing a game of pawn chess. Your goal is to win. You do it by a: reach other side of board, b: make opponent unable to move or c: capture all pawns of opponent. You get a json 2d array representing the board and a array of options possible/legal moves. Choose on of those and echo it formatted back into an 4 elements 1d array for example: You can respond with [ 0, 0, 0, 1 ] to move a pawn in upper left corner (0:0) foreward (0:1). But only repsond with one array with length 4, nothing different or you will lose and get a bad score i pleade you!. You are player {player}. ONLY RESPOND IN 4 ELEMENT LONG ARRAYS TELLING THE GAME YOUR CHOOSEN MOVE IN COORDINATS ( "[ x1, y1, x2, y2 ]" ). The board 0:0 is top left corner. The board 2d array is first for y second layer for x.',
                }
            ]

    def decide_move(self, board, options):
        easyToUnderstandOptions = []
        for opt in options:
            easyToUnderstandOptions.append([ opt['origin']['x'],opt['origin']['y'],opt['target']['x'],opt['target']['y'] ])

        for i in range(0, 5):
            self.messages.append({ 'role': 'user' , 'content': f"The board looks like this: {json.dumps(board)} your options are: {easyToUnderstandOptions}. Chose ONE of those options and respond. An option is ONLY 4 ELEMENTS long array" })

            client = Client(host='http://localhost:11434', headers={'x-some-header': 'some-value'})
            response = client.chat(
                model='gemma3:270m',
                messages=self.messages,
            )

            try:
                # Filter to json
                text = response['message']['content']
                print(f"Original text: {text}")
                match = re.search(r"\[\s*-?\d+(?:\s*,\s*-?\d+){3}\s*\]", text)
                move = match.group()
                print(f"Move found: {move}")
                move = json.loads(move)
                print(f"Move found to python obj: {move}")

                neededMoveInst = { 'origin': { 'x': move[0], 'y': move[1] }, 'target': { 'x': move[2], 'y': move[3] } }

                # Make sure move is legal
                for opt in options:
                    if (neededMoveInst == opt):
                        return neededMoveInst
                
                self.messages.append({ 'role': 'system', 'content': f'Not a valid option {move} please pic a real option now' })

            except:
                self.messages.append({ 'role': 'system', 'content': f'Not a valid response please only write json syntax of one list with 4 elements those elements are all decimal int numbers' })

        self.messages.append({ 'role': 'system', 'content': f'You took too long (over 5 tries). Choosing at random for you' })
        return options[random.randint(0, len(options)-1)]
