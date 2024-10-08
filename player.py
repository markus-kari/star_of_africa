import re
import map

class Player:
    """
    A class for a player, human or AI

    ...

    Attributes
    ----------
    name : str
        The name of the player
    AI_type : int
        Whether the player is AI (True, i.e. something else than 0) or
        human (False, i.e. 0). If the player is AI, this value also
        implies the strategy of the AI.
        1: targets the closest token
        2: tries to go to Cape Town, then becomes a 1
        3: tries to go to Gold Coast, then becomes a 1
        2 and 3 will become a 1 also if the Star of Africa is found
    location : str
        The location string.
        There are two different options how this looks:
        1) A city: just the abbreviation of the city
        2) Between two cities: first abb where the player last passed,
        second the abb where the player is going toward, third how
        many steps away the player is from the first city and fourth
        how many steps there are to the second city. The delimiter is
        a hyphen. (-)
        Examples:
        i) "Cai"; in Cairo
        ii) "Cai-Egy-1-3"; one step away from Cairo towards Egypt,
        three steps to Egypt
        iii) "nd0-Sah-3-1"; three steps away from the crossroads
        next to Tangier and Morocco towards Sahara, one step to Sahara
    money : int
        Money that the player has. Must be non-negative
        and divisible by 100.
    has_star : bool
        Whether the player has the Star of Africa
    has_horseshoe : bool
        Whether the player has a horeshoe. Can be True only after the
        Star of Africa has been found.
    offshore : bool
        Returns True if the player is on the sea (not on an island)
    special : int
        0 if there is nothing special, 1 if the player is travelling by
        sea with no money (i.e. two steps per turn), 2 if the player
        is ambushed by beduins, 3 if the player's ship is raided by
        pirates, 4-6 if the player is working as a slave: 6 if still
        for three turns, 5 if for two turns and 4 if for one turn

    Methods
    -------
    turn_possibilities
        Returns a list of possible actions, depending on the unflipped
        tokens.
    destination_options
        Returns a list of all the locations the player can go to, if
        the player is going by land or by sea.
    """

    def __init__(self, name, AI_type, starting_loc):
        """
        Parameters
        ----------
        name : str
            The name of the player
        AI_type : int
            Whether the player is AI (i.e. something else than 0) or
            human (0)
        starting_loc : str
            Whether the player starts from Tangier or Cairo
        """
        self.name = name
        self.AI_type = AI_type
        self.location = starting_loc
        self.money = 300
        self.has_star = False
        self.has_horseshoe = False
        self.offshore = False
        self.special = 0


    def turn_possibilities(self, unflipped):
        """Returns a list of possible actions in this turn.

        Args
        ----
        unflipped : list of bool
            The variable from the Game object that contains the information
            which cities have an unflipped token.

        Returns
        -------
        possible: list of str
            A list containing 1-4 of the following:
            flip: player can try to flip the token with dice
            land: player can move by land
            sea: player can move by ship
            air: player can move by plane
        """
        possible = []
        loc = re.split(r"-", self.location)
        # if the player is in a city
        if len(loc) == 1 and "nd" not in loc[0]:
            # if token has not been flipped
            if unflipped[map.abbs.index(loc[0])]:
                possible.append("flip")
            if map.land_routes[loc[0]]:
                possible.append("land")
            if map.sea_routes[loc[0]]:
                possible.append("sea")
            if map.air_routes[loc[0]] and self.money >= 300:
                possible.append("air")
        elif self.offshore:
            possible.append("sea")
        else:
            possible.append("land")
        return possible
    
    def destination_options(self, dice: int, loc: str = None, ignore: str = None):
        """Returns a list of all the locations player can go to.

        Args
        ----
        dice : int
            How many steps the player can take
        loc: str, optional
            If the function is calculated from another location than 
            where the player is currently located. Defaults to None,
            which refers to the player's current location.
        ignore : str, optional
            If there are any directions the player is not able to move
            towards. Defaults to None.
            E.g. player starts at "Cai-Egy-3-1" and rolls a two, this
            function will be called recursively with dice=1, loc="Egy" 
            and ignore="Cai", because otherwise the player would be
            able to go one step to Egypt and one step backwards,
            ending in the same space where the player started, which is
            not allowed.

        Returns:
        options : list of str
            A list of location strings where the player can go to
        """
        options = []
        if loc is None:
            loc = self.location
        locs = re.split(r"-", loc)
        # in a node
        if len(locs) == 1:
            if self.offshore:
                dest = [x for x in map.sea_routes[loc] if x[0] != ignore]
            else:
                dest = [x for x in map.land_routes[loc] if x[0] != ignore]
            for x in dest:
                if x[1] > dice:
                    options.append(
                        locs[0]
                        + "-"
                        + x[0]
                        + "-"
                        + str(dice)
                        + "-"
                        + str(x[1] - dice)
                    )
                elif x[1] == dice:
                    options.append(x[0])
                else:
                    if "nd" not in x[0]:
                        options.append(x[0])
                    if not self.offshore or "nd" in x[0]:
                        options = options + self.destination_options(
                            dice - x[1], x[0], loc
                        )
        # between nodes
        else:
            # towards the town player came from (locs[0])
            if int(locs[2]) > dice:
                options.append(
                    locs[0]
                    + "-"
                    + locs[1]
                    + "-"
                    + str(int(locs[2]) - dice)
                    + "-"
                    + str(int(locs[3]) + dice)
                )
            elif int(locs[2]) == dice:
                options.append(locs[0])
            else:
                if "nd" not in locs[0]:
                    options.append(locs[0])
                if not self.offshore or "nd" in locs[0]:
                    options = options + self.destination_options(
                        dice - int(locs[2]), locs[0], locs[1]
                    )
            # towards the town the player is heading (locs[1])
            if int(locs[3]) > dice:
                options.append(
                    locs[0]
                    + "-"
                    + locs[1]
                    + "-"
                    + str(int(locs[2]) + dice)
                    + "-"
                    + str(int(locs[3]) - dice)
                )
            elif int(locs[3]) == dice:
                options.append(locs[1])
            else:
                if "nd" not in locs[1]:
                    options.append(locs[1])
                if not self.offshore or "nd" in locs[1]:
                    options = options + self.destination_options(
                        dice - int(locs[3]), locs[1], locs[0]
                    )
        return options
    