import numpy as np
from matplotlib.backend_bases import MouseButton
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import matplotlib.patches as patches
import matplotlib.pyplot as pyplot

from sub.inputprocess import RULES as RULES
import math
import cmath


def model_plot(points, subplot):

    def point_plot(*points):
        x_coords = [point[0] for point in points]
        y_coords = [point[1] for point in points]

        subplot.scatter(x_coords, y_coords, color="blue")

    def line_plot(point1, point2):
        x_coords = [point1[0], point2[0]]
        y_coords = [point1[1], point2[1]]

        pyplot.plot(
            x_coords, y_coords, color="black", linewidth=1,
        )

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
            color="black",
        )
        subplot.add_patch(arc)

    point_plot(*points)

    for index in RULES["Lines"]:
        line_plot(point1=points[index[0] - 1], point2=points[index[1] - 1])

    for index in RULES["Arcs"]:
        arc_plot(
            point1=points[index[0] - 1],
            point2=points[index[1] - 1],
            point3=points[index[2] - 1],
        )
    return subplot

class PathInteractor:
    """
    An path editor.

    Press 't' to toggle vertex markers on and off.  When vertex markers are on,
    they can be dragged with the mouse.
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, pathpatch):

        self.ax = pathpatch.axes
        canvas = self.ax.figure.canvas
        self.pathpatch = pathpatch
        self.pathpatch.set_animated(True)

        x, y = zip(*self.pathpatch.get_path().vertices)
        temp = [[x[i], y[i]] for i in range(len(x))]
        abc = model_plot(temp, self.ax)
        self.line = abc
        # (self.line,) = ax.plot(
        #     x, y, marker="o", markerfacecolor="r", animated=True
        # )

        self._ind = None  # the active vertex

        canvas.mpl_connect("draw_event", self.on_draw)
        canvas.mpl_connect("button_press_event", self.on_button_press)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        canvas.mpl_connect("button_release_event", self.on_button_release)
        canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas = canvas

    def get_ind_under_point(self, event):
        """
        Return the index of the point closest to the event position or *None*
        if no point is within ``self.epsilon`` to the event position.
        """
        # display coords
        xy = np.asarray(self.pathpatch.get_path().vertices)
        xyt = self.pathpatch.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x) ** 2 + (yt - event.y) ** 2)
        ind = d.argmin()

        if d[ind] >= self.epsilon:
            ind = None

        return ind

    def on_draw(self, event):
        """Callback for draws."""
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.pathpatch)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_button_press(self, event):
        """Callback for mouse button presses."""
        if (
            event.inaxes is None
            or event.button != MouseButton.LEFT
            or not self.showverts
        ):
            return
        self._ind = self.get_ind_under_point(event)

    def on_button_release(self, event):
        """Callback for mouse button releases."""
        if event.button != MouseButton.LEFT or not self.showverts:
            return
        self._ind = None

    def on_key_press(self, event):
        """Callback for key presses."""
        if not event.inaxes:
            return
        if event.key == "t":
            self.showverts = not self.showverts
            # self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        self.canvas.draw()

    def on_mouse_move(self, event):
        """Callback for mouse movements."""
        if (
            self._ind is None
            or event.inaxes is None
            or event.button != MouseButton.LEFT
            or not self.showverts
        ):
            return

        vertices = self.pathpatch.get_path().vertices

        vertices[self._ind] = event.xdata, event.ydata
        # self.line.set_data(zip(*vertices))

        x, y = zip(*self.pathpatch.get_path().vertices)
        temp = [[x[i], y[i]] for i in range(len(x))]
        self.ax.clear()
        self.line = model_plot(temp, self.ax)

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.pathpatch)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)


fig, ax = pyplot.subplots(frameon=False)
pyplot.axis('off')

pathdata = [
    (Path.MOVETO, (114.40712390296207, 154.4548506587745)),
    (Path.MOVETO, (155.83216298727956, 153.69293386572238)),
    (Path.MOVETO, (158.73231133486775, 131.575630521931)),
    (Path.MOVETO, (10.39661174612677, 97.96224914262834)),
    (Path.MOVETO, (13.59506590428762, 34.38834774229362)),
    (Path.MOVETO, (31.4845802401193, 28.45614216554591)),
    (Path.MOVETO, (32.72203751729865, 11.091371502325634)),
    (Path.MOVETO, (58.67622185352986, 10.24172336521795)),
    (Path.MOVETO, (68.69993077132263, 29.048814235453474)),
    (Path.MOVETO, (10.70961349716724, 32.43813789262146)),
    (Path.MOVETO, (83.1338504234908, 71.65940041608457)),
    (Path.CLOSEPOLY, (116.8888742298014, 135.3959448675419)),
]

codes, verts = zip(*pathdata)
path = Path(verts, codes)
patch = PathPatch(path, facecolor="green", edgecolor="yellow", alpha=0.5)
ax.add_patch(patch)

interactor = PathInteractor(patch)
ax.set_aspect("equal", adjustable="box")
ax.set_title("drag vertices to update path")

pyplot.show()
