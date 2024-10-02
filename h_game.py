import initialize

if __name__ == "__main__":
    elimination = True
    game = initialize.init_human(elimination)
    while game.winner is None:
        game.play()
    print(f"\nPlayer {game.winner.name} won the game!")
    print(f"The game lasted {game.turn_no} turns.")
