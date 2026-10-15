import random
import copy
import json
import tkinter as tk

from bots.NoBot import NoBot
from pawnChessGame import PawnChessGame

class ExploreBot(NoBot):
    def __init__(self, initBoard, player):

        self.width = len(initBoard[0])
        self.height = len(initBoard)

        self.player = player

        self.tree = { 'board': copy.deepcopy(initBoard), 'winner': None, 'aWins': 0, 'bWins': 0, 'branches': None }
        self.myBranch = self.tree

        self.exploration_chance = 0.15
        self.gamePath = []

    def decide_move(self, board, options):
        # Fill out board
        if (self.myBranch['board'] == None):
            self.myBranch['board'] = copy.deepcopy(board)

        # Fill out sub branches
        if (self.myBranch['branches'] == None):
            subBranches = []
            for o in options:
                game = PawnChessGame(self.width, self.height)
                game.board = copy.deepcopy(self.myBranch['board'])
                game.currentlyPlaying = self.player
                game.move_pawn(self.player, o['origin']['x'], o['origin']['y'], o['target']['x'], o['target']['y'])
                subBranches.append({ 'board': game.board, 'winner': None, 'aWins': 0, 'bWins': 0, 'branches': None, 'moveToHere': o })
            self.myBranch['branches'] = subBranches


        branches = self.myBranch['branches']

        # 1. If a branch is already guaranteed winning take it.
        for index, subBranch in enumerate(branches):
            if subBranch['winner'] == self.player:
                self.myBranch = subBranch
                self.gamePath.append(index)
                return copy.deepcopy(self.myBranch['moveToHere'])

        # Avoid known guaranteed losses
        safe_indexes = []
        for index, subBranch in enumerate(branches):
            if (subBranch['winner'] == self.player or subBranch['winner'] == None):
                safe_indexes.append(index)
        # If all branches are known losses we still choose at random and accept the fate
        if len(safe_indexes) == 0:
            safe_indexes = list(range(len(branches)))

        # Sometimes try other branches.
        if random.random() < self.exploration_chance:
            unknown_indexes = []

            for index in safe_indexes:
                branch = branches[index]

                if branch['winner'] is None and branch['aWins'] + branch['bWins'] == 0:
                    unknown_indexes.append(index)

            if len(unknown_indexes) > 0:
                chosen_index = random.choice(unknown_indexes)
            else:
                chosen_index = random.choice(safe_indexes)

            self.myBranch = branches[chosen_index]
            self.gamePath.append(chosen_index)
            return copy.deepcopy(self.myBranch['moveToHere'])

        # Find porb. best option
        best_indexes = []
        best_score = -999999

        for index in safe_indexes:
            branch = branches[index]

            aWins = branch['aWins'] + 1
            bWins = branch['bWins'] + 1

            totalWins = aWins + bWins

            if self.player == 'A':
                score = aWins / totalWins
            else:
                score = bWins / totalWins

            if score > best_score:
                best_score = score
                best_indexes = [index]

            elif score == best_score:
                best_indexes.append(index)

        # Random tie-breaker.
        chosen_index = random.choice(best_indexes)

        self.myBranch = branches[chosen_index]
        self.gamePath.append(chosen_index)

        return copy.deepcopy(self.myBranch['moveToHere'])

    def board_changed(self, board):
        oppositePlayer = 'A'
        if (self.player == 'A'): oppositePlayer = 'B'
        elif (self.player == 'B'): oppositePlayer = 'A'

        # Fill out sub branches
        game = PawnChessGame(self.width, self.height)
        game.board = copy.deepcopy(self.myBranch['board'])
        options = game.available_moves(oppositePlayer)
        if (self.myBranch['branches'] == None):
            subBranches = []
            for o in options:
                game = PawnChessGame(self.width, self.height)
                game.board = copy.deepcopy(self.myBranch['board'])
                game.currentlyPlaying = oppositePlayer
                game.move_pawn(oppositePlayer, o['origin']['x'], o['origin']['y'], o['target']['x'], o['target']['y'])
                subBranches.append({ 'board': game.board, 'winner': None, 'aWins': 0, 'bWins': 0, 'branches': None, 'moveToHere': o })
            self.myBranch['branches'] = subBranches

        # Find the corresponding sub branch
        i = 0
        for branch in self.myBranch['branches']:
            if (branch['board'] == board):
                self.myBranch = branch
                self.gamePath.append(i)
                return
            i += 1

        print(f"SOMETHING WENT HORRIBLE WRONG WITH THE EXPLORE BOT (TREE IS OUT OF SYNC) I AM {self.player} and my branches is {self.myBranch}")
        return

    def propagate_result(self, winner):
        print(f"Propagating... {self.gamePath} len = {len(self.gamePath)}")

        treeCut = []
        elem = self.tree
        for decision in self.gamePath:
            treeCut.insert(0, elem)
            elem = elem['branches'][decision]

        # Count wins on this end
        if winner == 'A': self.myBranch['aWins'] += 1
        elif winner == 'B': self.myBranch['bWins'] += 1

        for elem in treeCut:
            # Count wins on this path
            if winner == 'A': elem['aWins'] += 1
            elif winner == 'B': elem['bWins'] += 1

            # Check if path garanteed win or loss
            winOrLos = elem['winner']
            itIsSame = True
            for branch in elem['branches']:
                if (branch['winner'] != winOrLos): itIsSame = False
            if (itIsSame == True): elem['winner'] = winOrLos

    def won(self):
        print("Win signal")
        self.myBranch['winner'] = self.player
        self.propagate_result(self.player)

    def lost(self):
        print("Lost signal")
        oppositePlayer = 'A'
        if (self.player == 'A'): oppositePlayer = 'B'
        self.myBranch['winner'] = oppositePlayer
        self.propagate_result(oppositePlayer)

    def resset(self, initBoard, player):
        print("GOT RESSET")
        self.player = player
        self.gamePath = []
        self.myBranch = self.tree
        print(f"I am {player} now")

    def info_print(self):
        print("ExploreBot")
        print(f"Player: {self.player}")
        show_explore_tree(self.tree, self.player)

def show_explore_tree(tree, bot_player):
    cell_size = 24
    box_padding = 6
    level_gap = 60
    sibling_gap = 30

    if tree is None:
        print("Tree is empty.")
        return

    board_height = len(tree["board"])
    board_width = len(tree["board"][0])

    box_width = board_width * cell_size + 2 * box_padding
    box_height = board_height * cell_size + 2 * box_padding

    root = tk.Tk()
    root.title("ExploreBot Learned Tree")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, background="white")

    x_scroll = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    y_scroll = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)

    canvas.configure(
        xscrollcommand=x_scroll.set,
        yscrollcommand=y_scroll.set
    )

    canvas.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    leaf_x = [30]

    def layout(node, depth=0):
        node["_depth"] = depth

        branches = node.get("branches") or []

        if len(branches) == 0:
            node["_x"] = leaf_x[0]
            leaf_x[0] += box_width + sibling_gap
        else:
            for child in branches:
                layout(child, depth + 1)

            first_x = branches[0]["_x"]
            last_x = branches[-1]["_x"]

            node["_x"] = (first_x + last_x) / 2

        node["_y"] = 30 + depth * (box_height + level_gap)

    def max_depth(node):
        branches = node.get("branches") or []

        if len(branches) == 0:
            return node["_depth"]

        return max(max_depth(child) for child in branches)

    def node_outline_color(node):
        opponent = "B" if bot_player == "A" else "A"

        if node.get("winner") == bot_player:
            return "green"

        if node.get("winner") == opponent:
            return "red"

        return "navy"

    def edge_color(child):
        opponent = "B" if bot_player == "A" else "A"

        if child.get("winner") == bot_player:
            return "green"

        if child.get("winner") == opponent:
            return "red"

        return "orange"

    def draw_edges(node):
        branches = node.get("branches") or []

        parent_x = node["_x"] + box_width / 2
        parent_y = node["_y"] + box_height

        for child in branches:
            child_x = child["_x"] + box_width / 2
            child_y = child["_y"]

            color = edge_color(child)

            canvas.create_line(
                parent_x,
                parent_y,
                child_x,
                child_y,
                fill=color,
                width=3 if color == "red" else 2,
                arrow=tk.LAST
            )

            mid_x = (parent_x + child_x) / 2
            mid_y = (parent_y + child_y) / 2

            canvas.create_text(
                mid_x,
                mid_y - 8,
                fill=color,
                font=("TkDefaultFont", 8, "bold")
            )

            draw_edges(child)

    def draw_node(node):
        x = node["_x"]
        y = node["_y"]

        board = node["board"]

        canvas.create_rectangle(
            x,
            y,
            x + box_width,
            y + box_height,
            fill="white",
            outline=node_outline_color(node),
            width=4
        )

        if (board != None):
            for row in range(len(board)):
                for col in range(len(board[row])):
                    left = x + box_padding + col * cell_size
                    top = y + box_padding + row * cell_size

                    canvas.create_rectangle(
                        left,
                        top,
                        left + cell_size,
                        top + cell_size,
                        fill="white",
                        outline="#777777"
                    )

                    value = board[row][col]

                    if value != " ":
                        text_color = "black"

                        if value == bot_player:
                            text_color = "blue"

                        canvas.create_text(
                            left + cell_size / 2,
                            top + cell_size / 2,
                            text=value,
                            fill=text_color,
                            font=("TkDefaultFont", 12, "bold")
                        )

        label_parts = []

        label_parts.append(f"A:{node.get('aWins', "IDk")} B:{node.get('bWins', "IDK")}")

        if node.get("winner") is not None:
            label_parts.append(f"winner: {node['winner']}")

        if len(label_parts) > 0:
            canvas.create_text(
                x + box_width / 2,
                y + box_height + 12,
                text=" | ".join(label_parts),
                fill=node_outline_color(node),
                font=("TkDefaultFont", 8, "bold")
            )

        for child in node.get("branches") or []:
            draw_node(child)

    layout(tree)

    draw_edges(tree)
    draw_node(tree)

    total_width = max(leaf_x[0] + 100, 900)
    total_height = max(
        60 + (max_depth(tree) + 1) * (box_height + level_gap),
        700
    )

    canvas.configure(scrollregion=(0, 0, total_width, total_height))

    root.mainloop()
