import copy
import random

import matplotlib.pyplot as plt

from bots.NoBot import NoBot

class TreeBot(NoBot):
    def __init__(self, initBoard, player):
        self.tree = {
            "board": copy.deepcopy(initBoard),
            "branches": [],
        }
        self.stack = []
        self.player = player

    def get_deepest_elem(self):
        elem = self.tree

        for index in self.stack:
            if index >= len(elem["branches"]):
                return None

            elem = elem["branches"][index]["branch"]
            if elem is None:
                return None

        return elem

    def _add_options(self, elem, options):
        # Add candidate moves to a node if it has no branches yet.
        if not elem["branches"]:
            elem["branches"] = [
                {
                    "move": copy.deepcopy(option),
                    "branch": None,
                    "winnable": True,
                }
                for option in options
            ]

    def decide_move(self, board, options):
        elem = self.get_deepest_elem()

        # A child node may not exist yet if this is the first visit.
        if elem is None:
            elem = {
                "board": copy.deepcopy(board),
                "branches": [],
            }

            if self.stack:
                parent = self.get_deepest_elem()
                if parent is not None:
                    parent["branch"] = elem
            else:
                self.tree = elem

        self._add_options(elem, options)

        # Pick the first branch not previously marked as losing.
        for index, branch in enumerate(elem["branches"]):
            if branch["winnable"]:
                return branch["move"]

        # All known branches are marked losing, so fall back to a legal move.
        if options:
            return random.choice(options)

        # No legal moves are available. (result in error bc. of parent program)
        return None

    def board_changed(self, board, options, decidedOption):
        elem = self.get_deepest_elem()

        if elem is None:
            elem = {
                "board": copy.deepcopy(board),
                "branches": [],
            }
            if self.stack:
                parent = self.get_deepest_elem()
                if parent is not None:
                    parent["branch"] = elem
            else:
                self.tree = elem

        self._add_options(elem, options)

        # Find the branch corresponding to the move that was played.
        branch_index = next(
            (
                index
                for index, branch in enumerate(elem["branches"])
                if branch["move"] == decidedOption
            ),
            None,
        )

        # The move may not have been among the options initially recorded.
        if branch_index is None:
            elem["branches"].append({
                "move": copy.deepcopy(decidedOption),
                "branch": None,
                "winnable": True,
            })
            branch_index = len(elem["branches"]) - 1

        # Create or update the node reached by that move.
        branch = elem["branches"][branch_index]
        if branch["branch"] is None:
            branch["branch"] = {
                "board": copy.deepcopy(board),
                "branches": [],
            }
        else:
            branch["branch"]["board"] = copy.deepcopy(board)

        self.stack.append(branch_index)

    def lost(self):
        # The final index in the stack identifies the last move's branch.
        if not self.stack:
            return

        elem = self.tree
        for index in self.stack[:-1]:
            if index >= len(elem["branches"]):
                return
            elem = elem["branches"][index]["branch"]
            if elem is None:
                return

        last_index = self.stack[-1]
        if last_index < len(elem["branches"]):
            elem["branches"][last_index]["winnable"] = False

    def won(self):
        pass

    def resset(self):
        self.stack.clear()


    def info_print(self):
        """
        Tree looks like:
        {
            "board": ...,
            "branches": [
                {"move": ..., "branch": ..., "winnable": True}
            ]
        }
        """
        
        figsize = (16, 10)
        node_fontsize = 7
        move_fontsize = 6

        positions = {}
        edges = []
        next_x = 0

        def move_label(move):
            origin = move.get("origin", {})
            target = move.get("target", {})
            return (
                f"({origin.get('x')},{origin.get('y')})"
                f"→({target.get('x')},{target.get('y')})"
            )

        def board_label(board):
            return "\n".join("".join(str(cell) for cell in row) for row in board)

        def layout(node, depth=0):
            nonlocal next_x

            branches = node.get("branches", [])

            # A leaf gets the next horizontal position.
            child_positions = []
            for branch in branches:
                child = branch.get("branch")
                if child is not None:
                    child_x = layout(child, depth + 1)
                    child_positions.append(child_x)

                    edges.append({
                        "parent": node,
                        "child": child,
                        "move": branch.get("move", {}),
                        "winnable": branch.get("winnable", True),
                    })

            if child_positions:
                x = sum(child_positions) / len(child_positions)
            else:
                x = next_x
                next_x += 1

            positions[id(node)] = (x, -depth)
            return x

        layout(self.tree)

        fig, ax = plt.subplots(figsize=figsize)

        # Draw edges and move labels.
        for edge in edges:
            x1, y1 = positions[id(edge["parent"])]
            x2, y2 = positions[id(edge["child"])]

            color = "green" if edge["winnable"] else "red"
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.2, zorder=1)

            label = move_label(edge["move"])
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                label,
                fontsize=move_fontsize,
                ha="center",
                va="center",
                color=color,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8},
            )

        # Draw board nodes.
        nodes = {}

        def collect_nodes(node):
            nodes[id(node)] = node
            for branch in node.get("branches", []):
                child = branch.get("branch")
                if child is not None:
                    collect_nodes(child)

        collect_nodes(self.tree)

        for node_id, node in nodes.items():
            x, y = positions[node_id]
            label = board_label(node.get("board", []))

            ax.text(
                x,
                y,
                label,
                fontsize=node_fontsize,
                ha="center",
                va="center",
                family="monospace",
                bbox={
                    "boxstyle": "round,pad=0.35",
                    "facecolor": "white",
                    "edgecolor": "black",
                },
                zorder=2,
            )

        ax.set_title("Pawn Chess decision tree")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
