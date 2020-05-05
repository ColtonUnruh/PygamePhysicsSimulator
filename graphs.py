import matplotlib.pyplot as plt


def show_plot(group):
    print(group.t[-1])
    plt.subplot(2, 1, 1)
    for ball in group:
        plt.plot(group.t, ball.displacement, color=normalize(ball.color), marker="")

    plt.title("Distance traveled and velocity")
    plt.ylabel("Distance traveled (pixels)")

    plt.subplot(2, 1, 2)
    for ball in group:
        plt.plot(group.t, ball.speed, color=normalize(ball.color), marker="")

    plt.ylabel("Velocity (pixels per second)")
    plt.xlabel("Time (seconds)")

    plt.show()


def normalize(c):
    return [x/255 for x in c]