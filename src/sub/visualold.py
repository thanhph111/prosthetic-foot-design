import matplotlib.pyplot as pyplot
import matplotlib.patches as patches
import math
import cmath

from sub.inputprocess import RULES as RULES


points = [
    [114.40712390296207, 154.4548506587745],
    [155.83216298727956, 153.69293386572238],
    [158.73231133486775, 131.575630521931],
    [100.39661174612677, 97.96224914262834],
    [133.59506590428762, 34.38834774229362],
    [317.4845802401193, 28.45614216554591],
    [323.72203751729865, 11.091371502325634],
    [58.67622185352986, 10.24172336521795],
    [68.69993077132263, 29.048814235453474],
    [108.70961349716724, 32.43813789262146],
    [83.1338504234908, 71.65940041608457],
    [116.8888742298014, 135.3959448675419],
]


def point_plot(*points):
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]

    subplot.scatter(x_coords, y_coords, color="blue")


def line_plot(point1, point2):
    x_coords = [point1[0], point2[0]]
    y_coords = [point1[1], point2[1]]

    pyplot.plot(x_coords, y_coords, color="black", linewidth=1,)


def arc_plot(point1, point2, point3):
    point1, point2, point3 = map(
        lambda x: complex(*x), (point1, point2, point3)
    )

    delta = (point3 - point1) / (point2 - point1)
    center = (point1 - point2) * (
        delta - abs(delta) ** 2
    ) / 2j / delta.imag - point1
    radius = abs(center + point1)

    phases = [
        math.degrees(cmath.phase(center + point1)),
        math.degrees(cmath.phase(center + point3)),
    ]
    arc = patches.Arc(
        (-center.real, -center.imag),
        2 * radius,
        2 * radius,
        angle=0,
        theta1=max(phases),
        theta2=min(phases),
        fill=False,
        linewidth=1,
        color="black"
    )
    subplot.add_patch(arc)


def model_plot(points):
    point_plot(*points)

    for index in RULES["Lines"]:
        line_plot(point1=points[index[0] - 1], point2=points[index[1] - 1])

    for index in RULES["Arcs"]:
        arc_plot(
            point1=points[index[0] - 1],
            point2=points[index[1] - 1],
            point3=points[index[2] - 1],
        )


if __name__ == "__main__":
    fig = pyplot.figure()
    subplot = fig.add_subplot(111, frameon=True)

    subplot.set_aspect("equal", adjustable="box")

    model_plot(points)

    pyplot.show()
