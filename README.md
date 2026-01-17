
# Quoridor-Bot

A classical alpha-beta pruning based bot to play Quoridor. The main game is written in Python while the bot itself is written in C++ to boost performance (and also as I am currently learning C++ so this is a very fun project!) 


# Features

- Can play human vs human, human vs bot or bot vs human 
- Currently uses a standard minimax algorithm with alpha beta pruning

# Future Features

- Transposition table to improve performance
- BFS caching (cache the results of the Breadth First Search used to path lengths and wall legality which is used frequently in legal move generation and the evaluation metric)
- Bit boards to improve performance
- More advanced search techniques (Quiescence search, null move pruning, etc)
- Store minmax results in the early phase of the game to a file to create an opening book to reduce move times in the opening
- More effective move pruning

## Installation

- Simply run the `main.py` file. The bot's c++ code has already been compiled to a pyd. 
- The bots depth can be adjusted by chaning the `BOT_DEPTH` constant in main.py

    
