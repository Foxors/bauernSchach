import random
import copy
import torch
import torch.nn as nn
import torch.optim as optim

from bots.NoBot import NoBot


class ActorCriticNetwork(nn.Module):
    def __init__(self, width, height):
        super().__init__()

        self.width = width
        self.height = height
        self.square_count = width * height

        # Board input:
        board_input_size = self.square_count * 2

        # Move input:
        #
        # first square_count values  = origin square one-hot
        # second square_count values = target square one-hot
        #
        # plus 5 helper values:
        #   is_capture
        #   is_straight_forward
        #   is_left_diagonal
        #   is_right_diagonal
        #   target_progress
        move_input_size = self.square_count * 2 + 5

        board_hidden_size = 64
        move_hidden_size = 64
        combined_hidden_size = 64

        # Encodes the board state.
        self.board_fc1 = nn.Linear(board_input_size, board_hidden_size)
        self.board_fc2 = nn.Linear(board_hidden_size, board_hidden_size)

        # Encodes one candidate move.
        self.move_fc1 = nn.Linear(move_input_size, move_hidden_size)

        # Scores a board + move pair.
        self.score_fc1 = nn.Linear(
            board_hidden_size + move_hidden_size,
            combined_hidden_size
        )
        self.score_fc2 = nn.Linear(combined_hidden_size, 1)

        # Estimates how good the current board is.
        self.value_head = nn.Linear(board_hidden_size, 1)

        self.hidden_activation = nn.ReLU()

    def encode_board(self, board_tensor):
        if board_tensor.dim() == 1:
            board_tensor = board_tensor.unsqueeze(0)

        x = self.board_fc1(board_tensor)
        x = self.hidden_activation(x)

        x = self.board_fc2(x)
        x = self.hidden_activation(x)

        return x

    def score_moves(self, board_tensor, move_tensors):
        board_embedding = self.encode_board(board_tensor)

        # Repeat board embedding once per legal move.
        board_embedding = board_embedding.expand(move_tensors.shape[0], -1)

        move_embedding = self.move_fc1(move_tensors)
        move_embedding = self.hidden_activation(move_embedding)

        combined = torch.cat([board_embedding, move_embedding], dim=1)

        x = self.score_fc1(combined)
        x = self.hidden_activation(x)

        move_scores = self.score_fc2(x).squeeze(1)

        return move_scores

    def value(self, board_tensor):
        board_embedding = self.encode_board(board_tensor)
        position_value = self.value_head(board_embedding).squeeze()

        return position_value


class NnBot(NoBot):
    def __init__(self, initBoard, player):
        self.player = player

        self.width = None
        self.height = None
        self.square_count = None

        self.model = None
        self.optimizer = None

        # gamma to punish later moves more then early ones
        self.gamma = 0.95

        # Chance to choose a random legal move
        self.epsilon = 0.10

        # Softmax temperature.
        self.temperature = 1.0

        # Coefficients for actor-critic training.
        self.value_loss_coefficient = 0.5
        self.entropy_coefficient = 0.01

        self.episode_memory = []

        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0

        self.last_loss = None

        self.resset(initBoard, player)

    def _ensure_model_for_board(self, board):
        height = len(board)
        width = len(board[0])

        if (
            self.model is not None
            and self.width == width
            and self.height == height
        ):
            return

        self.width = width
        self.height = height
        self.square_count = width * height

        self.model = ActorCriticNetwork(width, height)

        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=0.003
        )

    def _actual_to_perspective_position(self, position):
        x = position["x"]
        y = position["y"]

        if self.player == "B":
            y = self.height - 1 - y

        return {
            "x": x,
            "y": y
        }

    def _perspective_to_index(self, position):
        x = position["x"]
        y = position["y"]

        if x < 0 or x >= self.width:
            return None

        if y < 0 or y >= self.height:
            return None

        return y * self.width + x

    def _board_to_tensor(self, board):
        own_values = []
        enemy_values = []

        for perspective_y in range(self.height):
            for perspective_x in range(self.width):
                actual_x = perspective_x
                actual_y = perspective_y

                if self.player == "B":
                    actual_y = self.height - 1 - perspective_y

                cell = board[actual_y][actual_x]

                if cell == self.player:
                    own_values.append(1.0)
                    enemy_values.append(0.0)

                elif cell == " ":
                    own_values.append(0.0)
                    enemy_values.append(0.0)

                else:
                    own_values.append(0.0)
                    enemy_values.append(1.0)

        input_values = own_values + enemy_values

        return torch.tensor(input_values, dtype=torch.float32)

    def _option_to_move_tensor(self, board, option):
        perspective_origin = self._actual_to_perspective_position(
            option["origin"]
        )
        perspective_target = self._actual_to_perspective_position(
            option["target"]
        )

        origin_index = self._perspective_to_index(perspective_origin)
        target_index = self._perspective_to_index(perspective_target)

        if origin_index is None or target_index is None:
            return None

        origin_values = [0.0 for _ in range(self.square_count)]
        target_values = [0.0 for _ in range(self.square_count)]

        origin_values[origin_index] = 1.0
        target_values[target_index] = 1.0

        actual_target_x = option["target"]["x"]
        actual_target_y = option["target"]["y"]

        target_cell = board[actual_target_y][actual_target_x]

        is_capture = 0.0
        if target_cell != " " and target_cell != self.player:
            is_capture = 1.0

        dx = perspective_target["x"] - perspective_origin["x"]

        is_straight_forward = 1.0 if dx == 0 else 0.0
        is_left_diagonal = 1.0 if dx == -1 else 0.0
        is_right_diagonal = 1.0 if dx == 1 else 0.0

        # How close the target square is to the winning row,
        # from this bot's perspective.
        if self.height <= 1:
            target_progress = 0.0
        else:
            target_progress = perspective_target["y"] / (self.height - 1)

        helper_values = [
            is_capture,
            is_straight_forward,
            is_left_diagonal,
            is_right_diagonal,
            target_progress
        ]

        move_values = origin_values + target_values + helper_values

        return torch.tensor(move_values, dtype=torch.float32)

    def decide_move(self, board, options):
        self._ensure_model_for_board(board)

        if len(options) == 0:
            return None

        board_tensor = self._board_to_tensor(board)

        valid_options = []
        valid_move_tensors = []

        for option in options:
            move_tensor = self._option_to_move_tensor(board, option)

            if move_tensor is not None:
                valid_options.append(option)
                valid_move_tensors.append(move_tensor)

        if len(valid_options) == 0:
            return copy.deepcopy(random.choice(options))

        legal_move_tensors = torch.stack(valid_move_tensors)

        with torch.no_grad():
            legal_move_scores = self.model.score_moves(
                board_tensor,
                legal_move_tensors
            )

            legal_move_probabilities = torch.softmax(
                legal_move_scores / self.temperature,
                dim=0
            )

        # Exploration to sometimes choose randomly for better learning.
        if random.random() < self.epsilon:
            chosen_index = random.randrange(len(valid_options))
        else:
            chosen_index = torch.multinomial(
                legal_move_probabilities,
                1
            ).item()

        chosen_option = valid_options[chosen_index]

        self.episode_memory.append(
            {
                "board_tensor": board_tensor.detach().clone(),
                "legal_move_tensors": legal_move_tensors.detach().clone(),
                "chosen_index": chosen_index
            }
        )

        return copy.deepcopy(chosen_option)

    def _train(self, final_reward):
        if len(self.episode_memory) == 0:
            return

        policy_loss_terms = []
        value_loss_terms = []
        entropy_terms = []

        number_of_moves = len(self.episode_memory)

        for move_index, memory in enumerate(self.episode_memory):
            board_tensor = memory["board_tensor"]
            legal_move_tensors = memory["legal_move_tensors"]
            chosen_index = memory["chosen_index"]

            legal_move_scores = self.model.score_moves(
                board_tensor,
                legal_move_tensors
            )

            log_probabilities = torch.log_softmax(
                legal_move_scores,
                dim=0
            )

            probabilities = torch.softmax(
                legal_move_scores,
                dim=0
            )

            chosen_log_probability = log_probabilities[chosen_index]

            # Later moves are usually more directly responsible.
            discounted_reward = final_reward * (
                self.gamma ** (number_of_moves - move_index - 1)
            )

            reward_tensor = torch.tensor(
                discounted_reward,
                dtype=torch.float32
            )

            predicted_value = self.model.value(board_tensor)

            # advantage = actual result - expected result
            advantage = reward_tensor - predicted_value.detach()

            policy_loss = -chosen_log_probability * advantage

            value_loss = (predicted_value - reward_tensor) ** 2

            entropy = -torch.sum(
                probabilities * log_probabilities
            )

            policy_loss_terms.append(policy_loss)
            value_loss_terms.append(value_loss)
            entropy_terms.append(entropy)

        total_policy_loss = torch.stack(policy_loss_terms).sum()
        total_value_loss = torch.stack(value_loss_terms).sum()
        total_entropy = torch.stack(entropy_terms).sum()

        total_loss = (
            total_policy_loss
            + self.value_loss_coefficient * total_value_loss
            - self.entropy_coefficient * total_entropy
        )

        self.optimizer.zero_grad()
        total_loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=1.0
        )

        self.optimizer.step()

        self.last_loss = total_loss.item()

        self.episode_memory = []

    def won(self):
        self.games_played += 1
        self.games_won += 1
        self._train(final_reward=1.0)

    def lost(self):
        self.games_played += 1
        self.games_lost += 1
        self._train(final_reward=-1.0)

    def resset(self, initBoard, player):
        self.player = player
        self._ensure_model_for_board(initBoard)

        self.initial_board = copy.deepcopy(initBoard)

        # Important:
        # New round means old unfinished episode memory should be cleared.
        self.episode_memory = []

    def info_print(self):
        print("Neural Network Bot")
        print(f"Player: {self.player}")
        print(f"Board size: {self.width}x{self.height}")
        print(f"Games played: {self.games_played}")
        print(f"Games won: {self.games_won}")
        print(f"Games lost: {self.games_lost}")

        if self.games_played > 0:
            win_rate = self.games_won / self.games_played
            print(f"Win rate: {win_rate:.2%}")

        if self.last_loss is not None:
            print(f"Last loss: {self.last_loss:.4f}")

    def save(self, path="hexapawn_nn_bot.pt"):
        torch.save(
            {
                "width": self.width,
                "height": self.height,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "games_played": self.games_played,
                "games_won": self.games_won,
                "games_lost": self.games_lost
            },
            path
        )

    def load(self, path="hexapawn_nn_bot.pt"):
        checkpoint = torch.load(path, map_location="cpu")

        width = checkpoint["width"]
        height = checkpoint["height"]

        fake_board = [[" " for _ in range(width)] for _ in range(height)]

        self._ensure_model_for_board(fake_board)

        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        self.games_played = checkpoint.get("games_played", 0)
        self.games_won = checkpoint.get("games_won", 0)
        self.games_lost = checkpoint.get("games_lost", 0)
