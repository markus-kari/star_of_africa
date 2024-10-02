from functools import cache, lru_cache
import numpy as np
import re

# exceptions: four Capes, two locations starting with Dar
abbs = [
    "Add",
    "Ain",
    "Bah",
    "Can",
    "Con",
    "Dare",
    "Darf",
    "Dra",
    "Egy",
    "Gol",
    "Gua",
    "Kan",
    "Lak",
    "Mor",
    "Moz",
    "Oco",
    "Sah",
    "Sie",
    "Sla",
    "Sth",
    "Stm",
    "Sua",
    "Tam",
    "Tim",
    "Tow",
    "Tri",
    "Tun",
    "Ver",
    "Vic",
    "Wha",
    "Cai",
    "Tan",
    "nd0",
    "nd1",
    "nd2",
    "nd3",
    "nd4",
    "nd5",
    "nd6",
    "nd7",
    "nd8",
    "nd9",
]

full_names = [
    "Addis Abeba",
    "Ain-Galaka",
    "Bahr El Ghasal",
    "Canary Islands",
    "Congo",
    "Daressalam",
    "Dar-Fur",
    "Dragon Mountain",
    "Egypt",
    "Gold Coast",
    "Cape Guardafui",
    "Kandjama",
    "Lake Victoria",
    "Morocco",
    "Mozambique",
    "Ocomba",
    "Sahara",
    "Sierra Leone",
    "Slave Coast",
    "St. Helena",
    "Cape St. Marie",
    "Suakin",
    "Tamatave",
    "Timbuktu",
    "Capetown",
    "Tripoli",
    "Tunis",
    "Cape Verde",
    "Victoria Falls",
    "Whalefish Bay",
    "Cairo",
    "Tangier",
]

# dictionary: abbreviation to full name
abb_to_full = {abbs[x]: full_names[x] for x in range(32)}

# There are 10 crossroads ("nodes") in total on the map, marked as ndX
# e.g. node 0 is nd0
# Nodes along land routes:
# Node 0: between Morocco, Sahara and Tangier
# Node 1: between Gold Coast, Sierra Leone and Timbuktu
# Node 2: between Ain-Galaka, Dar-Fur, Kandjama and Slave Coast
# Node 3: between Daressalam, Lake Victoria and Mozambique
# Node 4: between Congo, Mozambique and node 5
# Node 5: between Dragon Mountain, Victoria Falls and node 4
# Nodes along the sea routes:
# Node 6: between Cairo, Tripoli and Tunis
# Node 7: between Cape Verde, Sierra Leone and St. Helena
# Node 8: between Congo, Gold Coast and Slave Coast
# Node 9: between Cape Town, St. Helena and Whalefish Bay

land_routes = {
    "Add": [("Gua", 3), ("Lak", 3), ("Sua", 3)],
    "Ain": [("Darf", 4), ("nd2", 4)],
    "Bah": [("Darf", 2), ("Lak", 2)],
    "Can": [],
    "Con": [("Kan", 3), ("Oco", 4), ("nd4", 8)],
    "Dare": [("Gua", 6), ("nd3", 1)],
    "Darf": [("Ain", 4), ("Bah", 2), ("Egy", 3), ("Sah", 8), ("Sua", 4), ("nd2", 4)],
    "Dra": [("Vic", 3), ("nd5", 2)],
    "Egy": [("Darf", 3), ("Tri", 6), ("Cai", 4)],
    "Gol": [("nd1", 2)],
    "Gua": [("Add", 3), ("Dare", 6)],
    "Kan": [("Con", 3), ("nd2", 2)],
    "Lak": [("Add", 3), ("Bah", 2), ("Oco", 4), ("nd3", 4)],
    "Mor": [("Ver", 8), ("nd0", 1)],
    "Moz": [("nd3", 2), ("nd4", 2)],
    "Oco": [("Con", 4), ("Lak", 4)],
    "Sah": [("Darf", 8), ("nd0", 4)],
    "Sie": [("Ver", 4), ("nd1", 3)],
    "Sla": [("Tim", 5), ("nd2", 3)],
    "Sth": [],
    "Stm": [("Tam", 4)],
    "Sua": [("Add", 3), ("Darf", 4)],
    "Tam": [("Stm", 4)],
    "Tim": [("Sla", 5), ("nd1", 2)],
    "Tow": [("Wha", 4)],
    "Tri": [("Egy", 6), ("Tun", 3)],
    "Tun": [("Tri", 3), ("Tan", 5)],
    "Ver": [("Mor", 8), ("Sie", 4)],
    "Vic": [("Dra", 3), ("Wha", 4), ("nd5", 2)],
    "Wha": [("Tow", 4), ("Vic", 4)],
    "Cai": [("Egy", 4)],
    "Tan": [("Tun", 5), ("nd0", 1)],
    "nd0": [("Mor", 1), ("Sah", 4), ("Tan", 1)],
    "nd1": [("Gol", 2), ("Sie", 3), ("Tim", 2)],
    "nd2": [("Ain", 4), ("Darf", 4), ("Kan", 2), ("Sla", 3)],
    "nd3": [("Dare", 1), ("Lak", 4), ("Moz", 2)],
    "nd4": [("Con", 8), ("Moz", 2), ("nd5", 1)],
    "nd5": [("Dra", 2), ("Vic", 2), ("nd4", 1)],
    "nd6": [],
    "nd7": [],
    "nd8": [],
    "nd9": [],
}

sea_routes = {
    "Add": [],
    "Ain": [],
    "Bah": [],
    "Can": [("Ver", 5), ("Tan", 3)],
    "Con": [("Wha", 5), ("nd8", 4)],
    "Dare": [],
    "Darf": [],
    "Dra": [],
    "Egy": [],
    "Gol": [("Sie", 5), ("nd8", 3)],
    "Gua": [("Moz", 8), ("Sua", 5), ("Tam", 8)],
    "Kan": [],
    "Lak": [],
    "Mor": [],
    "Moz": [("Gua", 8), ("Stm", 3)],
    "Oco": [],
    "Sah": [],
    "Sie": [("Gol", 5), ("nd7", 2)],
    "Sla": [("nd8", 1)],
    "Sth": [("nd7", 9), ("nd9", 8)],
    "Stm": [("Moz", 3), ("Tow", 8)],
    "Sua": [("Gua", 5), ("Cai", 4)],
    "Tam": [("Gua", 8)],
    "Tim": [],
    "Tow": [("Stm", 8), ("nd9", 2)],
    "Tri": [("nd6", 1)],
    "Tun": [("Tan", 3), ("nd6", 2)],
    "Ver": [("Can", 5), ("nd7", 1)],
    "Vic": [],
    "Wha": [("Con", 5), ("nd9", 3)],
    "Cai": [("Sua", 4), ("nd6", 3)],
    "Tan": [("Can", 3), ("Tun", 3)],
    "nd0": [],
    "nd1": [],
    "nd2": [],
    "nd3": [],
    "nd4": [],
    "nd5": [],
    "nd6": [("Tri", 1), ("Tun", 2), ("Cai", 3)],
    "nd7": [("Sie", 2), ("Sth", 9), ("Ver", 1)],
    "nd8": [("Con", 4), ("Gol", 3), ("Sla", 1)],
    "nd9": [("Sth", 8), ("Tow", 2), ("Wha", 3)],
}

air_routes = {
    "Add": [],
    "Ain": [],
    "Bah": [],
    "Can": [],
    "Con": ["Gol", "Wha"],
    "Dare": [],
    "Darf": ["Oco", "Sua", "Tri"],
    "Dra": ["Lak", "Tow"],
    "Egy": [],
    "Gol": ["Con", "Mor", "Tri", "Wha"],
    "Gua": ["Lak", "Tam"],
    "Kan": [],
    "Lak": ["Dra", "Gua", "Sua"],
    "Mor": ["Gol", "Sie", "Tan"],
    "Moz": [],
    "Oco": ["Darf", "Tow"],
    "Sah": [],
    "Sie": ["Mor", "Sth"],
    "Sla": [],
    "Sth": ["Sie", "Tow"],
    "Stm": ["Tow"],
    "Sua": ["Darf", "Lak", "Cai"],
    "Tam": ["Gua", "Tow"],
    "Tim": [],
    "Tow": ["Dra", "Oco", "Sth", "Stm", "Tam", "Wha"],
    "Tri": ["Darf", "Gol", "Tan"],
    "Tun": [],
    "Ver": [],
    "Vic": [],
    "Wha": ["Con", "Gol", "Tow"],
    "Cai": ["Sua"],
    "Tan": ["Mor", "Tri"],
    "nd0": [],
    "nd1": [],
    "nd2": [],
    "nd3": [],
    "nd4": [],
    "nd5": [],
    "nd6": [],
    "nd7": [],
    "nd8": [],
    "nd9": [],
}


@cache
def distances(place, poor):
    """Returns a list of distances to other nodes in the map.

    This function takes in a number refering to abbs and the player's
    financial status (whether the player has money or not) and returns
    a list of distances to all the different nodes in the board. If the
    player has money, the distance is simply the amount of steps to the
    node. If not, the distance through the sea is multiplied by 1.75
    (reflecting the fact that the movement through the sea is then
    slower.) The distances are calculated using Dijkstra's algorithm.

    Parameters
    ----------
    place : int
        The locations of the node that is being investigated.
        The number refers to its order in abbs, e.g. 0 is Add (i.e.
        Addis Abeba).
    poor : bool
        If the player has money or not.

    Returns
    -------
    dist: a list of the distances to other nodes in the map
    """
    size = 42
    dist = [np.inf] * size
    visited = [False] * size
    dist[place] = 0
    while not all(visited):
        comp = np.inf
        current = 0
        for x in range(size):
            if not visited[x] and dist[x] < comp:
                comp = dist[x]
                current = x
        for dest in land_routes[abbs[current]]:
            target = abbs.index(dest[0])
            dist[target] = min(dist[target], dist[current] + dest[1])
        for dest in sea_routes[abbs[current]]:
            target = abbs.index(dest[0])
            if poor:
                dist[target] = min(dist[target], dist[current] + 1.75 * dest[1])
            else:
                dist[target] = min(dist[target], dist[current] + dest[1])
        visited[current] = True
    return dist


@lru_cache
def closest_tokens(unflipped, poor):
    """Returns the distance of all nodes to the closest tokens.

    This function utilises the function distances and calculates the
    distances to the closest unflipped tokens. It returns then a sorted
    list for all nodes of the map.

    Please note that unflipped needs to be a tuple! The type list does
    not work because of the caching.

    Parameters
    ----------
    unflipped : tuple (not list!) of bool
        The variable from the Game object that contains the information
        which cities have an unflipped token.
    poor : bool
        If the player has money or not.

    Returns
    -------
    List of lists: the sorted distance to all the unflipped tokens from
    each node in order.
    """
    cities = np.array([distances(x, poor) for x in range(42) if unflipped[x]])
    return np.sort(np.transpose(cities))


dist_gol = [
    18,
    11,
    13,
    13,
    7,
    20,
    11,
    18,
    14,
    0,
    20,
    9,
    15,
    16,
    17,
    11,
    19,
    5,
    4,
    16,
    20,
    15,
    24,
    4,
    16,
    20,
    19,
    8,
    16,
    12,
    18,
    16,
    17,
    2,
    7,
    19,
    15,
    16,
    21,
    7,
    3,
    15,
]
dist_tow = [
    20,
    18,
    19,
    25,
    9,
    14,
    18,
    11,
    21,
    16,
    19,
    12,
    17,
    28,
    11,
    13,
    26,
    21,
    14,
    10,
    8,
    22,
    12,
    19,
    0,
    27,
    30,
    20,
    8,
    4,
    25,
    28,
    29,
    18,
    14,
    13,
    11,
    10,
    28,
    19,
    13,
    2,
]


@cache
def expected(n):
    """Returns the expected amount of dice rolls for the distance n."""
    if n < 1:
        return 0
    return (
        1/6 * (
            expected(n - 1)
            + expected(n - 2)
            + expected(n - 3)
            + expected(n - 4)
            + expected(n - 5)
            + expected(n - 6)
            + 6
        )
    )


@cache
def expected_time(money):
    """Returns the expected amount of turns to home for each location.

    This method uses the Dijkstra's algorithm and calculates the
    expected amount of turns needed to travel from each node of the
    board to either Cairo or Tangier (the closer one) with a given
    amount of money.

    Parameters
    ----------
    money : int
        The amount of money the player can spend.

    Returns
    -------
    dictionary
        The keys are the abbs, the values are tuples with three values:
        0 - The expected amount of turns
        1 - The fastest travel time for this amount of money (i.e.
        land, sea or air)
        2 - An array in which the first value refers to the first
        location in the shortest journey where the journey does not
        continue by land travel, the second value the amount of steps
        to there.
    """
    size = 42
    dist = [np.inf] * size
    visited = [False] * size
    dist[30] = 0
    dist[31] = 0
    travel_way = [""] * size
    # each element: first the target (or itself), then how many steps
    # describes the "chain" effect for land moving and sea moving in nodes
    chain = [None] * size
    chain[30] = np.array([30, 0])
    chain[31] = np.array([31, 0])
    while not all(visited):
        comp = np.inf
        current = 0
        for x in range(size):
            if not visited[x] and dist[x] <= comp:
                comp = dist[x]
                current = x
        for dest in land_routes[abbs[current]]:
            target = abbs.index(dest[0])
            benchmark = dist[target]
            if chain[current] is not None and chain[current][1] + dest[1] < 31:
                dist[target] = min(
                    benchmark,
                    dist[current] + expected(dest[1]),
                    dist[chain[current][0]] + expected(chain[current][1] + dest[1]),
                )
            else:
                dist[target] = min(benchmark, dist[current] + expected(dest[1]))
            if dist[target] != benchmark:
                chain[target] = chain[current] + [0, dest[1]]
                travel_way[target] = "land"
        for dest in sea_routes[abbs[current]]:
            target = abbs.index(dest[0])
            benchmark = dist[target]
            if money == 0:
                if "nd" in abbs[current]:
                    dist[target] = min(
                        benchmark,
                        dist[chain[current][0]]
                        + int((chain[current][1] + dest[1] + 1) / 2),
                    )
                else:
                    dist[target] = min(
                        benchmark, dist[current] + int((dest[1] + 1) / 2)
                    )
            else:
                if "nd" in abbs[current]:
                    dist[target] = min(
                        benchmark,
                        expected_time(money - 100)[abbs[chain[current][0]]][0]
                        + expected(chain[current][1] + dest[1]),
                    )
                # one doesn't need to pay in nodes, only in the harbour when one leaves
                elif "nd" in abbs[target]:
                    dist[target] = min(benchmark, dist[current] + expected(dest[1]))
                else:
                    dist[target] = min(
                        benchmark,
                        expected_time(money - 100)[abbs[current]][0]
                        + expected(dest[1]),
                    )
            if dist[target] != benchmark:
                if "nd" in dest[0]:
                    chain[target] = np.array([current, dest[1]])
                else:
                    chain[target] = np.array([target, 0])
                travel_way[target] = "sea"
        if money >= 300:
            for dest in air_routes[abbs[current]]:
                target = abbs.index(dest)
                benchmark = dist[target]
                dist[target] = min(
                    benchmark, expected_time(money - 300)[abbs[current]][0] + 1
                )
                if dist[target] != benchmark:
                    chain[target] = np.array([target, 0])
                    travel_way[target] = "air"
        visited[current] = True
    return {abbs[x]: (dist[x], travel_way[x], chain[x]) for x in range(42)}

def locstr(location, offshore, unflipped):
    """Returns a string which describes the location."""
    loc = re.split(r"-", location)
    # if the player is in a city
    if len(loc) == 1 and "nd" not in loc[0]:
        if loc[0] not in ["Cai", "Tan"]:
            if unflipped[abbs.index(loc[0])]:
                return f"{abb_to_full[loc[0]]} (the token has not yet been flipped)"
            return f"{abb_to_full[loc[0]]} (the token is already flipped)"
        return f"{abb_to_full[loc[0]]}"

    # in one of the crossroads on the land
    if len(loc) == 1 and not offshore:
        if loc[0] == "nd0":
            cities = "Tangier and Morocco"
        elif loc[0] == "nd1":
            cities = "Sierra Leone, Gold Coast and Timbuktu"
        elif loc[0] == "nd2":
            cities = "Ain-Galaka, Dar-Fur, Kandjama and Slave Coast"
        elif loc[0] == "nd3":
            cities = "Lake Victoria, Daressalam and Mozambique"
        elif loc[0] == "nd4":
            return ("the northeastern crossroads between Mozambique, " +
                "Dragon Mountains and Victoria Falls")
        # node 5
        else:
            return ("the southwestern crossroads between Mozambique, " +
                "Dragon Mountains and Victoria Falls")
        return f"the crossroads between {cities}"

    # in one of the crossroads on the sea
    if len(loc) == 1:
        if loc[0] == "nd6":
            cities = "Tunis, Tripoli and Cairo"
        elif loc[0] == "nd7":
            cities = "Cape Verde, Sierra Leone and St. Helena"
        elif loc[0] == "nd8":
            cities = "Gold Coast, Slave Coast and Congo"
        # node 9
        else:
            cities = "St. Helena, Whalesfish Bay and Capetown"
        return f"the crossroads between {cities} on the sea"

    # travelling by sea
    if offshore:
        # between a city and crossroads
        if "nd" in loc[0] or "nd" in loc[1]:
            if "nd" in loc[0]:
                crossroads = loc[0]
                other = loc[1]
            else:
                crossroads = loc[1]
                other = loc[0]
            if crossroads == "nd6":
                if other == "Tun":
                    direction = "east"
                # towards Cairo
                else:
                    direction = "west"
                direction = "northwest"
            elif crossroads == "nd7":
                if other == "Sie":
                    direction = "northwest"
                # towards St. Helena
                else:
                    direction = "north"
            elif crossroads == "nd8":
                if other == "Gol":
                    direction = "southeast"
                # towards Congo
                else:
                    direction = "northwest"
            # node 9
            else:
                if other == "Wha":
                    direction = "southwest"
                elif other == "Tow":
                    direction = "northwest"
                # towards St. Helena
                else:
                    direction = "southeast"
            if "nd" in loc[0]:
                return f"{loc[3]} step(s) {direction} of {abb_to_full[other]} by sea"
            return f"{loc[2]} step(s) {direction} of {abb_to_full[other]} by sea"

        # no crossroads involved
        return (f"{loc[3]} step(s) to {abb_to_full[loc[1]]}, " +
            f"{loc[2]} step(s) to {abb_to_full[loc[0]]} by sea")

    # travelling by land
    # between a city and crossroads
    if "nd" in loc[0] or "nd" in loc[1]:
        if "nd" in loc[0]:
            crossroads = loc[0]
            other = loc[1]
        else:
            crossroads = loc[1]
            other = loc[0]
        if crossroads == "nd0":
            direction = "northwest"
        elif crossroads == "nd1":
            if other == "Gol":
                direction = "north"
            elif other == "Sie":
                direction = "east"
            # towards Timbuktu
            else:
                direction = "southwest"
        elif crossroads == "nd2":
            if other == "Ain":
                direction = "south"
            elif other == "Darf":
                direction = "west"
            elif other == "Kan":
                direction = "north"
            # towards Slave Coast
            else:
                direction = "east"
        elif crossroads == "nd3":
            if other == "Lak":
                direction = "southeast"
            # towards Mozambique
            else:
                direction = "north"
        elif crossroads == "nd4":
            if other == "Con":
                direction = "southeast"
            # towards Mozambique
            else:
                direction = "southwest"
        # node 5
        else:
            direction = "northeast"
        if "nd" in loc[0]:
            return f"{loc[3]} step(s) {direction} of {abb_to_full[other]}"
        else:
            return f"{loc[2]} step(s) {direction} of {abb_to_full[other]}"

    # no crossroads involved
    return (f"{loc[3]} step(s) to {abb_to_full[loc[1]]}, " +
        f"{loc[2]} step(s) to {abb_to_full[loc[0]]}")
