import pandas as pd
import numpy as np
import initialize
import matplotlib.pyplot as plt
import map
import csv

if __name__ == "__main__":
    df_ = pd.read_csv("statistics_big.csv")
    df = df_.astype(dtype={'Winner':'<U4', 'Turns': np.uint8, 'Horseshoe winner': bool, 'Star location': np.uint8})
    names = initialize.sample_names[:4]
    victories = np.array([len(df[df['Winner'] == name]) for name in names]) / len(df)
    horseshoes = len(df[df['Horseshoe winner']]) / len(df)
    turns = df['Turns']
    
    for key, value in enumerate(names):
        print(f"{value} won {round(victories[key]*100, 5)} % of the games.")
    print(f"{horseshoes * 100} % of the games were won by finding a horseshoe.")
    print(f"The game lasted on average {round(turns.mean(), 3)} and the standard deviation was {round(turns.std(), 3)}.")

    df['Turns'].plot.hist(bins=range(2, df['Turns'].max()), align='mid')
    plt.xlabel("Number of turns")
    plt.show()
    plt.close()

    turn_loc = np.zeros([30, 2])
    horseshoe_loc = np.zeros(30)
    winners_loc = np.zeros([30, 4])
    for x in range(30):
        data = df[df['Star location'] == x]
        turn_data = data['Turns']
        turn_loc[x] = [turn_data.mean(), turn_data.std()]
        horseshoe_loc[x] = len(data[data['Horseshoe winner']]) / len(data)
        winner_data = np.zeros(len(names))
        for key, value in enumerate(names):
            winner_data[key] = len(data[data['Winner'] == value])
        winners_loc[x] = winner_data

    # plot: mean and std of turns per loc
    plt.plot(turn_loc[:, 0], turn_loc[:, 1], '.', label='Data')
    x = [data for key, data in enumerate(turn_loc[:, 0]) if key not in [21, 26, 6, 16, 3]]
    y = [data for key, data in enumerate(turn_loc[:, 1]) if key not in [21, 26, 6, 16, 3]]
    a, b = np.polyfit(x, y, 1)
    plt.plot(turn_loc[:, 0], a * turn_loc[:, 0] + b, label='Regression line')
    plt.ylabel("Standard deviation of number of turns")
    plt.xlabel("Average number of turns")
    plt.legend()
    plt.show()
    plt.close()

    # horseshoe winners per loc
    for x in range(30):
        print(f"In {map.full_names[x]} {round(100*horseshoe_loc[x], 2)} % were won by horseshoe winner.")
    print(f"The average is {round(horseshoe_loc.mean() * 100, 2)} and the standard deviation {round(horseshoe_loc.std() * 100, 2)}")

    # plot: winners per loc
    winners = {}
    for key, value in enumerate(names):
        winners[value] = winners_loc[:, key]
    width = 0.4
    fig, ax = plt.subplots()
    bottom = np.zeros(30)
    for winner, win_count in winners.items():
        p = ax.bar(map.full_names[:30], win_count, width, label=winner, bottom=bottom)
        bottom += win_count
        ax.bar_label(p, label_type='center')
    ax.set_title('Number of victories by a player')
    ax.legend()
    plt.show()
    plt.close()

    max_turns = df['Turns'].max()+1
    turns_amount = np.zeros(max_turns)
    horseshoe_turns = np.zeros(max_turns)
    winners_turns = np.zeros([max_turns, 4])
    for x in range(2, max_turns):
        data = df[df['Turns'] == x]
        if len(data) == 0:
            continue
        turns_amount[x] = len(data)
        horseshoe_turns[x] = len(data[data['Horseshoe winner']]) / len(data)
        winner_data = np.zeros(len(names))
        for key, value in enumerate(names):
            winner_data[key] = len(data[data['Winner'] == value])
        winners_turns[x] = winner_data

    # horseshoe winner per turn
    for x in range(2, max_turns):
        print(f"If the game lasted {x} turns which happened {int(turns_amount[x])} times, {round(horseshoe_turns[x]*100, 2)} % were won by horseshoe winner.")

    # plot: winners per turn
    winners = {}
    for key, value in enumerate(names):
        winners[value] = winners_turns[:, key]
    width = 0.4
    fig, ax = plt.subplots()
    bottom = np.zeros(max_turns)
    for winner, win_count in winners.items():
        p = ax.bar([x for x in range(max_turns)], win_count, width, label=winner, bottom=bottom)
        bottom += win_count
        ax.bar_label(p, label_type='center')
    ax.set_title('Number of victories by a player')
    ax.legend()
    plt.show()
    plt.close()

    fieldnames = ['Location', 'Average turns', 'Standard deviation of turns', 'Horseshoe winners', 
                  'Won by A', 'Won by B', 'Won by C', 'Won by D'] 
    with open("location_stats.csv", "w", newline='') as file:
        header_writer = csv.DictWriter(file, fieldnames)
        header_writer.writeheader()
        writer = csv.writer(file)
        for x in range(30):
            writer.writerow(
                [map.full_names[x], 
                 round(turn_loc[x][0], 2), 
                 round(turn_loc[x][1], 2), 
                 round(100*horseshoe_loc[x], 2), 
                 round(winners_loc[x][0]/sum(winners_loc[x])*100, 2), 
                 round(winners_loc[x][1]/sum(winners_loc[x])*100, 2), 
                 round(winners_loc[x][2]/sum(winners_loc[x])*100, 2), 
                 round(winners_loc[x][3]/sum(winners_loc[x])*100, 2)]
                 )
