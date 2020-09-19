import sub.plot
from matplotlib import pyplot
import matplotlib.cm as cm

PHOTO = True
colors = cm.rainbow([x / (120 - 1) for x in range(0, 120)])


def converge_plot(gen, order, name):
    objectives = [800 / chrom["result"]["objective"] for chrom in gen]
    pyplot.xlim(46.04669093735338, 4774.706328145873)

    pyplot.scatter(750, order, c="r", s=15, zorder=60)

    pyplot.hlines(order, min(objectives), max(objectives))
    pyplot.plot(
        objectives,
        [order] * len(objectives),
        "|",
        ms=30,
        zorder=0,
        color=colors[order],
    )

    pyplot.axis("off")

    if PHOTO:
        fig.savefig("res/" + f"{name:03d}" + ".png", transparent=False)
        pyplot.cla()


if __name__ == "__main__":
    fig = pyplot.figure(figsize=(10, 1.5))
    pyplot.subplots_adjust(left=0.03, right=0.94, top=0.82, bottom=0.1)
    data = sub.plot.get_data()

    for index, gen in enumerate(data):
        pyplot.cla()
        converge_plot(gen, index, index)
        pyplot.pause(0.01)

    # pyplot.show()
