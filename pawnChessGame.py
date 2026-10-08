class PawnChessGame:
    def __init__(self, width: int = 3, height: int = 3):
        # Width/Height of board
        self.width = width
        self.height = height

        # Resset board
        self.board = [[' ' for x in range(self.width)] for y in range(self.height)] 
        for x in range(self.width):
            self.board[0][x] = 'A'
            self.board[self.height-1][x] = 'B'

        # Resset how many pawns each player has
        self.PawnCountA = len(self.board[0])
        self.PawnCountB = len(self.board[0])
    
        # Resset who is now and who won
        self.currentlyPlaying = 'A'
        self.winner = ' '

    def print_board(self):
        for y in range(self.height):
            for x in range(self.width-1):
                print(f"{self.board[y][x]}|", end="")
            print(f"{self.board[y][self.width-1]}")
        print(f"Turn of {self.currentlyPlaying}")

    def move_pawn(self, player: str, x1: int, y1: int, x2: int, y2: int):
        # Check if legal move
        if (self.winner != ' '):
            raise Exception(f"Game is already over! ({self.winner} won)")
        if (player != self.currentlyPlaying):
            raise Exception(f"It is not {player}'s turn right now!")
        moves = self.available_moves(player)
        if (not ({'origin': {'x': x1, 'y': y1}, 'target': {'x': x2, 'y': y2}} in moves)):
            raise Exception(f"Is illegal move: {x1}:{y1} to {x2}:{y2}!")

        mox = x1
        moy = y1
        mtx = x2
        mty = y2

        # Remove one pawn from other player if capturing
        if (self.board[mty][mtx] == 'A'): self.PawnCountA -= 1
        if (self.board[mty][mtx] == 'B'): self.PawnCountB -= 1

        # Apply move
        self.board[mty][mtx] = self.board[moy][mox]
        self.board[moy][mox] = ' ';

        self.check_win()
        self.print_board()

        # Change who is
        if (self.currentlyPlaying == 'A'): self.currentlyPlaying = 'B'
        elif (self.currentlyPlaying == 'B'): self.currentlyPlaying = 'A'

    def check_win(self):
        # 1. When oponent does not have any bauer left
        if (self.PawnCountA <= 0): self.winner = 'B'
        if (self.PawnCountB <= 0): self.winner = 'A'

        # 2. Reached the other side
        if ('B' in self.board[0]): self.winner = 'B';
        if ('A' in self.board[self.height-1]): self.winner = 'A';

        # 3. No moves possible
        if (self.currentlyPlaying == 'A'):
            if (len(self.available_moves('B')) <= 0): self.winner = 'A'
        if (self.currentlyPlaying == 'B'):
            if (len(self.available_moves('A')) <= 0): self.winner = 'B'

    def available_moves(self, player: str):
        availableMoves = []

        for y in range(0, self.height):
            for x in range(0, self.width):
                bauer = self.board[y][x]

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
                        if (posX < 0 or posX >= self.width or
                            posY < 0 or posY >= self.height):
                            continue

                        # Check if would bump into team mate
                        if (self.board[posY][posX] == player):
                            continue

                        # Check if bump into other bauer only when walking straight
                        # Or if there are bauers to capture on the sides
                        if (offsetX == -1):
                            if (self.board[posY][posX] == ' ' or self.board[posY][posX] == player):
                                continue

                        elif (offsetX == 0):
                            if (self.board[posY][posX] != ' '):
                                continue

                        elif (offsetX == 1):
                            if (self.board[posY][posX] == ' ' or self.board[posY][posX] == player):
                                continue

                        # If sucess add as posibilitie
                        availableMoves.append(
                            {
                                'origin': {'x': x, 'y': y},
                                'target': {'x': posX, 'y': posY}
                            })

        return availableMoves
