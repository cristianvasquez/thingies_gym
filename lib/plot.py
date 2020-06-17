import matplotlib.pyplot as plt
from numpy import np


def drawValueFunction(V, gridWorld, policy):
    fig, ax = plt.subplots()
    im = ax.imshow(np.reshape(V, (-1, gridWorld.getWidth())))
    for cell in gridWorld.getCells():
        p = cell.getCoords()
        i = cell.getIndex()
        if not cell.isGoal():
            text = ax.text(p[1], p[0], str(policy[i]),
                           ha="center", va="center", color="w")
        if cell.isGoal():
            text = ax.text(p[1], p[0], "X",
                           ha="center", va="center", color="w")
    plt.show()
