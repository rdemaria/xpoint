from re import S
from tkinter import E
from turtle import st

import matplotlib.pyplot as plt
import numpy as np

from .point import Point
from .style import apply_style


defaultstyle = {
    ".Point": {"marker": "o", "color": "k", "markersize": 5},
    ".Line": {"color": "k"},
    ".PolyLine": {"color": "k"},
    ".Text": {"color": "k", "fontsize": 10},
}


class Projection:
    @classmethod
    def orthographic(cls, left, right, bottom, top, near, far):
        """
        Compute the 2D projection matrix for an orthographic projection.

        Parameters:
        left, right: float
            The coordinates for the left and right planes of the viewing frustum.
        bottom, top: float
            The coordinates for the bottom and top planes of the viewing frustum.
        near, far: float
            The distance to the near and far planes of the viewing frustum.

        Returns:
        np.array, shape (4,4)
            The 2D projection matrix for the given orthographic projection.
        """
        matrix = np.zeros((4, 4))
        matrix[0, 0] = 2.0 / (right - left)
        matrix[1, 1] = 2.0 / (top - bottom)
        matrix[2, 2] = -2.0 / (far - near)
        matrix[3, 3] = 1.0
        matrix[0, 3] = -(right + left) / (right - left)
        matrix[1, 3] = -(top + bottom) / (top - bottom)
        matrix[2, 3] = -(far + near) / (far - near)
        return cls(matrix)

    def perspective(cls, fov_y, aspect_ratio, near, far):
        """
        Compute the 2D projection matrix for a perspective projection.

        Parameters:
        fov_y: float
            The vertical field of view in degrees.
        aspect_ratio: float
            The aspect ratio of the viewport (width/height).
        near, far: float
            The distance to the near and far planes of the viewing frustum.

        Returns:
        np.array, shape (4,4)
        The 2D projection matrix for the given perspective projection.
        """
        fov_y = np.radians(fov_y)
        tan_half_fov_y = np.tan(fov_y / 2.0)
        matrix = np.zeros((4, 4))
        matrix[0, 0] = 1.0 / (aspect_ratio * tan_half_fov_y)
        matrix[1, 1] = 1.0 / tan_half_fov_y
        matrix[2, 2] = -(far + near) / (far - near)
        matrix[2, 3] = -2.0 * far * near / (far - near)
        matrix[3, 2] = -1.0
        return cls(matrix)

    def __init__(self, matrix):
        self.matrix = matrix

    def __call__(self, coords):
        ones = np.ones((coords.shape[0], 1))
        points_h = np.hstack((coords, ones))
        points_p = self.matrix @ points_h.T
        points_p /= points_p[3]
        return points_p[:2].T


class SimpleProjection:
    @classmethod
    def from_string(cls, origin=(0, 0, 0), projection="xy", scaling=1):
        matrix = np.zeros((2, 3), dtype=np.float64)
        if len(projection) == 2:
            if isinstance(scaling, (int, float)):
                sx, sy =scaling, scaling
            else:
               sx, sy = scaling
            a1,a2=[(0,90).index(a) for a in projection]
            return cls.from_angles_scaling(origin=origin,angles=(a1,a2,0),scaling=(sx,sy,0))
            matrix[0, i1] = sx
            matrix[1, i2] = sy
        elif len(projection) == 3:
            angles=[(0,120,240).index(a) for a in projection]
            return cls.from_angles_scaling(origin=origin,angles=(a1,a2,0),scaling=scaling)

        return cls(origin, matrix)

    @classmethod
    def from_angles_scaling(cls, origin=(0, 0, 0), angles=(0, 120, 240), scaling=1):
        rx, ry, rz = np.radians(angles)
        if isinstance(scaling, (int, float)):
            sx, sy, sz = (scaling, scaling, scaling)
        else:
            sx, sy, sz = np.array(scaling)
        matrix = np.array(
            [
                [sx * np.cos(rx), sy * np.cos(ry), sz * np.cos(rz)]
                [sx * np.sin(rx), sy * np.sin(ry), sz * np.sin(rz)],
            ]
        )

    def __init__(self, origin, projection):
        self.origin = origin
        self.projection = projection

    def __call__(self, coords):
        return self.projection @ (coords - self.origin)


class Canvas2DMPL:
    def __init__(
        self,
        projection="xy",
        scaling=1,
        origin=(0, 0, 0),
        xlabel="x [m]",
        ylabel="y [m]",
        title="",
        style=None,
    ):

        self.update_projection(projection=projection, scaling=scaling, origin=origin)
        self.origin = origin
        self.parts = {}  # stores parts and style
        self.artists = {}  # stores artists and reference to part
        if style is None:
            self.style = defaultstyle
        self.initialize(xlabel, ylabel, title)

    def update_projection(self,projection='xy',scaling=1,origin=(0,0,0)):
        if isinstance(projection, str):
            self._projection = SimpleProjection.from_string(
                origin=origin, projection=projection, scaling=scaling
            )
        else:
            self.projection = projection

    def project(self, point):
        return point[self.projection]

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
            self.parts[part] = style

    def remove(self, part):
        del self.parts[part]
        for art in self.artists[part]:
            art.remove()
        del self.artists[part]

    def draw(self, style=None):
        self.clear()
        for part, partstyle in self.parts.items():
            for prim, primstyle, ref in part.get_primitives(style):
                localstyle = self.style.copy()
                if primstyle is not None:
                    localstyle.update(primstyle)
                if partstyle is not None:
                    localstyle.update(partstyle)
                if style is not None:
                    localstyle.update(style)
                print(localstyle, style)
                localstyle = apply_style(prim, localstyle)
                print(localstyle)
                draw_func = getattr(
                    self, "draw_" + prim.__class__.__name__.lower()
                )
                artists = draw_func(prim, localstyle)
                for art in artists:
                    self.artists[art] = ref
        self.annotation = self.ax.text(
            0, 0, "", bbox=dict(boxstyle="round", fc="w")
        )
        self.annotation.set_visible(False)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.figure.show()
        self.figure.canvas.draw_idle()

    def draw_line(self, line, style):
        x = [line.a.position[0], line.b.position[0]]
        y = [line.a.position[1], line.b.position[1]]
        (art,) = self.ax.plot(x, y, picker=True, pickradius=3, **style)
        return [art]

    def draw_polyline(self, polyline, style):
        x = [p.position[0] for p in polyline.points]
        y = [p.position[1] for p in polyline.points]
        (art,) = self.ax.plot(x, y, picker=True, pickradius=3, **style)
        return [art]

    def draw_point(self, point, style):
        x = [point.position[0]]
        y = [point.position[1]]
        (art,) = self.ax.plot(x, y, picker=True, pickradius=3, **style)
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
