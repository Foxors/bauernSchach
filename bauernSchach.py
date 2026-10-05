import random
from time import sleep

board = [
    [ 'A', 'A', 'A' ],
    [ ' ', ' ', ' ' ],
    [ 'B', 'B', 'B' ]
]

BauerCountA = len(board[0])
BauerCountB = len(board[0])

currentlyPlaying = 'A'


def move(x1: int, y1: int, x2: int, y2: int):
    if (x1 < 0 or x1 >= 3 or
        y1 < 0 or y1 >= 3 or
        x2 < 0 or x2 >= 3 or
        y2 < 0 or y2 >= 3):
        return False

    board[y2][x2] = board[y1][x1]
    board[y1][x1] = ' ';

    return True

def available_moves(player: str):
    availableMoves = []

    for y in range(0, len(board)):
        for x in range(0, len(board[y])):
            bauer = board[y][x]

            if (player == bauer):
                # Go through every move this bauer can do
                for offsetX in range(-1, 2, 1):
                    # Figure out world coordinats
                    posX = x + offsetX;
                    posY = y;

                    # move up or down depending on player
                    if (player == 'A'):
                        posY += 1;
                    else:
                        posY -= 1;

                    # Check if on grid
                    if (posX < 0 or posX >= 3 or
                        posY < 0 or posY >= 3):
                        continue
                    
                    # Check if would bump into team mate
                    if (board[posY][posX] == player):
                        continue

                    # Check if bump into other bauer only when walking straight
                    if (offsetX == 0):
                        if (board[posY][posX] != ' '):
                            continue

                    # If sucess add as posibilitie
                    availableMoves.append([x, y, posX, posY])

    return availableMoves

def check_winner():
    # 1. When oponent does not have any bauer left
    if (BauerCountA <= 0): return 'B'
    if (BauerCountB <= 0): return 'A'

    # 2. Reached the other side
    if ('B' in board[0]): return 'B';
    if ('A' in board[len(board)-1]): return 'A';

    # 3. No moves possible
    if (len(available_moves('A')) <= 0): return 'B'
    if (len(available_moves('B')) <= 0): return 'A'

    return ' '

def print_board():
    for i in board:
        print(i)



print_board()

while True:
    moves = available_moves(currentlyPlaying)

    if (len(moves) <= 0):
        break

    nextMove = moves[random.randint(0, len(moves)) - 1]
    x1 = nextMove[0]
    y1 = nextMove[1]
    x2 = nextMove[2]
    y2 = nextMove[3]

    print(f'{currentlyPlaying} makes move: {nextMove}')

    move(x1, y1, x2, y2)
    print_board()

    winner = check_winner()
    if (winner != ' '):
        print(f'The winner is {winner}!')
        break

    sleep(1)

    if (currentlyPlaying == 'A'):
        currentlyPlaying = 'B'
    else:
        currentlyPlaying = 'A'
