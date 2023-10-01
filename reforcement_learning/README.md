                       Tic-Tac-Toe Q-Learning Agent Report

 Libraries Used

1. Python: The programming language used for implementing the Q-learning agent and game environment.

2. NumPy: A library for numerical computing, used for managing the Tic-Tac-Toe game board and Q-table.

3. Pygame: A library for creating graphical user interfaces, used for visualizing the game board and interactions.

 Environment Setup

 Game Constants

- Board Size: 3x3
- Cell Size: 100 pixels
- Window Size: 300x300 pixels
- Line Width: 15 pixels
- Colors: Various colors are used for drawing the game board, X, and O.

 Q-Learning Agent

- Exploration Rate (Epsilon): 0.2
- Learning Rate (Alpha): 0.8
- Discount Factor (Gamma): 1.0

 Training and Evaluation

 Training the Q-Learning Agent

The Q-learning agent was trained over 50000 episodes. During training, the agent played games against itself, updating its Q-values based on the outcomes of these games. The training process involved:

- Exploration: The agent randomly explored the available actions with a 20% probability (as determined by the exploration rate, epsilon).

- Exploitation: The agent selected actions based on the highest Q-values with an 80% probability.

- Reward Calculation: Rewards were assigned based on the game outcome:
  - Player X win: +1.0
  - Player O win: -1.0
  - Tie: 0.5
  - Ongoing game: 0.0

 Evaluating the Q-Learning Agent

The trained Q-learning agent was evaluated through 50000 game sessions against a random player. The evaluation results are as follows:

- Wins: X wins (Player X):  46943
- Ties: 1093
-Defeats: 1964
- Win Percentage: 93.886%
- Tie Percentage: 2.186%
-Defeats Percentage: 3.928%
 Results: -
The Q-learning agent's performance was assessed based on the evaluation results:

- Wins: 1883
- Ties: 46
- Defeats:71
- Win Percentage: 94.15%
-Defeats Percentage: 3.55%
- Tie Percentage: 2.3%

