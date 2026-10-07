class TreeBot(NoBot):
    def __init__(self, board, bot_player):
        self.bot_player = bot_player

        # Each state stores its legal moves and the state reached by each move.
        # State format: (player_to_move, board_tuple)
        self.tree = {}

        # Moves made by this bot in the current game:
        # [(state_key, move_tuple), ...]
        self.game_path = []

        # The bot's most recent move, pending confirmation that it was applied.
        self.pending = None

    def position_key(self, board, player_to_move):
        return (player_to_move, tuple(tuple(row) for row in board))

    def _get_node(self, key):
        return self.tree.setdefault(
            key,
            {"moves": {}, "status": "unknown"}
        )

    def _record_result(self, key, move, result):
        node = self.tree.get(key)
        if node is None or move not in node["moves"]:
            return

        edge = node["moves"][move]
        edge["observed"] = result

    def _propagate_results(self):
        changed = True

        while changed:
            changed = False

            for key, node in self.tree.items():
                old_status = node["status"]
                outcomes = []

                for edge in node["moves"].values():
                    child_key = edge.get("child")
                    if child_key in self.tree:
                        outcomes.append(self.tree[child_key]["status"])

                if "lost" in outcomes:
                    node["status"] = "won"
                elif node["moves"] and all(
                    edge.get("child") in self.tree
                    and self.tree[edge["child"]]["status"] == "won"
                    for edge in node["moves"].values()
                ):
                    node["status"] = "lost"

                if node["status"] != old_status:
                    changed = True

    def _finish_game(self, result):
        # The pending move may be the one that ended the game.
        if self.pending is not None:
            self.game_path.append(self.pending)
            self.pending = None

        for key, move in self.game_path:
            self._record_result(key, move, result)

        self._propagate_results()
        self.game_path = []

    def make_move(self, board, options):
        if not options:
            return [0, 0, 0, 0]

        key = self.position_key(board, self.bot_player)
        node = self._get_node(key)

        # The previous move was applied if the bot has reached another turn.
        if self.pending is not None:
            self.game_path.append(self.pending)
            self.pending = None

        # Record all currently legal moves without discarding learned data.
        for option in options:
            move = tuple(option)
            node["moves"].setdefault(
                move,
                {"child": None, "observed": "unknown"}
            )

        # Prefer moves whose resulting states are not proven wins for the
        # opponent. If no such move is known, explore any legal move.
        safe = []
        unknown = []

        for option in options:
            move = tuple(option)
            edge = node["moves"][move]
            child_key = edge.get("child")

            if child_key is None or child_key not in self.tree:
                unknown.append(option)
            elif self.tree[child_key]["status"] != "won":
                safe.append(option)

        if safe:
            choices = safe
        elif unknown:
            choices = unknown
        else:
            choices = list(options)

        move = list(random.choice(choices))
        self.pending = (key, tuple(move))
        return move

    def lost(self):
        self._finish_game("lost")

    def won(self):
        self._finish_game("won")
    
    def observe_resulting_position(self, board, player_to_move):
        if self.pending is None:
            return

        key, move = self.pending
        node = self.tree.get(key)

        if node is not None and move in node["moves"]:
            child_key = self.position_key(board, player_to_move)
            node["moves"][move]["child"] = child_key

        # Keep pending until make_move() is called again, so the move is
        # included in game_path then. If the game ends immediately,
        # won()/lost() will include it.
        self._propagate_results()
