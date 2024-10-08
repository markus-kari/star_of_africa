import random
import player, game

def init_human(elimination=True):
    """
    Initializes the game.

    Asks the number of players, their names and
    their starting locations. Randomizes the starting order.
    Check the variable elimination from the Game object documentation.

    Returns a game object with players.
    """
    while True:
        no_players = int(input("How many players are playing the game (1-6): "))
        if 1 <= no_players <= 6:
            break
        print("The amount of players must be between 1 and 6!")
    players = []
    sample_names = ["Amy", "Brook", "Connor", "David", "Emma", "Felix"]
    for x in range(no_players):
        while True:
            decision = input(f"\nIs the player {x+1} a (h)uman or a (c)omputer? ")

            if decision[0].lower() == "c":
                while True:
                    name = input("Is this computer random (0) or type 1-4? ")
                    match name:
                        case "0":
                            ai_type = random.randint(1, 4)
                            match ai_type:
                                case 1:
                                    players.append(player.Player(sample_names[x], 1, "Tan"))
                                case 2:
                                    players.append(player.Player(sample_names[x], 1, "Cai"))
                                case 3:
                                    players.append(player.Player(sample_names[x], 2, "Cai"))
                                case 4:
                                    players.append(player.Player(sample_names[x], 3, "Tan"))
                            break
                        case "1":
                            players.append(player.Player(sample_names[x], 1, "Tan"))
                            break
                        case "2":
                            players.append(player.Player(sample_names[x], 1, "Cai"))
                            break
                        case "3":
                            players.append(player.Player(sample_names[x], 2, "Cai"))
                            break
                        case "4":
                            players.append(player.Player(sample_names[x], 3, "Tan"))
                            break
                        case _:
                            print("Write a number between 0 and 4!")
                break

            if decision[0].lower() == "h":
                name = input("The name of the player: ")
                while True:
                    starting_loc = input(
                        f"Does {name} start from (T)angier or (C)airo? Write T or C: "
                    )
                    if starting_loc[0].lower() == "t":
                        starting_loc = "Tan"
                        break
                    if starting_loc[0].lower() == "c":
                        starting_loc = "Cai"
                        break
                    print("The starting location must be T or C!")
                players.append(player.Player(name, 0, starting_loc))
                break

            print("The player needs to be h or c!")
    random.shuffle(players)
    return game.Game(players, True, elimination)


def init_AI(elimination=True):
    """Initializes the game when there are only AI players."""

    players = [
        player.Player("Amy", 1, "Cai"),
        player.Player("Brook", 1, "Tan"),
        player.Player("Connor", 2, "Cai"),
        player.Player("David", 3, "Tan"),
    ]
    random.shuffle(players)
    return game.Game(players, False, elimination)
