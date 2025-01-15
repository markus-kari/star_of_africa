import time
import random
import initialize
import csv
import numpy as np

if __name__ == "__main__":
    # change this variable for different amount of games
    no_games = 10**3
    # change this variable if you don't want the elimination rules on
    elimination = True

    t = time.time()  
    fieldnames = ['Winner', 'Turns', 'Horseshoe winner', 'Star location']      
    data = np.empty([no_games, len(fieldnames)], dtype=object)
    for x in range(no_games):
        random.seed(x)
        game = initialize.init_AI(elimination)
        while game.winner is None:
            msg = game.play()
        data[x] = [game.winner.name, game.turn_no, game.winner.has_horseshoe, game.tokens.index(7)]
    with open("statistics.csv", "w", newline='') as file:
        header_writer = csv.DictWriter(file, fieldnames)
        header_writer.writeheader()
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    print(f"It took {round(time.time()-t, 3)} seconds to run this.")
