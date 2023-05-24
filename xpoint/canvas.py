import re


import matplotlib.pyplot as plt
import numpy as np

from .point import Point


def apply_style(primitive, style):
    """Apply style to primitive.

    The style is a dictionary of style properties. If a value is a dictions, the key is interpreted as selector.
     
    A selector is a string that optionally starts with a character that determines the type of selector,
      followed by a string that is used to match the selector. The following selectors are supported:

    * ``: Match the class name of primitive
    * `.`: Match the layer name of the primitive
    * `#`: Match the name of the primitive
    * `~`: Match the name of the primitive using a regular expression

    The following style properties are supported:

    * ``color``: The color of the primitive
    * ``linewidth``: The width of the line
    * ``linestyle``: The style of the line
    * ``marker``: The marker of the primitive
    * ``markersize``: The size of the marker
    * ``alpha``: The transparency of the primitive
    * ``label``: The label of the primitive
    * ``visible``: Whether the primitive is visible
    * ``zorder``: The z-order of the primitive
    * ``facecolor``: The face color of the primitive
    * ``edgecolor``: The edge color of the primitive
    * ``facealpha``: The face transparency of the primitive
    * ``edgealpha``: The edge transparency of the primitive
    * ``hatch``: The hatch of the primitive
    * ``fill``: Whether the primitive is filled
    * ``capstyle``: The cap style of the primitive
    * ``joinstyle``: The join style of the primitive
    * ``antialiased``: Whether the primitive is antialiased
    * ``dash_capstyle``: The cap style of the dash
    * ``solid_capstyle``: The cap style of the solid
    * ``dash_joinstyle``: The join style of the dash
    * ``solid_joinstyle``: The join style of the solid
    """
    result = {}
    if style is not None:
        for k, v in style.items():
            if isinstance(v, dict):  # k is a selector
                if k[0] == "." and primitive.layer == k[1:]:
                    result.update(v)
                elif k[0] == "#" and primitive.name == k[1:]:
                    result.update(v)
                elif (
                    k[0] == "~"
                    and isinstance(primitive.name, str)
                    and re.match(k[1:], primitive.name)
                ):
                    result.update(v)
                elif primitive.__class__.__name__ == k:
                    result.update(v)
            else:
                result[k] = v
    return result


class OrthoProjection:
    def __init__(self, left, right, bottom, top, near, far):
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
        self.matrix = matrix

    def __call__(self, coords):
        ones = np.ones((coords.shape[0], 1))
        points_h = np.hstack((coords, ones))
        points_p = self.matrix @ points_h.T
        points_p /= points_p[3]
        return points_p[:2].T


class PerspectiveProjection:
    def __init__(self, fov_y, aspect_ratio, near, far):
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
        self.matrix = matrix

    def __call__(self, coords):
        ones = np.ones((coords.shape[0], 1))
        points_h = np.hstack((coords, ones))
        points_p = self.matrix @ points_h.T
        points_p /= points_p[3]
        return points_p[:2].T


class Projection:
    def __init__(self, origin=(0, 0, 0), axes="xy", scaling=1, angles=None):
        self.origin = np.array(origin)
        self.axes = axes
        self.scaling = scaling
        self.angles = angles
        self.update()

    def update(self):
        self.matrix = np.zeros((2, 3), dtype=np.float64)
        if np.isscalar(self.scaling):
            if len(self.axes) == 2:
                self.scaling = (self.scaling, self.scaling, 0)
            else:
                self.scaling = (self.scaling, self.scaling, self.scaling)
        if self.angles is None:
            if len(self.axes) == 2:
                angles = (0, 90, 0)
            else:
                angles = (0, 120, 240)
        angles = np.radians(angles)
        for ai, ax in enumerate(self.axes):
            if ax not in "xyz":
                raise ValueError(f"Invalid axis {ax}")
            ii = "xyz".index(ax)
            self.matrix[0, ii] = self.scaling[ii] * np.cos(angles[ii])
            self.matrix[1, ii] = self.scaling[ii] * np.sin(angles[ii])

    def __call__(self, coords):
        return self.matrix @ (coords - self.origin).T

    def __repr__(self) -> str:
        return f"Projection(origin={self.origin}, axes={self.axes!r}, scaling={self.scaling}, angles={self.angles})"


class Canvas2DMPL:
    style_keywords = {
        "antialiased",
        "color",
        "dash_capstyle",
        "dash_joinstyle",
        "fillstyle",
        "linestyle",
        "linewidth",
        "marker",
        "markeredgecolor",
        "markeredgewidth",
        "markerfacecolor",
        "markerfacecoloralt",
        "markerpath",
        "markersize",
        "markevery",
        "sketch_params",
        "solid_capstyle",
        "solid_joinstyle",
        "visible",
        "zorder",
    }

    defaultstyle = {
        "Point": {"marker": "o", "color": "k", "markersize": 5},
        "Line": {"color": "k"},
        "PolyLine": {"color": "k"},
        "Text": {"color": "k", "fontsize": 10},
    }

    def __init__(
        self,
        axes="xy",
        scaling=1,
        origin=(0, 0, 0),
        xlabel="$x$ [m]",
        ylabel="$y$ [m]",
        title="",
        style=None,
    ):
        self.projection = Projection(origin=origin, axes=axes, scaling=scaling)
        self.origin = origin
        self.parts = {}  # stores parts and style
        self.artists = {}  # stores artists and reference to part
        if style is None:
            self.style = self.__class__.defaultstyle
        self.initialize(xlabel, ylabel, title)

    def project(self, point):
        return self.projection(point)

    def mpl_style_from_dict(self, style):
        mpl_style = {}
        for key in style:
            if key in self.__class__.style_keywords:
                mpl_style[key] = style[key]
        return mpl_style

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
        """
        Draw parts according to style.

        Priority of styles is:
        - style given to draw
        - style given when part was added
        - style of the part
        - style of the primitive given by the parent part
        - style of the primitive
        - style given when canvas was initialized
        """
        self.clear()
        for part, partstyle in self.parts.items():
            for prim, primstyle in part.get_primitives(partstyle):
                localstyle = self.style.copy()
                for st in style, prim.style, primstyle:
                    if st is not None:
                        localstyle.update(st)
                localstyle = apply_style(prim, localstyle)  # resolve selectors
                if localstyle.get("visible", True):
                    fname = "draw_" + prim.__class__.__name__.lower()
                    draw_func = getattr(self, fname)
                    artists = draw_func(prim, localstyle)
                    for art in artists:
                        self.artists[art] = part
        self.annotation = self.ax.text(
            0, 0, "", bbox=dict(boxstyle="round", fc="w")
        )
        self.annotation.set_visible(False)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.figure.show()
        self.figure.canvas.draw_idle()
        return self

    def draw_point(self, point, style):
        x, y = self.project(point.location)
        style = self.mpl_style_from_dict(style)
        print(point.location, x,y,style)
        (art,) = self.ax.plot([x], [y], picker=True, pickradius=3, **style)
        return [art]

    def draw_line(self, line, style):
        x = [line.a.location[0], line.b.location[0]]
        y = [line.a.location[1], line.b.location[1]]
        style = self.mpl_style_from_dict(style)
        (art,) = self.ax.plot(x, y, picker=True, pickradius=3, **style)
        return [art]

    def draw_polyline(self, polyline, style):
        x = [p.location[0] for p in polyline.points]
        y = [p.location[1] for p in polyline.points]
        style = self.mpl_style_from_dict(style)
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
        self.artists.clear()


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
