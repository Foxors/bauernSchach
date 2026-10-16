import pyxel
import matplotlib.pyplot as plt
import numpy as np
import json

def create_bot_tournament_plot(savedData, botName):
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots()

    colors = [ "blue", "red", "green", "orange", "yellow", "purple", "pink", "aqua", "black", "gold", "brown" ]

    tournament_index = 0

    for tournament in savedData:
        # Skip tournaments that don't include this bot.
        if not any(bot["name"] == botName for bot in tournament["results"]):
            continue

        # Build cumulative wins: start at zero, then update after each game.
        wins = [0]
        total = 0

        for winner in tournament["winnerTimeline"]:
            if winner == botName:
                total += 1
            wins.append(total)

        date = tournament["date"]
        label = (
            f"{date[2]}.{date[1]}.{date[0]} "
            f"{date[3]:02}:{date[4]:02}:{date[5]:02} "
            f"board: {tournament["size"]}x{tournament["size"]}"
        )

        # stairs() requires one more edge than values.
        ax.stairs(
            wins,
            range(len(wins) + 1),
            label=label,
            linewidth=1.5,
            color=colors[tournament_index % len(colors)]
        )

        tournament_index += 1

    if tournament_index == 0:
        print(f"No tournaments found for bot '{botName}'.")
        plt.close(fig)
        return

    ax.set_xlabel("Game")
    ax.set_ylabel(f"Cumulative wins — {botName}")
    ax.set_title(f"{botName}: wins across tournaments")
    ax.legend(title="Tournament")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    plt.show()

def create_plot(data):
    print("Calculating…")

    # Calculating graph
    scores = {}
    for bot in data['results']:
        scores[bot['name']] = [0]
    
    for winner in data['winnerTimeline']:
        for botName, yVal in scores.items():
            yVal.append(yVal[-1])

        scores[winner][-1] += 1
    
    # Remove last 0 element
    for botName, yVal in scores.items():
        yVal.pop()

    print("Plotting…")
    plt.style.use('_mpl-gallery')

    fig, ax = plt.subplots()

    colors = [ "blue", "red", "green", "orange", "yellow", "purple", "pink", "navy", "aqua" ]
    botColor = 0
    highest = 1

    # Plot A and B as separate colored lines.
    for botName, yVal in scores.items():

        ax.stairs(
            yVal,
            linewidth=1,
            label=botName,
            color=colors[botColor]
        )

        botColor += 1
        highest = max(highest, yVal[-1])

    ax.set_xlabel("Game")
    ax.set_ylabel("Wins")
    ax.set_title("Wins per bot over time")
    #fig.tight_layout(rect=(0.079, 0.047, 0.984, 0.968))
    fig.tight_layout()


    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.show()

def create_plot(data):
    print("Calculating…")

    # Calculating graph
    scores = {}
    for bot in data['results']:
        scores[bot['name']] = [0]
    
    for winner in data['winnerTimeline']:
        for botName, yVal in scores.items():
            yVal.append(yVal[-1])

        scores[winner][-1] += 1
    
    # Remove last 0 element
    for botName, yVal in scores.items():
        yVal.pop()

    print("Plotting…")
    plt.style.use('_mpl-gallery')

    fig, ax = plt.subplots()

    colors = [ "blue", "red", "green", "orange", "yellow", "purple", "pink" ]
    botColor = 0
    highest = 1

    # Plot A and B as separate colored lines.
    for botName, yVal in scores.items():

        ax.stairs(
            yVal,
            linewidth=1,
            label=botName,
            color=colors[botColor]
        )

        botColor += 1
        highest = max(highest, yVal[-1])

    ax.set_xlabel("Game")
    ax.set_ylabel("Wins")
    ax.set_title("Wins per bot over time")
    #fig.tight_layout(rect=(0.079, 0.047, 0.984, 0.968))
    fig.tight_layout()


    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.show()

def main():
    saveDir = "tournamentResults.json"

    savedData = []
    with open(saveDir, "r") as f:
        savedData = json.load(f)

    view = input("Want to see only one bot? [y/n]: ")
    if (view == 'y'):
        botName = input("Bot name to compare across tournaments: ")
        create_bot_tournament_plot(savedData, botName)
        return

    i = 0
    for d in savedData:
        print(f"{i}. from the {d['date'][2]}.{d['date'][1]}.{d['date'][0]} at {d['date'][3]}:{d['date'][4]}:{d['date'][5]} o'clock")
        i += 1

    selData = -1
    while (selData < 0 or selData >= len(savedData)):
        try:
            selData = int(input("Input the one you want to see: "))
        except: selData = -1

    d = savedData[selData]
    print(f"\nOn {d['date'][2]}.{d['date'][1]}.{d['date'][0]} at {d['date'][3]}:{d['date'][4]}:{d['date'][5]} o'clock")
    print(f"Played {d['gamesPlayed']} on a {d['size']} cell sized board")
    for bot in d['results']:
        print(f" - {bot['name']} won {bot['wins']} times")

    input("press enter to continue...")

    create_plot(d)

if __name__ == "__main__":
    main()
