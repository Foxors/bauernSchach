import pyxel
import matplotlib.pyplot as plt
import numpy as np
import json

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

    i = 0
    for d in savedData:
        print(f"{i}. from the {d['date'][2]}.{d['date'][1]}.{d['date'][0]} at {d['date'][3]}:{d['date'][4]}:{d['date'][5]} o'clock")

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
