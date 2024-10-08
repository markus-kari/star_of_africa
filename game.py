import random
import time
import re
import map, player, AI_decisions

class Game:
    """
    A class that stores the data of the game and runs it

    ...

    Attributes
    ----------
    players : list of Player objects
        Contains all the Player objects
    turn : int
        Keeps track whose turn it is. Must be smaller than len(players)
    turn_no : int
        Keeps track of how many turns have been played. Starts with 1.
    tokens : list of int
        Contains the information of the (unflipped) tokens of 30 cities
        in their respective order. Does not contain the information
        whether the token has been flipped.
        1: an empty token (12)
        2: a horseshoe (5)
        3: a robber (3)
        4: a topaz worth 300 (4)
        5: an emerald worth 600 (3)
        6: a ruby worth 1000 (2)
        7: the Star of Africa
    unflipped : list of bool
        Contains the information of the 30 cities, 2 starting locations
        and 10 crossroads, whether they have an unflipped token in
        them. The order is the same as with the previous variable
        (tokens). This is needed for caches.
    horseshoes_found : int
        Contains the info how many horseshoes has been found. Needed
        for elimination of players.
    star_found : bool
        Whether the Star of Africa has been found
    winner : Player
        The player who won the game. This will be None before the game
        has finished.
    cape_visit : bool
        Whether Cape Town has been visited. The first player to reach
        Cape Town gets 500 pounds.
    human_game : bool
        Whether this game contains humans. If False, turn events will
        not be printed, but instead they will be spent by the funtion
        play as a report.
    elimination : bool, optional
        If the Star of Africa is found and all the horseshoes are
        found, if True, then all the rest of the players, i.e. players
        who can't win anymore, will lose. Defaults to True.

    Methods
    -------
    play
        Runs the game and takes care of the order of turns
    run_turn
        The human player decides which action to take.
        For AI corresponds to run_turn_AI and AI_turn_decision.
    movement_decision
        The human player decides where to travel.
        For AI corresponds to AI_movement_decision
    run_turn_AI
        The AI player sees which action the player must take or if
        that needs to be decided
    AI_turn_decision
        The AI player decides which action to take when there are
        multiple options
    AI_movement_decision
        The AI player decides where to travel
    flip
        Flips the token where the player is
    move
        Moves the player to the new location
    """

    def __init__(self, players, human_game, elimination=True):
        """
        Parameters
        ----------
        players : list of Player objects
            Contains all the Player objects
        """
        self.players = players
        self.turn = 0
        self.turn_no = 1
        self.tokens = [1] * 12 + [2] * 5 + [3] * 3 + [4] * 4 + [5] * 3 + [6] * 2 + [7]
        random.shuffle(self.tokens)
        self.unflipped = [True] * 30 + [False] * 12
        self.horseshoes_found = 0
        self.star_found = False
        self.winner = None
        self.cape_visit = False
        self.human_game = human_game
        self.elimination = elimination

    def play(self):
        """Runs the game and takes care of the turns."""
        if self.turn == len(self.players):
            self.turn = 0
            self.turn_no += 1
        active = self.players[self.turn]
        if active.AI_type:
            self.run_turn_AI(active)
        else:
            self.run_turn(active)
        # If any players are eliminated, the order might be messed up. Therefore this.
        self.turn = self.players.index(active)
        if active.location in ("Tan", "Cai") and (active.has_star or active.has_horseshoe):
            self.winner = active
        self.turn += 1
        msg = f"{active.name}, {active.money}, {active.location}"
        return msg

    def run_turn(self, player):
        """This function takes care of deciding for a human.

        This function will ask the player (if the player has a choice)
        what he/she would like to do and calls the respective function
        accordingly. It also checks that the player doesn't have a
        special flag on, i.e. the player is not forced to move at the
        sea slowly, deal with pirates or beduins or be a slave.

        Args
        ----
        player : Player
            The current player's object

        Returns None
        """
        print(f"\nIt is {player.name}'s turn!")
        print(f"You have {player.money} pounds.")
        print("You are in the following location: " +
            f"{map.locstr(player.location, player.offshore, self.unflipped)}.\n")
        time.sleep(3)
        if player.special == 0:
            possible = player.turn_possibilities(self.unflipped)
            if len(possible) == 1:
                if "land" in possible:
                    print("You need to travel by land.")
                    self.movement_decision(player, "land")
                else:
                    print("You need to travel by sea.")
                    if not player.offshore:
                        player.offshore = True
                        if player.money == 0:
                            player.special = 1
                            self.movement_decision(player, "sea_forced")
                        else:
                            player.money -= 100
                            self.movement_decision(player, "sea")
                    else:
                        self.movement_decision(player, "sea")
            else:
                while True:
                    for _, value in enumerate(possible):
                        if value == "flip":
                            print(
                                "If you want to try to flip the token in " +
                                    f"{map.abb_to_full[player.location]}, write flip."
                            )
                        elif value == "land":
                            print("If you want to travel by land, write land.")
                        elif value == "sea":
                            print("If you want to travel by sea, write sea.")
                        else:
                            print("If you want to travel by plane, write air.")
                    decision = input(
                        "Which option would you like? (You can also write tokens.) "
                    )
                    match decision:
                        case "flip":
                            print(self.try_flip(player))
                            break
                        case "land":
                            self.movement_decision(player, "land")
                            break
                        # player cannot be already offshore
                        case "sea":
                            player.offshore = True
                            if player.money == 0:
                                player.special = 1
                                self.movement_decision(player, "sea_forced")
                            else:
                                player.money -= 100
                                self.movement_decision(player, "sea")
                            break
                        case "air":
                            player.money -= 300
                            self.movement_decision(player, "air")
                            break
                        case "tokens":
                            self.token_location()
                        case "cheat":
                            self.cheat()
                        case _:
                            print(
                                "You need to choose one of the aforementioned options" +
                                    "(or write tokens)! "
                            )
        elif player.special == 1:
            print("You need to travel by sea.")
            self.movement_decision(player, "sea_forced")
        elif player.special in (2, 3):
            print(self.stuck(player))
        else:
            print(self.slave(player))
        return None

    def movement_decision(self, player: player.Player, decision):
        """This function chooses the destination for a human.

        This function will look for the available destination options
        by calling the function destination_options, ask the player
        which of the destination options the player prefers and calls
        the function move which moves the person there.

        Args
        ----
        player : Player
            The current player's object
        decision : str
            This has four possible values:
            air - the person flies
            sea_forced - the person travels two steps a turn by sea
            land or sea - the person travels that way by rolling a dice

        Returns None
        """
        if decision == "air":
            options = map.air_routes[player.location]
        elif decision == "sea_forced":
            print(
                "\nYou have no money, so you are travelling at a steady pace of two steps per turn."
            )
            options = player.destination_options(2)
        else:
            roll = random.randint(1, 6)
            print(f"\nYou rolled a {roll}.\n")
            options = player.destination_options(roll)
        while True:
            for index, value in enumerate(options):
                print(
                    f"Write {index} if you want to move to the following location: " +
                        f"{map.locstr(value, player.offshore, self.unflipped)}."
                )
            decision = input(
                "Where would you like to travel? (You can also write tokens.) "
            )
            if decision.isnumeric() and 0 <= int(decision) < len(options):
                self.move(player, options[int(decision)])
                break
            if decision == "tokens":
                self.token_location()
            if decision == "cheat":
                self.cheat()
            print("You need to write one of those numbers (or write tokens)!\n")
        return None

    def run_turn_AI(self, player):
        """This function checks if the AI needs to decide action.

        This function will check if the AI has a special status or not.
        If the AI has a special status, it calls the corresponding
        function. If not, it will call the AI_turn_decision, if there
        are several action options, and eventually it will call the
        function AI_movement_decision.

        Args
        ----
        player : Player
            The current player's object

        Returns None
        """
        if self.human_game:
            print(f"\nIt is {player.name}'s turn!")
            print(f"{player.name} has {player.money} pounds.")
            print(
                f"{player.name} is in the following location: " +
                    f"{map.locstr(player.location, player.offshore, self.unflipped)}.\n"
            )
        if player.special == 0:
            possible = player.turn_possibilities(self.unflipped)
            if len(possible) == 1:
                if "land" in possible:
                    self.AI_movement_decision(player, "land")
                else:
                    if not player.offshore:
                        player.offshore = True
                        if player.money == 0:
                            player.special = 1
                            self.AI_movement_decision(player, "sea_forced")
                        else:
                            player.money -= 100
                            self.AI_movement_decision(player, "sea")
                    else:
                        self.AI_movement_decision(player, "sea")
            else:
                self.AI_movement_decision(
                    player, self.AI_turn_decision(player, possible)
                )
        elif player.special == 1:
            self.AI_movement_decision(player, "sea_forced")
        elif player.special in (2, 3):
            msg = self.stuck(player)
            if self.human_game:
                print(msg)
        else:
            msg = self.slave(player)
            if self.human_game:
                print(msg)
        return None

    def AI_turn_decision(self, player, options):
        """This function will help AI decide what to do.

        This function is called if the AI has more than one option what
        to do this turn. This function will check what type the AI is
        (and correct that if necessary), and will then call the
        corresponding function to decide which action the AI will
        choose. It then returns back to the function run_turn_AI the
        action the AI chooses.

        Args
        ----
        player : Player
            The current player's object
        options : list of str
            The options for this turn that the AI has

        Returns
        -------
        result : str
            The action the AI chooses.
        """
        if player.has_star or player.has_horseshoe:
            result = map.expected_time(player.money)[player.location][1]
        elif self.star_found:
            result = AI_decisions.choose_action_token(
                options, player.location, self.unflipped, player.money
            )
        else:
            # check if the strategy needs to be changed
            if player.AI_type == 2 and self.cape_visit:
                player.AI_type = 1
            elif player.AI_type == 3 and not self.unflipped[9]:
                player.AI_type = 1

            if player.AI_type in (2, 3):
                result = AI_decisions.choose_action_city(options)
            # player.AI_type == 1
            else:
                result = AI_decisions.choose_action_token(
                    options, player.location, self.unflipped, player.money
                )
        if result == "sea":
            player.offshore = True
            if player.money == 0:
                player.special = 1
                result = "sea_forced"
            else:
                player.money -= 100
        elif result == "air":
            player.money -= 300
        return result

    def AI_movement_decision(self, player, decision):
        """This function will move the AI.

        This function is called when the AI has decided the action for
        this turn. If it is trying to flip the token, the function
        try_flip is called. Otherwise this function will call other
        functions to see, which movement options the AI has, which of
        those it chooses for and eventually it will move the AI to that
        location by calling the the function move.

        Args
        ----
        player : Player
            The current player's object
        decision : str
            The action the AI chose

        Returns None
        """
        time.sleep(3)
        if decision == "flip":
            if self.human_game:
                print(f"{player.name} is trying to flip a token.")
                print(self.try_flip(player))
            else:
                self.try_flip(player)
        else:
            if decision == "air":
                if self.human_game:
                    print(f"{player.name} is travelling by plane.")
                options = map.air_routes[player.location]
            elif decision == "sea_forced":
                if self.human_game:
                    print(f"{player.name} is travelling by ship.")
                options = player.destination_options(2)
            else:
                if self.human_game and decision == "sea":
                    print(f"{player.name} is travelling by ship.")
                elif self.human_game and decision == "land":
                    print(f"{player.name} is travelling by land.")
                roll = random.randint(1, 6)
                options = player.destination_options(roll)
            if player.has_star or player.has_horseshoe:
                choice = AI_decisions.choose_home(options, player.money)
            elif self.star_found:
                choice = AI_decisions.choose_token(options, self.unflipped, player.money)
            else:
                # check if the strategy needs to be changed
                if player.AI_type == 2 and self.cape_visit:
                    player.AI_type = 1
                elif player.AI_type == 3 and not self.unflipped[9]:
                    player.AI_type = 1

                if player.AI_type == 2:
                    choice = AI_decisions.choose_city(
                        "Tow", options, self.unflipped, player.money
                        )
                elif player.AI_type == 3:
                    choice = AI_decisions.choose_city(
                        "Gol", options, self.unflipped, player.money
                        )
                # player.AI_type == 1
                else:
                    choice = AI_decisions.choose_token(options, self.unflipped, player.money)
            new_loc = options[choice]
            if self.human_game:
                print(
                    f"{player.name} will travel to the following location: " +
                        f"{map.locstr(new_loc, player.offshore, self.unflipped)}"
                )
            self.move(player, new_loc)
        return None

    def flip(self, player: player.Player):
        """This function flips the token where the player is.

        This function finds the token in the player's location and
        takes action accordingly: player's money is changed or player
        object's variable (and the variable star_found) will be changed
        if the Star of Africa or a horseshoe is found. Slave Coast and
        Gold Coast are taken into account here.
        If elimination is True, some players are eliminated by this
        function (see documentation at the class Game).

        Args
        ----
        player : Player
            The current player's object

        Returns
        -------
        mesg: str
            A message that explains what happened
        """
        token_no = self.tokens[map.abbs.index(player.location)]
        match token_no:
            case 1:
                msg = "You found nothing. "
                if player.location == "Sla":
                    msg += "You have to now stay as a slave for three turns!"
                    player.special = 6
            case 2:
                self.horseshoes_found += 1
                if self.star_found:
                    msg = "\nYou found a horseshoe!! Now go quickly back to Cairo or Tangier!"
                    player.has_horseshoe = True
                    # Elimination
                    if self.horseshoes_found == 5 and self.elimination:
                        eliminated = []
                        for x in self.players:
                            if not (x.has_horseshoe or x.has_star):
                                eliminated.append(x)
                        for x in eliminated:
                            self.players.remove(x)
                        if eliminated:
                            msg += "\nThis was the last horseshoe, so the players who "
                            msg += "don't have a horsehoe or the Star of Africa will be eliminated!!"
                            msg += "\nThe following player(s) got eliminated: "
                            msg += ", ".join([a.name for a in eliminated])
                            msg += "."
                else:
                    msg = "You found a horseshoe! "
                    msg += "However, the Star of Africa has not yet been found."
            case 3:
                msg = "There was a robber! You lost all your money!"
                player.money = 0
            case 4:
                if player.location == "Gol":
                    msg = "You found a topaz! "
                    msg += "Because you are in Gold Coast, you got 600 pounds!"
                    player.money += 600
                else:
                    msg = "You found a topaz! You got 300 pounds!"
                    player.money += 300
            case 5:
                if player.location == "Gol":
                    msg = "You found an emerald! "
                    msg += "Because you are in Gold Coast, you got 1200 pounds!"
                    player.money += 1200
                else:
                    msg = "You found an emerald! You got 600 pounds!"
                    player.money += 600
            case 6:
                if player.location == "Gol":
                    msg = "You found a ruby! "
                    msg += "Because you are in Gold Coast, you got 2000 pounds!"
                    player.money += 2000
                else:
                    msg = "You found a ruby! You got 1000 pounds!"
                    player.money += 1000
            # token is 7
            case 7:
                msg = "You found the Star of Africa!! "
                msg += "Now go quickly back to Cairo or Tangier!"
                self.star_found = True
                player.has_star = True
                if self.horseshoes_found == 5 and self.elimination:
                    msg += "\nAll the horsehoes are found, so the game ended!"
                    self.winner = player
        self.unflipped[map.abbs.index(player.location)] = False
        return msg

    def try_flip(self, player: player.Player):
        """Trying to flip a token in a city. Works if 4-6 is rolled."""
        x = random.randint(1, 6)
        msg = f"\nYou tried to flip the token and you rolled a {x}. "
        if x > 3:
            msg += f"\n{self.flip(player)}"
        else:
            msg += "Unfortunately you didn't manage to flip the token."
        return msg

    def move(self, player: player.Player, new_loc):
        """This function will move the player and check for flip.

        The player is moved to the new location and if the player is in
        a city with an unflipped token and has at least 100 pounds, the
        player is asked whether the player wants to flip the token. AI
        will always choose to flip the token if the AI does not have
        the Star of Africa or a horseshoe.
        This function will also take care of the 500 pounds paid to the
        first person in Cape Town and if the player gets stuck (=raided
        by pirates or ambushed by beduins).

        Args
        ----
        player : Player
            The current player's object
        new_loc : str
            The new location string of the player

        Returns None
        """
        player.location = new_loc
        if len(re.split(r"-", new_loc)) == 1 and ("nd" not in new_loc):
            player.offshore = False
            player.special = 0
            if new_loc == "Tow" and not self.cape_visit:
                if self.human_game and player.AI_type:
                    print(
                        f"{player.name} was the first player to visit Cape Town and got 500 pounds."
                    )
                elif self.human_game:
                    print(
                        "You were the first player to visit Cape Town! You get 500 pounds!"
                    )
                self.cape_visit = True
                player.money += 500
            if self.unflipped[map.abbs.index(new_loc)] and player.money >= 100:
                if player.AI_type:
                    if not (player.has_star or player.has_horseshoe):
                        player.money -= 100
                        msg = self.flip(player)
                        if self.human_game:
                            print(msg)
                else:
                    action = input(
                        f"Would you like to flip the token in {map.abb_to_full[new_loc]}? " +
                            "Write (y)es or (n)o. "
                    )
                    while True:
                        if action[0].lower() == "y":
                            player.money -= 100
                            print(self.flip(player))
                            break
                        if action[0].lower() == "n":
                            break
                        print("You need to write y or n!")
        else:
            if new_loc in ["Sah-Darf-2-6", "Darf-Sah-6-2"]:
                player.special = 2
            elif new_loc in [
                "Sth-nd7-1-8",
                "nd7-Sth-8-1",
                "Sth-nd9-1-7",
                "Sth-nd9-7-1",
            ]:
                player.special = 3
        return None

    def stuck(self, player: player.Player):
        """Player being ambushed by beduins or pirates."""
        if player.special == 2:
            msg = "You are ambushed by the beduins!"
        else:
            msg = "Your ship is raided by the pirates!"
        x = random.randint(1, 6)
        msg += f"\nYou rolled a {x}."
        if x < 3:
            msg += "\nYou managed to escape! You can move freely next turn."
            player.special = 0
        else:
            msg += "\nYou did not manage to escape. Hopefully next turn."
        return msg

    def slave(self, player: player.Player):
        """Player working as a slave in Slave Coast."""
        msg = "You are working as a slave. "
        if player.special == 4:
            msg += "You are free to move next turn."
            player.special = 0
        elif player.special == 5:
            msg += "You are free to move in 2 turns."
            player.special -= 1
        else:
            msg += "You are free to move in 3 turns."
            player.special -= 1
        return msg

    def token_location(self):
        """Prints which cities have unflipped tokens and which haven't."""
        for x in range(30):
            if self.unflipped[x]:
                print(map.full_names[x] + ": not flipped")
            else:
                print(map.full_names[x] + ": flipped")
        return None

    def cheat(self):
        """Prints the tokens of the cities."""
        for x in range(30):
            print(f"{map.full_names[x]}: {self.tokens[x]}")
        return None