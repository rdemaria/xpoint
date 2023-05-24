"""

TODO:
    - implement scaling
    - implement get_primitives, Line, PolyLine, Text, Distance
    - implement draw

"""

import re
from collections.abc import Iterable

import numpy as np
from scipy.spatial.transform import Rotation

from .style import apply_style


def direction(a: np.ndarray, b: np.ndarray):
    """return direction vector from a to b"""
    return (b - a) / np.linalg.norm(b - a)


def is_iterable(obj):
    """Check if object is iterable"""
    return hasattr(obj, "__iter__")


def is_array_like(obj, shapes: Iterable[int]):
    """Check if object is array like"""
    try:
        obj = np.array(obj)
        assert obj.shape in shapes
        return obj
    except (AssertionError, ValueError):
        return None


def has_shape(obj, shapes):
    return hasattr(obj, "shape") and obj.shape in shapes


class Point:
    """A point in 3D space with an orientation.

    Returns
    -------
    Point
        A new point object.

    Usage
    -----
    p = Point()
    p = Point(point)
    p = Point(matrix)
    p = Point(location, rotation, scaling)
    p = Point(x, y, z) # to be forbidden?
    p = Point(x=1, y=1, z=1, rx=1, ry=1, rz=3, scx=1, scy=1, scz=1)


    Parameters
    ----------
    matrix : array_like, optional
        A 4x4 transformation matrix.
    point : Point, optional
        A point with which to initialize this point's location, rotation, and scaling.
    location : array_like, optional
        A 3-element array specifying the x, y, and z coordinates of the point's location.
    rotation : array_like, optional
        A 3-element array specifying the point's rotation about the x, y, and z axes.
    scaling : array_like, optional
        A 3-element array specifying the point's scaling along the x, y, and z axes.
    x, y, z : float, optional
        The x, y, and z coordinates of the point's location.
    rx, ry, rz : float, optional
        The point's rotation about the x, y, and z axes, respectively.
    sx, sy, sz : float, optional
        The point's scaling along the x, y, and z axes, respectively.
    name : str, optional
        Name of the point.
    style : dict, optional
        Dictionary of style specifications.
    seq : str, optional
        Order of Euler angles. Default is 'zxy'.
    degrees : bool, optional
        If True, Euler angles are in degrees. If False, they are in radians. Default is True.
    """

    def __init__(self, *args, **kwargs):
        self._matrix = np.eye(4)
        self.name = kwargs.get("name")
        self.parts = kwargs.get("parts", {})
        self.seq = kwargs.get("seq", "zxy")
        self.degrees = kwargs.get("degrees", True)
        self.style = kwargs.get("style")
        if len(args) == 0 and len(kwargs) == 0:
            pass
        elif len(args) == 1:  # matrix or location or x
            if isinstance(args[0], Point):
                self._matrix[:, :] = args[0]._matrix
            elif is_iterable(args[0]):
                if has_shape(args[0], [(4, 4)]):
                    self.matrix = args[0]
                else:
                    self.location = args[0]
            else:
                self.location = args
        elif len(args) == 2:  # location,roration or x,y
            if is_iterable(args[0]) and is_iterable(args[1]):
                self.location = args[0]
                self.rotation = args[1]
            else:
                self.location = args
        elif len(args) == 3:  # localtion,rotation,scaling or x,y,z
            if all(map(is_iterable, args)):
                self.location = args[0]
                self.rotation = args[1]
                self.scaling = args[2]
            else:
                self.location = args
        elif len(args) > 3:
            raise ValueError(
                f"{self.__class__} takes at most 3 unnamed arguments"
            )
        if len(kwargs) > 0:
            for ll in [
                "point",
                "matrix",
                "location",
                "rotation",
                "scaling",
                "x",
                "y",
                "z",
                "rx",
                "ry",
                "rz",
                "sx",
                "sy",
                "sz",
            ]:
                if ll in kwargs:
                    setattr(self, ll, kwargs.pop(ll))
            for ll in kwargs:
                setattr(self, ll, kwargs[ll])

    # getters and setters
    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix[:] = value

    @property
    def location(self):
        return self._matrix[:3, 3]

    @location.setter
    def location(self, value):
        self._matrix[: len(value), 3] = value

    @property
    def x(self):
        return self._matrix[0, 3]

    @x.setter
    def x(self, value):
        self._matrix[0, 3] = value

    @property
    def y(self):
        return self._matrix[1, 3]

    @y.setter
    def y(self, value):
        self._matrix[1, 3] = value

    @property
    def z(self):
        return self._matrix[2, 3]

    @z.setter
    def z(self, value):
        self._matrix[2, 3] = value

    @property
    def dx(self):
        return self._matrix[:3, 0]

    @property
    def dy(self):
        return self._matrix[:3, 1]

    @property
    def dz(self):
        return self._matrix[:3, 2]

    @property
    def rotation_scipy(self):
        return Rotation.from_matrix(self._matrix[:3, :3])

    @property
    def rotation(self):
        return self.rotation_scipy.as_euler(seq=self.seq, degrees=self.degrees)

    @property
    def rotation_axis(self):
        return self.rotation_scipy.as_rotvec()

    @property
    def rotation_matrix(self):
        return self.rotation_scipy.as_matrix()

    @rotation_matrix.setter
    def rotation_matrix(self, value):
        self._matrix[:3, :3] = value

    @property
    def rotation_quat(self):
        return self.rotation_scipy.as_quat()

    @property
    def rz(self):
        return self.rotation[0]

    def _reorder_rotation(self, *xyz):
        return [xyz["xyz".index(ll)] for ll in self.seq]

    @rz.setter
    def rz(self, rz):
        self._matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq,
            angles=self._reorder_rotation(self.rx, self.ry, rz),
            degrees=self.degrees,
        ).as_matrix()

    @property
    def rx(self):
        return self.rotation[1]

    @rx.setter
    def rx(self, rx):
        self._matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq,
            angles=self._reorder_rotation(rx, self.ry, self.rz),
            degrees=self.degrees,
        ).as_matrix()

    @property
    def ry(self):
        return self.rotation[2]

    @ry.setter
    def ry(self, ry):
        self._matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq,
            angles=self._reorder_rotation(self.rx, ry, self.rz),
            degrees=self.degrees,
        ).as_matrix()

    @property
    def sx(self):
        return np.linalg.norm(self._matrix[:3, 0])

    @property
    def sy(self):
        return np.linalg.norm(self._matrix[:3, 1])

    @property
    def sz(self):
        return np.linalg.norm(self._matrix[:3, 2])

    @property
    def scaling(self):
        return np.array([self.sx, self.sy, self.sz])

    # generic methods

    def copy(self):
        return Point(self, seq=self.seq, degrees=self.degrees, name=self)

    def __repr__(self):
        out = []
        for ll in "x y z rx ry rz".split():
            val = getattr(self, ll)
            if val != 0:
                out.append(f"{ll}={val:.15g}")
        for ll in "sx sy sz".split():
            val = getattr(self, ll)
            if abs(val - 1) > 1e-15:
                out.append(f"{ll}={val}")
        args = ",".join(out)
        return f"Point({args})"

    # Operators to be confirmed

    def __add__(self, other):
        """Return lhs translated by rhs"""
        if isinstance(other, Point):
            return self.translate(other.location, inplace=False)
        else:
            return self.translate(other, inplace=False)

    def __mul__(self, other):
        """Return lhs rotate by rhs"""
        if isinstance(other, Point):
            return self.rotate(other.rotation_scipy, inplace=False)
        else:
            return self.rotate(other, inplace=False)

    def __sub__(self, other):
        """Return lhs translated by -rhs"""
        if isinstance(other, Point):
            return self.translate(-other.location, inplace=False)
        else:
            return self.translate(-other, inplace=False)

    def __truediv__(self, other):
        """Return lhs rotate by inv(rhs)"""
        if isinstance(other, Point):
            return self.rotate(-other.rotation_scipy, inplace=False)
        else:
            return self.rotate(-other, inplace=False)

    def __iadd__(self, other):
        """Translate lhs by rhs"""
        if isinstance(other, Point):
            return self.translate(other.location, inplace=True)
        else:
            return self.translate(other, inplace=True)

    def __imul__(self, other):
        """Rotate lhs by rhs"""
        if isinstance(other, Point):
            return self.rotate(other.rotation, inplace=True)
        else:
            return self.rotate(other, inplace=True)

    def __isub__(self, other):
        """Translate lhs by -rhs"""
        if isinstance(other, Point):
            return self.translate(-other.location, inplace=True)
        else:
            return self.translate(-other, inplace=True)

    def __itruediv__(self, other):
        """Rotate lhs by inv(rhs)"""
        if isinstance(other, Point):
            return self.rotate(-other.rotation, inplace=True)
        else:
            return self.rotate(-other, inplace=True)

    def __neg__(self):
        """Return inverse of point"""
        return Point(-self.location, self.rotation)

    def __pos__(self):
        """Return copy of point"""
        return self.copy()

    def __eq__(self, other):
        return (self.location == other.location) and (
            self.rotation == other.rotation
        )

    def __ne__(self, other):
        return not self == other

    @property
    def dup(self):
        return self.copy()

    # Part management

    def add_part(self, name, part):
        self.parts[name] = part
        part.parent = self

    def remove_part(self, name):
        self.parts[name].parent = None
        del self.parts[name]

    def iter_part(self):
        return self.parts.keys()

    # transformations
    def moveto(self, location=None, x=0, y=0, z=0):
        """
        Move by delta or (dx,dy,dz) in the point frame
        """
        if location is None:
            location = np.array(x, y, z)
        self.location = location
        return self

    def moveby(self, delta=None, dx=0, dy=0, dz=0):
        """
        Move by delta or (dx,dy,dz) in the point frame
        """
        if delta is None:
            delta = np.array((dx, dy, dz))
        self.location += self.rotation_matrix @ delta
        return self

    def rotate(self, axis, angle, degrees=True):
        self.rotation_scipy *= Rotation.from_euler(
            axis, angle, degrees=degrees
        )

    def transform(self, other):
        self._matrix = other._matrix @ self._matrix
        return self

    def arcby(self, angle, dx=0, dy=0, dz=0, axis="z", degrees=True):
        """
        Move the point to the end of an arc of circle tangent to the local direction specified by delta=(dx, dy, dz) and orthogonal to axis with pathlength =|delta| and arc angle = angle:
        """
        tangent = self._matrix[:3, :3] @ np.array([dx, dy, dz])
        if degrees:
            angle = np.deg2rad(angle)
            # roll = np.deg2rad(roll)
        if axis in "xyz":
            axis = getattr(self, "d" + axis)
        else:
            axis = np.asarray(axis)
        radius = np.cross(tangent,axis) / angle
        #    c=np.cos(angle)
        #    s=np.sin(angle)
        #    t=1-c
        #    rot = np.array([[t * axis[i] * axis[j] + c * (i == j) - s * axis[i] * axis[j]
        #                              for j in range(3)] for i in range(3)])
        rot = Rotation.from_rotvec(axis * angle, degrees=False).as_matrix()
        print(radius, rot @ radius, rot @ radius - radius, self.location)
        self.location = self.location + (rot @ radius - radius)
        self.rotation_matrix = rot @ self.rotation_matrix
        return self

    def lookat(self, x_or_location=0, y=0, z=0, axis="z"):
        """Rotate the point such that axis points to the given location"""
        if is_iterable(x_or_location):
            location = np.array(location)
        else:
            location = np.array([x_or_location, y, z])
        if axis in "xyz":
            axis = getattr(self, "d" + axis)
        else:
            axis = np.array(axis)
        self.rotation_scipy = Rotation.from_rotvec(
            axis
        ) * Rotation.from_rotvec(location - self.location)
        return self

    # parts interface

    def __getitem__(self, key):
        return self.parts[key].transform(self._matrix)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"Point has no attribute {key}")

    def __setitem__(self, name, part):
        localpart = part.transform(np.linalg.inv(self._matrix))
        self.add(name, localpart)

    def __iter__(self):
        return iter(self.parts)

    def __len__(self):
        return len(self.parts)

    def __contains__(self, key):
        return key in self.parts

    def __delitem__(self, key):
        del self.parts[key]

    def __hash__(self):
        return hash(id(self))

    def keys(self):
        return self.parts.keys()

    def values(self):
        return (self.parts[key] for key in self.parts)

    def items(self):
        return ((key, self.parts[key]) for key in self.parts)

    # Drawing interface

    def draw2d(self, projection="xy", style=None, canvas=None):
        if canvas is None:
            from .canvas import Canvas2DMPL as Canvas2D

            canvas = Canvas2D(axes=projection)
        canvas.add(self, style=style)
        canvas.draw()
        return canvas

    def draw3d(self, backend="pyvista"):
        from .canvas import Canvas3D

        canvas = Canvas3D(backend=backend)
        canvas.add(self)
        canvas.draw()
        return canvas

    def get_primitives(self, style=None, parent=None):
        """
        Return a list of (primitive, style, parent) to be drawn.
        """
        if parent is None:
            parent = self
        if style is None:
            style = self.style
        if style is None:
            style = {}
        out = []
        if len(self.parts) == 0 or style.get("draw_locations", False):
            out.append((self, style, parent))
        if style.get("draw_parts", True):
            for k, part in self.parts.items():
                out += part.get_primitives(style, parent)
        return out
