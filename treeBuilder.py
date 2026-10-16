from pawnChessGame import PawnChessGame
import copy
import tkinter as tk
from tkinter import ttk

def build_tree():
    posMoves = 0

    def makeTree(board, turnOf, moveMade=None):
        nonlocal posMoves
        game = PawnChessGame(len(board[0]), len(board))
        game.winner = ' '
        game.currentlyPlaying = turnOf
        game.board = board

        game.check_win()

        posMoves += 1

        # A terminal win contributes one outcome to that winner.
        if game.winner != ' ':
            return {
                'board': board,
                'branches': None,
                'winner': game.winner,
                'aWins': int(game.winner == 'A'),
                'bWins': int(game.winner == 'B'),
                'moveMade': moveMade,
            }

        # Keep your existing convention: turnOf is the previous player,
        # so the other player moves next.
        nextTurn = 'B' if turnOf == 'A' else 'A'
        availMoves = game.available_moves(nextTurn)

        if not availMoves:
            return {
                'board': board,
                'branches': None,
                'winner': None,
                'aWins': 0,
                'bWins': 0,
                'moveMade': moveMade,
            }

        branches = []
        for mov in availMoves:
            newBoard = copy.deepcopy(board)
            y0, x0 = mov['origin']['y'], mov['origin']['x']
            y1, x1 = mov['target']['y'], mov['target']['x']

            newBoard[y1][x1] = newBoard[y0][x0]
            newBoard[y0][x0] = ' '

            branches.append(makeTree(newBoard, nextTurn, mov))

        # Every child subtree contributes its terminal win counts.
        aWins = sum(branch['aWins'] for branch in branches)
        bWins = sum(branch['bWins'] for branch in branches)

        # Keep winner only when every child has the same known result.
        childWinners = [branch['winner'] for branch in branches]
        winner = childWinners[0] if all(w == childWinners[0] for w in childWinners) else None

        return {
            'board': board,
            'branches': branches,
            'winner': winner,
            'aWins': aWins,
            'bWins': bWins,
            'moveMade': moveMade,
        }

    game = PawnChessGame(3, 3)
    tree = makeTree(game.board, 'B')

    print(f"Possible moves: {posMoves}")

    return tree

def show_tree(tree):
    cell_size = 20
    box_padding = 4
    level_gap = 16
    sibling_gap = 12

    box_width = len(tree['board'][0]) * cell_size + 2 * box_padding
    box_height = len(tree['board']) * cell_size + 2 * box_padding

    root = tk.Tk()
    root.title("Pawn Chess Game Tree")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, background="white")
    x_scroll = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    y_scroll = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(
        xscrollcommand=x_scroll.set,
        yscrollcommand=y_scroll.set,
    )

    canvas.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Convert the input into a consistent node format.
    def prepare(item, depth=0):
        if item is None:
            return None

        node = {
            "board": item["board"],
            "winner": item.get("winner"),
            "children": [],
        }

        for branch in item.get("branches") or []:
            child = prepare(branch, depth + 1)
            if child is not None:
                node["children"].append(child)

        return node

    root_node = prepare(tree)

    if root_node is None:
        root.destroy()
        return

    # Assign x positions: leaves get their own slots; parent nodes are
    # centered over their children. y position is determined by depth.
    leaves = [0]

    def layout(node, depth=0):
        node["depth"] = depth

        if not node["children"]:
            node["x"] = leaves[0]
            leaves[0] += box_width + sibling_gap
        else:
            for child in node["children"]:
                layout(child, depth + 1)

            first_x = node["children"][0]["x"]
            last_x = node["children"][-1]["x"]
            node["x"] = (first_x + last_x) / 2

    layout(root_node)

    # Draw connectors first so the lines appear behind the board boxes.
    def draw_edges(node):
        parent_x = node["x"] + box_width / 2
        parent_y = node["depth"] * (box_height + level_gap) + box_height

        for child in node["children"]:
            child_x = child["x"] + box_width / 2
            child_y = child["depth"] * (box_height + level_gap)

            canvas.create_line(
                parent_x, parent_y,
                child_x, child_y,
                fill="#555555",
                width=2,
            )
            draw_edges(child)

    def draw_nodes(node):
        x = node["x"]
        y = node["depth"] * (box_height + level_gap)
        board = node["board"]

        # Outer box around the board.
        winner = node["winner"]

        if winner == "A":
            outline_color = "red"
        elif winner == "B":
            outline_color = "green"
        else:
            outline_color = "#888888"  # draw or undecided

        canvas.create_rectangle(
            x, y, x + box_width, y + box_height,
            fill="white",
            outline=outline_color,
            width=4,
        )

        # Draw the board cells and their contents.
        for row in range(len(node['board'])):
            for col in range(len(node['board'][0])):
                left = x + box_padding + col * cell_size
                top = y + box_padding + row * cell_size

                canvas.create_rectangle(
                    left, top,
                    left + cell_size, top + cell_size,
                    fill="white",
                    outline="#777777",
                )

                value = str(board[row][col]).strip()
                if value:
                    canvas.create_text(
                        left + cell_size / 2,
                        top + cell_size / 2,
                        text=value,
                        font=("TkDefaultFont", 12, "bold"),
                    )

        for child in node["children"]:
            draw_nodes(child)

    draw_edges(root_node)
    draw_nodes(root_node)

    total_width = max(leaves[0], box_width + 20)
    max_depth_found = max_node_depth(root_node)
    total_height = (max_depth_found + 1) * (box_height + level_gap)

    canvas.configure(scrollregion=(0, 0, total_width, total_height))
    root.mainloop()


def max_node_depth(node):
    if not node["children"]:
        return node["depth"]
    return max(max_node_depth(child) for child in node["children"])

if __name__ == "__main__":
    tree = build_tree()
    show_tree(tree)
    print(tree)
