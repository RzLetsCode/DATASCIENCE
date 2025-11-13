import numpy as np
import random
import pygame
import sys
import time

# Define constants
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
BOARD_SIZE = 3
CELL_SIZE = 100
WINDOW_SIZE = (CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE)
LINE_WIDTH = 15
LINE_COLOR = (0, 0, 0)
PLAYER_X_COLOR = (255, 0, 255)
PLAYER_O_COLOR = (0, 255, 255)
FONT_SIZE = 32
FONT_COLOR = (150, 150, 150)

# Initialize pygame
pygame.init()
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Tic-Tac-Toe")
font = pygame.font.Font(None, FONT_SIZE)

# Define the Tic-Tac-Toe environment
class TicTacToeEnvironment:
    def __init__(self):
        # Initialize the game board and game state
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = PLAYER_X
        self.winner = None
        self.game_over = False

    def reset(self):
        # Reset the game state to start a new game
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = PLAYER_X
        self.winner = None
        self.game_over = False

    def is_empty(self, row, col):
        return self.board[row][col] == EMPTY

    def is_valid_move(self, row, col):
        return not self.game_over and self.is_empty(row, col)

    def make_move(self, row, col):
        if self.is_valid_move(row, col):
            # Make a move and update the game state
            self.board[row][col] = self.current_player
            self.check_game_status()
            self.current_player = PLAYER_X if self.current_player == PLAYER_O else PLAYER_O

    def check_game_status(self):
        for player in [PLAYER_X, PLAYER_O]:
            # Check rows, columns, and diagonals for a win
            for i in range(BOARD_SIZE):
                if np.all(self.board[i, :] == player) or np.all(self.board[:, i] == player):
                    self.winner = player
                    self.game_over = True
                    return
            if np.all(np.diag(self.board) == player) or np.all(np.diag(np.fliplr(self.board)) == player):
                self.winner = player
                self.game_over = True
                return
        # Check for a tie
        if np.all(self.board != EMPTY):
            self.game_over = True

    def get_state(self):
        return tuple(tuple(row) for row in self.board)

    def is_game_over(self):
        return self.game_over

    def get_winner(self):
        return self.winner

    def available_moves(self):
        if self.game_over:
            return []
        return [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.is_empty(i, j)]

    def draw_board(self):
        # Draw the game board and pieces on the screen
        window.fill((255, 0, 255))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                left = col * CELL_SIZE
                top = row * CELL_SIZE
                pygame.draw.rect(window, (40, 80, 60), (left, top, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(window, LINE_COLOR, (left, top, CELL_SIZE, CELL_SIZE), LINE_WIDTH)
                if self.board[row][col] == PLAYER_X:
                    text = font.render("X", True, PLAYER_X_COLOR)
                    window.blit(text, (left + CELL_SIZE // 2 - FONT_SIZE // 2, top + CELL_SIZE // 2 - FONT_SIZE // 2))
                elif self.board[row][col] == PLAYER_O:
                    text = font.render("O", True, PLAYER_O_COLOR)
                    window.blit(text, (left + CELL_SIZE // 2 - FONT_SIZE // 2, top + CELL_SIZE // 2 - FONT_SIZE // 2))
        pygame.display.flip()

class QLearningAgent:
    def __init__(self, epsilon=0.2, alpha=0.8, gamma=1.0):
        # Initialize the Q-learning agent with hyperparameters
        self.q_table = {}
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor

    def get_q_value(self, state, action):
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]

    def choose_action(self, state, available_actions):
        if random.random() < self.epsilon:
            return random.choice(available_actions)  # Explore
        else:
            # Exploit: Select the action with the highest Q-value
            max_q_value = max([self.get_q_value(state, action) for action in available_actions])
            best_actions = [action for action in available_actions if self.get_q_value(state, action) == max_q_value]
            return random.choice(best_actions)

    def update_q_value(self, state, action, reward, next_state, available_actions):
        current_q_value = self.get_q_value(state, action)
        max_next_q_value = max([self.get_q_value(next_state, next_action) for next_action in available_actions])
        new_q_value = (1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * max_next_q_value)
        self.q_table[(state, action)] = new_q_value

def train_q_learning_agent(agent, episodes=50000):
    wins = 0
    ties = 0
    defeats = 0
    env = TicTacToeEnvironment()
    for episode in range(episodes):
        env.reset()
        state = env.get_state()
        while not env.is_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            available_actions = env.available_moves()
            action = agent.choose_action(state, available_actions)
            env.make_move(*action)
            env.draw_board()
            if env.is_game_over():
                if env.get_winner() == PLAYER_X:
                    reward = 1
                    wins += 1
                elif env.get_winner() == PLAYER_O:
                    reward = -1
                    defeats += 1
                else:
                    reward = 0
                    ties += 1
            else:
                reward = 0
            agent.update_q_value(state, action, reward, env.get_state(), available_actions)
            state = env.get_state()
    win_percentage = round((wins / episodes) * 100, 4)
    defeat_percentage = round((defeats / episodes) * 100, 4)
    tie_percentage = round((ties / episodes) * 100, 4)
    print(f"Training results :::::::::: Wins: {wins}, Ties: {ties}, Defeats:{defeats} Win Percentage: {win_percentage}%, Defeat Percentage: {defeat_percentage}%, Tie Percentage: {tie_percentage}%")

def evaluate_q_learning_agent(agent, episodes=2000):
    wins = 0
    ties = 0
    defeats = 0
    for _ in range(episodes):
        env = TicTacToeEnvironment()
        state = env.get_state()
        while not env.is_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            available_actions = env.available_moves()
            action = agent.choose_action(state, available_actions)
            env.make_move(*action)
            env.draw_board()
            if env.is_game_over():
                if env.get_winner() == PLAYER_X:
                    wins += 1
                elif env.get_winner() == PLAYER_O:
                    defeats += 1
                elif env.get_winner() is None:
                    ties += 1
            state = env.get_state()
    win_percentage = round((wins / episodes) * 100, 4)
    defeat_percentage = round((defeats / episodes) * 100, 4)
    tie_percentage = round((ties / episodes) * 100, 4)
    print(f"Evaluation results :::::::::: Wins: {wins}, Ties: {ties}, Defeats:{defeats} Win Percentage: {win_percentage}%, Defeat Percentage: {defeat_percentage}%, Tie Percentage: {tie_percentage}%")

# Create and train the Q-learning agent
agent = QLearningAgent()
train_q_learning_agent(agent, episodes=50000)

# Evaluate the Q-learning agent
evaluate_q_learning_agent(agent, episodes=2000)

# Keep the GUI window open until the user closes it
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
