import json
import random
import copy
import math

from bots.NoBot import NoBot

def sigmoid(x):
    x = max(-60, min(60, x))
    return 1 / (1 + math.exp(-x))

class Nn:
    def __init__(self):
        self.nn = []

    def add_layer(self, neuronsCount, bias):
        # Add input layer if no layers exist
        if (self.nn == []):
            neurons = []
            for i in range(neuronsCount): neurons.append({ 'value': 0, 'bias': bias, 'weigths': [] })
            self.nn.append(neurons)
            return
        
        # Add hidden output layer/hidden layer
        neurons = []
        for i in range(neuronsCount):
            weigths = []
            for i in range(len(self.nn[-1])): weigths.append(random.random())
            neurons.append({ 'value': 0, 'bias': bias, 'weigths': weigths })
        self.nn.append(neurons)
    
    def process(self, inputs):
        for i in range(len(self.nn[0])):
            self.nn[0][i]['value'] = inputs[i]

        # Go through every layer and every neuron and every weigth
        for layer in range(1, len(self.nn)):
            for neuron in range(len(self.nn[layer])):

                val = self.nn[layer][neuron]['bias']
                for weigth in range(len(self.nn[layer][neuron]['weigths'])):
                    val += self.nn[layer-1][weigth]['value'] * self.nn[layer][neuron]['weigths'][weigth]

                self.nn[layer][neuron]['value'] = sigmoid(val)

        # Return result of output layer
        out = []
        for neuron in self.nn[-1]:
            out.append(neuron['value'])
        return out

    def backup(self):
        self.nnBackup = copy.deepcopy(self.nn)

    def restore(self):
        self.nn = copy.deepcopy(self.nnBackup)

    def mutate(self, amount=0.5):
        layer_index = random.randrange(1, len(self.nn))
        neuron = random.choice(self.nn[layer_index])

        if random.choice([True, False]):
            weight_index = random.randrange(len(neuron['weigths']))
            neuron['weigths'][weight_index] += random.uniform(-amount, amount)
        else:
            neuron['bias'] += random.uniform(-amount, amount)


class NnBot(NoBot):
    def __init__(self, initBoard, player):
        self.player = player

        self.height = len(initBoard)
        self.width = len(initBoard[0])

        self.nn = Nn()
        self.nn.add_layer(self.width*self.height+1, 0)
        self.nn.add_layer(self.width*self.height*2, 0)
        self.nn.add_layer(self.width*self.height, 0)
        self.nn.add_layer(round(self.width*self.height/2), 0)
        self.nn.add_layer(4, 0)
        self.nn.backup()
        print(f"Neural Network: {json.dumps(self.nn.nn, indent=4)}")

    def decide_move(self, board, options):
        while True:
            # Build input
            board1d = f = [i for s in board for i in s]
            inputs = [self.player]
            inputs.extend(board1d)

            for i in range(len(inputs)):
                if (inputs[i] == 'A'): inputs[i] = 1
                elif (inputs[i] == 'B'): inputs[i] = 2
                elif (inputs[i] == ' '): inputs[i] = 0

            print(f"Given inputs {inputs}")

            rs = self.nn.process(inputs)

            rOX = round(1/3/rs[0])
            if (rOX > 1): rOX = 1
            rOY = round(1/3/rs[1])
            if (rOY > 1): rOY = 1
            rTX = round(1/3/rs[2])
            if (rTX > 1): rTX = 1
            rTY = round(1/3/rs[3])
            if (rTY > 1): rTY = 1

            print(f"From {rOX}:{rOY} to {rTX}:{rTY}")

            proposedMove = { "origin": { 'x': rOX, 'y': rOY }, "target": { 'x': rTX, 'y': rTY } }

            if (proposedMove in options):
                return proposedMove

            self.nn.mutate()

    def board_changed(self, board):
        pass

    def lost(self):
        self.nn.restore()
        self.nn.mutate()

    def won(self):
        self.nn.backup()
        self.nn.mutate()

    def resset(self):
        pass

    def info_print(self):
        pass
