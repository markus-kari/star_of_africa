import re
import numpy as np
import map

def choose_home(loc_strs, money):
    """Returns the preferable option to get home asap.

    This function, with the help of the function expected_time, returns
    which of the options given to the function has the shortest
    expected value of turns to get to Tangier or Cairo.

    Parameters
    ----------
    loc_strs : str
        The locations the player could reach this turn.
    money : int
        How much money the player has this turn.

    Returns
    -------
    int: the best option of the loc_strs
    """
    exp_values = np.zeros_like(loc_strs)
    times = map.expected_time(money)
    for index, value in enumerate(loc_strs):
        loc = re.split(r"-", value)
        if len(loc) == 1:
            exp_values[index] = times[loc[0]][0]
        else:
            # how long it takes to the next place in the chain + how much from there
            first = (
                map.expected(int(loc[2]) + times[loc[0]][2][1])
                + times[map.abbs[times[loc[0]][2][0]]][0]
            )
            second = (
                map.expected(int(loc[3]) + times[loc[1]][2][1])
                + times[map.abbs[times[loc[1]][2][0]]][0]
            )
            exp_values[index] = min(first, second)
    return np.argmin(exp_values)


def closest_token_location(loc_str, unflipped, poor):
    """Returns the distances to the closest token.

    This helper function, with the help of the function closest_tokens,
    returns the distances to the closest token from this location.
    It could be through sea or through land, but if the player has no
    money, (s)he moves slower in the sea and that is reflected in the
    result.

    Parameters
    ----------
    loc_str : str
        The location which is being investigated.
    unflipped : list of bool
        The variable from the Game object that contains the information
        which cities have an unflipped token.
    poor : bool
        If the player has money or not.

    Returns
    -------
    int: the best option of the loc_strs
    """
    # notice: regular min (not np.min) is utilized, so one needs to play around with the types
    dists = map.closest_tokens(tuple(unflipped), poor)
    loc = re.split(r"-", loc_str)
    if len(loc) == 1:
        return [np.int64(a) for a in dists[map.abbs.index(loc[0])]]
    first = dists[map.abbs.index(loc[0])] + int(loc[2])
    second = dists[map.abbs.index(loc[1])] + int(loc[3])
    return min(list(first), list(second))


def choose_token(loc_strs, unflipped, money):
    """Returns the best option to get the closest token."""
    if money:
        poor = False
    else:
        poor = True
    dist_values = []
    for loc in loc_strs:
        dist_values.append(closest_token_location(loc, unflipped, poor))
    return dist_values.index(min(dist_values))


def choose_action_token(options, loc, unflipped, money):
    """Returns the action to get the closest token.

    This function chooses the best action if there are 2+ options for
    action this turn to get to the closest token the fastest. It also
    takes into account that money should not be consumed excessively
    if the player doesn't have that much money (i.e. it discourages
    going with a ferry or with a plane). It also tries to avoid
    decisions that get the person stuck, for instance if one has to
    take a ferry to get a token, even though the player doesn't have
    much money.

    Parameters
    ----------
    options : str
        Which actions are available this turn.
    loc : str
        The location of the player.
    unflipped : list of bool
        The variable from the Game object that contains the information
        which cities have an unflipped token.
    money : int
        How much money the player has.

    Returns
    -------
    str: the best option what to do this turn: either flip, land, sea
    or air
    """

    def sea_coeff(money):
        if money == 0:
            return 0
        if money == 100:
            return 7
        if money == 200:
            return 4
        if money == 300:
            return 1
        return 0

    def air_coeff(money):
        if money == 300:
            return 10
        if money == 400:
            return 6
        if money == 500:
            return 4
        if money < 800:
            return 2
        return 0

    if money:
        poor = False
    else:
        poor = True
    if "flip" in options:
        return "flip"
    transport_times = [None] * len(options)
    for index, value in enumerate(options):
        if value == "land":
            # loc is enough - this is always a city!
            # go one step to each direction and pick the best
            move_options = map.land_routes[loc]
            compare = []
            for a in move_options:
                new_loc = loc + "-" + a[0] + "-" + str(1) + "-" + str(a[1] - 1)
                compare.append(closest_token_location(new_loc, unflipped, poor))
            transport_times[index] = min(compare)
        elif value == "sea":
            move_options = map.sea_routes[loc]
            compare = []
            for a in move_options:
                new_loc = loc + "-" + a[0] + "-" + str(1) + "-" + str(a[1] - 1)
                # poor is False so that this would not get stuck!
                if index == 1 and transport_times[0][0] < 13:
                    tester = np.array(
                        closest_token_location(new_loc, unflipped, poor=False)
                    )
                else:
                    tester = np.array(
                        closest_token_location(new_loc, unflipped, poor)
                    )
                # this condition is to not make it get stuck!
                if not (
                    index == 1
                    and transport_times[0][0] - 2 == tester[0]
                    and transport_times[0][0] < 13
                ):
                    tester += sea_coeff(money)
                compare.append(list(tester))
            transport_times[index] = min(compare)
        # air
        else:
            move_options = map.air_routes[loc]
            compare = []
            for a in move_options:
                if money == 300:
                    tester = np.array(
                        closest_token_location(a, unflipped, poor=True)
                    )
                else:
                    tester = np.array(
                        closest_token_location(a, unflipped, poor=False)
                    )
                tester += air_coeff(money)
                compare.append(list(tester))
            transport_times[index] = min(compare)
    return options[transport_times.index(min(transport_times))]


def choose_action_city(options):
    """Returns an action when the AI is targetting a city.

    This function will return an action when the AI is trying to go to
    either Gold Coast or Cape Town. The action is flip if available or
    otherwise it will be travel by land. Because it will never choose
    air or sea, there is no need to consider the situation when neither
    is an option."""
    if "flip" in options:
        return "flip"
    return "land"


def choose_city(destination, loc_strs, unflipped, money):
    """Returns the best option to get towards a city AI is targetting.

    This function chooses the best destination option. The best
    destination is decided with the following priority list:
    1) Gold Coast or Cape Town
    2) A city with an unflipped token. If there are several, choose
    the on which is the closest to home.
    3) The square which is closest to Gold Coast / Cape Town.

    Parameters
    ----------
    destination : str
        Either Gol (=Gold Coast) or Tow (=Cape Town)
    loc_strs : str
        The locations the player could reach this turn.
    unflipped : list of bool
        The variable from the Game object that contains the information
        which cities have an unflipped token.
    money : int
        How much money the player has this turn.

    Returns
    -------
    int: the best option of the loc_strs
    """
    # destination can be either Gol or Tow
    if "Gol" in loc_strs:
        return loc_strs.index("Gol")
    if "Tow" in loc_strs:
        return loc_strs.index("Tow")
    cities = [len(re.split(r"-", a)) == 1 for a in loc_strs]
    potentials = [
        value and unflipped[map.abbs.index(loc_strs[index])]
        for index, value in enumerate(cities)
    ]
    if sum(potentials) == 1:
        return potentials.index(1)
    if sum(potentials) == 0:
        distances = []
        for a in loc_strs:
            loc_str = re.split(r"-", a)
            if len(loc_str) == 1:  # a crossroads or a flipped city
                if destination == "Gol":
                    distances.append(map.dist_gol[map.abbs.index(loc_str[0])])
                else:
                    distances.append(map.dist_tow[map.abbs.index(loc_str[0])])
            else:
                if destination == "Gol":
                    dist_1 = map.dist_gol[map.abbs.index(loc_str[0])] + int(loc_str[2])
                    dist_2 = map.dist_gol[map.abbs.index(loc_str[1])] + int(loc_str[3])
                else:
                    dist_1 = map.dist_tow[map.abbs.index(loc_str[0])] + int(loc_str[2])
                    dist_2 = map.dist_tow[map.abbs.index(loc_str[1])] + int(loc_str[3])
                distances.append(min(dist_1, dist_2))
    else:
        distances = []
        for a in loc_strs:
            loc_str = re.split(r"-", a)
            if len(loc_str) > 1 or not unflipped[map.abbs.index(a)]:
                distances.append(np.inf)
            elif money == 0:
                distances.append(map.expected_time(money)[loc_str[0]][0])
            else:
                distances.append(map.expected_time(money - 100)[loc_str[0]][0])
    return distances.index(min(distances))
