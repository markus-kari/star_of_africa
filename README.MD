# Star of Africa
The Star of Africa is a Python text-based version of the most famous board game of Finland (Afrikan tähti). It can be played by both humans and AIs! The games AI play can also be analysed!

As the game is text-based, the project also includes a picture of the gameboard, which makes it easier to understand what's going on. There is also a file called **analysis.pdf**, which includes both the rules and an analysis of the game.

## Dependencies
- Python 3.12
- Numpy (an older version will do)
(For analysing the game:)
- Pandas
- Matplotlib

## Usage
The game can be played either by humans, by AI or with both! For a game involving humans, run h_game.py . The game can involve AI but it doesn't have to. For a game involving only AIs, run ai_game.py .

### Game with humans
The game can involve 1-6 players, humans or AIs. For each player you need to define if it is a human or an AI player. In case of a human player you also to provide the name and the starting location. For an AI player you need to only define its type: it will be named automatically and its type will also define its starting location. AIs have four types and one "random" type which chooses randomly one of the types. A type will define the AIs strategy how to play the game. AI types are explained in the section Game with AIs only. 

The game asks which action the player wants to take (if multiple available) and where to move if moving. The actions the AI will take are also described. The game continues as per rules, and as the game ends, the program tells which player won and how many turns the game took.

### Game with AIs only
Running the file will make AIs play the game several times. The number of games can be changed (governed by the variable no_games at the top). Each game will be played by four AIs, and each AI has a unique type. The data of each game is saved into statistics.csv. The games can be then analysed with analyse.py.

The AIs have four types:
1) Targets always the closest token and starts in Cairo. In the AI game its name is Amy.
2) Targets always the closest token and starts in Tangier. In the AI game its name is Brook.
3) Starts in Cairo, and will slowly travel down to Cape Town. In the AI game its name is Connor.
4) Starts in Tangier, and will slowly travel down to Gold Coast. In the AI game its name is David.

If Cape Town is reached or the token in Gold Coast flipped, the AIs will respectively change to the strategy where they will just target the closest token. They will also change to the closest-token-strategy, if the Star of Africa is found. Whenever the player has found the Star of Africa or a horseshoe after the Star of Africa is found, i.e. the player needs to quickly travel back to Tangier or Cairo, the AI will no longer flip any tokens but instead will travel back to those cities as quickly as possible.

Please note: the games are not random per se, as each game will have a seed assigned to it. What this means is that if you run the file with 10 games, each game will have a unique result, but if you run the file a second time with 10 games, it will have the same 10 results as the first game. This is so that the results would be easier to replicate and to analyse.

## Author
Created by Markus Kari, 2024.

## License
[MIT](https://choosealicense.com/licenses/mit/) 

_However_, remember that the Star of Africa as a board game is a licensed product, and the author claims no ownership over the board game. That means also that for any commercial products based on this work a permission should be asked, likely from Kari Mannerla's heirs. 