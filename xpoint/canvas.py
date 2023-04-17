from re import S
from tkinter import E
from turtle import st
import numpy as np
import matplotlib.pyplot as plt
from point import Point
from .style import apply_style


def projection_from_str(xy):
    p = np.zeros((3, 3), dtype=np.float64)
    p["xyz".index(0, xy[0])] = 1
    p["xyz".index(1, xy[1])] = 1


defaultstyle = {
    ".Point": {"marker": "o", "color": "k", "markersize": 5},
    ".Line": {"color": "k"},
    ".PolyLine": {"color": "k"},
    ".Text": {"color": "k", "fontsize": 10},
}


class OrthoProjection:
    def __init__(self, xy="xy", scaling=1, origin=(0, 0)):
        self.proj = np.zeros((3, 2), dtype=np.float64)
        self.proj[0, "xyz".index(xy[0])] = 1
        self.proj[1, "xyz".index(xy[1])] = 1

        if np.isscalar(scaling):
            sx, sy = scaling
        else:
            sx, sy = scaling
        self.proj[0, :] *= sx
        self.proj[1, :] *= sy
        self.origin = np.array(origin)

    def __call__(self, position):
        return self.proj @ position - self.origin


class Canvas2D:
    def __init__(
        self,
        projection="xy",
        scaling=1,
        origin=(0, 0),
        xlabel="x [m]",
        ylabel="y [m]",
        title="",
        style={},
    ):
        self.set_projection(projection, scaling, origin)
        self.set_backend(xlabel, ylabel, title)
        self.style = style
        self.artists = {}

    def set_projection(self, projection, scaling, origin):
        if type(projection is str):
            if len(projection) == 2:
                self.projection = OrthoProjection(projection, scaling, origin)
            else:
                raise ValueError("Projection string must be xy, xz, yz")
        else:
            self.projection = projection

    def set_backend(self, xlabel, ylabel, title):
        self.backend = CanvasMPL2D(xlabel=xlabel, ylabel=ylabel, title=title)
        self.backend.init()

    def draw(self, part, style=None):
        primitives = [self.projection(prim) for prim in part.get_primitives()]
        self.backend.draw(primitives, style)


class Canvas3D:
    def __init__(
        self,
        scaling=1,
        origin=(0, 0, 0),
        xlabel="x [m]",
        ylabel="y [m]",
        zlabel="z [m]",
        title="",
    ):
        self.projection = Point().scale(scaling).translate(origin)
        self.initialize(xlabel, ylabel, zlabel, title)
        self.primitives = {}
        self.artists = {}
        self.style = defaultstyle


class CanvasMPL2D:
    def __init__(self, xlabel="x [m]", ylabel="y [m]", title="", style=None):
        self.parts = {}
        self.artists = {}
        if style is None:
            self.style = defaultstyle
        self.initialize(xlabel, ylabel, title)


    def initialize(self, xlabel, ylabel, title):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.figure = plt.figure(hex(id(self)))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect("equal")
        cb1 = self.figure.canvas.mpl_connect(
            "motion_notify_event", self.on_motion_notify
        )
        cb2 = self.figure.canvas.mpl_connect("pick_event", self.on_pick)
        self.callbacks = [cb1, cb2]
        self.draw()

    def __del__(self):
        for cb in self.callbacks:
            self.figure.canvas.mpl_disconnect(cb)

    def add(self, *parts, style=None):
        for part in parts:
            self.parts[part]=style

    def remove(self, part):
        del self.parts[part]
        for art in self.artists[part]:
            art.remove()
        del self.artists[part]

    def draw(self, style=None):
        self.clear()
        for part,partstyle in self.parts.items():
            for prim,primstyle,ref in part.get_primitives(style):
                localstyle = self.style.copy()
                if primstyle is not None:
                    localstyle.update(primstyle)
                if partstyle is not None:
                    localstyle.update(partstyle)
                if style is not None:
                    localstyle.update(style)
                print(localstyle,style)
                localstyle = apply_style(prim, localstyle)
                print(localstyle)
                draw_func = getattr(self, "draw_" + prim.__class__.__name__.lower())
                artists = draw_func(prim, localstyle)
                for art in artists:
                    self.artists[art] = ref
        self.annotation = self.ax.text(0, 0, "", bbox=dict(boxstyle="round", fc="w"))
        self.annotation.set_visible(False)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.figure.show()
        self.figure.canvas.draw_idle()

    def draw_line(self, line, style):
        x = [line.a.pose.position[0], line.b.pose.position[0]]
        y = [line.a.pose.position[1], line.b.pose.position[1]]
        (art,) = self.ax.plot(x, y, picker=True, pickradius=3, **style)
        return [art]

    def draw_polyline(self, polyline, style):
        x = [p.pose.position[0] for p in polyline.points]
        y = [p.pose.position[1] for p in polyline.points]
        (art,) = self.ax.plot(x, y,picker=True, pickradius=3, **style)
        return [art]

    def draw_point(self, point, style):
        x = [point.pose.position[0]]
        y = [point.pose.position[1]]
        (art,) = self.ax.plot(x, y,picker=True, pickradius=3, **style)
        return [art]

    def on_motion_notify(self, event):
        if event.inaxes == self.ax:
            for art in self.artists:
                if art.contains(event)[0]:
                    self.annotation.set_text(self.artists[art].name)
                    self.annotation.set_x(event.xdata)
                    self.annotation.set_y(event.ydata)
                    self.annotation.set_visible(True)
                    self.last_hover = self.artists[art]
                    self.figure.canvas.draw_idle()
                    break
            else:
                self.annotation.set_visible(False)
                self.figure.canvas.draw_idle()

    def on_pick(self, event):
        self.pickevent = event
        self.last_picked = self.artists[event.artist]
        self.ax.text(
            event.mouseevent.xdata,
            event.mouseevent.ydata,
            self.last_picked.name,
            bbox=dict(boxstyle="round", fc="w"),
        )

    def clear(self):
        self.ax.clear()
