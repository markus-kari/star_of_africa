import time
import random
import initialize

if __name__ == "__main__":
    no_games = 1000
    elimination = True
    turns = 0
    t = time.time()
    for x in range(no_games):
        random.seed(x)
        game = initialize.init_AI(elimination)
        with open("locations.txt", "a") as file:
            file.write(f"\nGame {x}:\n")
        while game.winner is None:
            msg = game.play()
            with open("locations.txt", "a") as file:
                file.write(f"{msg}\n")
        turns += game.turn_no
        with open("statistics.txt", "a") as file:
            file.write(
                f"Winner was: {game.winner.name}. Game lasted {game.turn_no} turns.\n"
            )
    print(f"It took {round(time.time()-t, 3)} seconds to run this.")
    print(f"On average it took {turns/no_games} turns.")
