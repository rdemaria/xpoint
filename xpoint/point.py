"""

TODO:
    - implement scaling
    - implement get_primitives, Line, PolyLine, Text, Distance
    - implement draw

"""


import re
import numpy as np
from scipy.spatial.transform import Rotation
from collections.abc import Iterable


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
    return obj.shape in shapes


class Point:
    """A point in 3D space with an orientation"""

    def __init__(self,
                 position=None,
                 name=None,
                 body=None,
                 style=None,
                 seq="zxy",
                 degrees=True,
                 ):
        self.matrix = np.eye(4)
        self.style = style
        self.name = name
        self.body = body
        self.seq = seq
        self.degrees = degrees
        if isinstance(position, Point):
            self.matrix[:] = position.matrix
        elif isinstance(position, Rotation):
            self.matrix[:3, :3] = position.as_matrix()
        else:
            position = np.array(position)
            if position.shape == (4, 4):
                self.matrix[:] = position
            elif position.shape == (3, 3):
                self.matrix[:3, :3] = position
            elif position.shape in ((3,), (2,), (1,)):
                self.matrix[3, :len(position)] = position

    @property
    def position(self):
        return self.matrix[3, :3]

    @position.setter
    def position(self, value):
        self.matrix[3, : len(value)] = value

    @property
    def x(self):
        return self.matrix[3, 0]

    @x.setter
    def x(self, value):
        self.matrix[3, 0] = value

    @property
    def y(self):
        return self.matrix[3, 1]

    @y.setter
    def y(self, value):
        self.matrix[3, 1] = value

    @property
    def z(self):
        return self.matrix[3, 2]

    @z.setter
    def z(self, value):
        self.matrix[3, 2] = value

    @property
    def rotation(self):
        return Rotation.from_matrix(self.matrix[:3, :3])

    @property
    def rotation_euler(self):
        return self.rotation.as_euler(seq=self.seq, degrees=self.degrees)

    @property
    def rotation_axis(self):
        return self.rotation.as_rotvec()

    @property
    def rotation_matrix(self):
        return self.rotation.as_matrix()

    @property
    def rotation_quat(self):
        return self.rotation.as_quat()

    @property
    def rotx(self):
        return self.rotation[0]

    @rotx.setter
    def rotx(self, rotx):
        self.matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq, angles=(
                rotx, self.roty, self.rotz), degrees=self.degrees
        ).as_matrix()

    @property
    def roty(self):
        return self.rotation[1]

    @roty.setter
    def roty(self, roty):
        self.matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq, angles=(
                self.rotx, roty, self.rotz), degrees=self.degrees
        ).as_matrix()

    @property
    def rotz(self):
        return self.rotation[2]

    @rotz.setter
    def rotz(self, rotz):
        self.matrix[:3, :3] = Rotation.from_euler(
            seq=self.seq, angles=(self.rotx, self.roty,
                                  rotz), degrees=self.degrees
        ).as_matrix()

    @property
    def scx(self):
        return np.linalg.norm(self.matrix[:3, 0])

    @property
    def scy(self):
        return np.linalg.norm(self.matrix[:3, 1])

    @property
    def scz(self):
        return np.linalg.norm(self.matrix[:3, 2])

    @property
    def scaling(self):
        return np.array([self.scx, self.scy, self.scz])

    def __add__(self, other):
        """Return lhs translated by rhs"""
        if isinstance(other, Point):
            return self.translate(other.position, inplace=False)
        else:
            return self.translate(other, inplace=False)

    def __mul__(self, other):
        """Return lhs rotate by rhs"""
        if isinstance(other, Point):
            return self.rotate(other.rotation, inplace=False)
        else:
            return self.rotate(other, inplace=False)

    def __sub__(self, other):
        """Return lhs translated by -rhs"""
        if isinstance(other, Point):
            return self.translate(-other.position, inplace=False)
        else:
            return self.translate(-other, inplace=False)

    def __truediv__(self, other):
        """Return lhs rotate by inv(rhs)"""
        if isinstance(other, Point):
            return self.rotate(-other.rotation, inplace=False)
        else:
            return self.rotate(-other, inplace=False)

    def __iadd__(self, other):
        """Translate lhs by rhs"""
        if isinstance(other, Point):
            return self.translate(other.position, inplace=True)
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
            return self.translate(-other.position, inplace=True)
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
        return Point(-self.position, -self.rotation)

    def __pos__(self):
        """Return copy of point"""
        return Point(self.position, self.rotation)

    def __repr__(self):
        return "Point({}, {})".format(self.position, self.rotation)

    def __str__(self):
        return "Point({}, {})".format(self.position, self.rotation)

    def __eq__(self, other):
        return (self.position == other.position) and (
            self.rotation == other.rotation
        )

    def __ne__(self, other):
        return not self == other

    def copy(self):
        return Point(self.matrix, seq=self.seq, degrees=self.degrees, name=self)

    def translate(self, x_or_position=0, y=0, z=0, local=True, inplace=False):
        if position := is_array_like(x_or_position, ((3,), (2,), (1,))):
            position = np.array(position)
        else:
            position = np.array([x_or_position, y, z])
        if inplace:
            point = self
        else:
            point = self.copy()
        if local:
            position = self.matrix@position
        point.position += position
        return point

    def rotate(self, axis, angle, degrees=True):
        self.rotation *= Rotation.from_euler(axis, angle, degrees=degrees)

    def transform(self, other):
        return self * other

    def __getitem__(self, key):
        return self.body[key].transform(self.matrix)

    def __setitem__(self, key, value):
        self.body[key] = value.transform(np.linalg.inv(self.matrix))

    def __iter__(self):
        return iter(self.body)

    def __len__(self):
        return len(self.body)

    def __contains__(self, key):
        return key in self.body

    def __delitem__(self, key):
        del self.body[key]

    def keys(self):
        return self.body.keys()

    def values(self):
        return (self.body[key] for key in self.body)

    def items(self):
        return ((key, self.body[key]) for key in self.body)

    def draw2d(self, projection='xy', backend='matplotlib'):
        from .canvas import Canvas2D

    def draw3d(self, backend='pyvista'):
        from .canvas import Canvas3D
