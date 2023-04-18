import re
import numpy as np
from scipy.spatial.transform import Rotation
from collections.abc import Iterable


def direction(a: np.ndarray, b: np.ndarray):
    """return direction vector from a to b"""
    return (b - a) / np.linalg.norm(b - a)


def is_array_like(obj, shapes: Iterable[int]):
    """Check if object is array like"""
    try:
        obj = np.array(obj)
        assert obj.shape in shapes
        return obj
    except (AssertionError, ValueError):
        return False


class Point:
    """A point in 3D space with an orientation"""

    def __init__(
        self,
        x_or_position_or_matrix_or_point=None,
        y_or_rotation=None,
        z_or_scaling=None,
        rotz=0,
        rotx=0,
        roty=0,
        scx=1,
        scy=1,
        scz=1,
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
        if x_or_position_or_matrix_or_point is None:
            return
        # one arg definition: Point, matrix 3x3 or 4x4
        elif isinstance(x_or_position_or_matrix_or_point, Point):
            self.set_matrix(x_or_position_or_matrix_or_point.matrix)
        elif matrix := is_array_like(
                x_or_position_or_matrix_or_point, ((4, 4), (3, 3))
        ):
            self.set_matrix(matrix, style=style, name=name, body=body)
        else:  # (position, rotation, scaling)
            if position := is_array_like(
                x_or_position_or_matrix_or_point, ((3,), (2,), (1,))
            ):
                self.position = position
            if rotation := is_array_like(y_or_rotation, ((3,), (2,), (1,))):
                self.set_rotation(rotation, degrees=degrees, seq=seq)
            else:
                self.set_rotation((rotx, roty, rotz), degrees=degrees, seq=seq)
            if scaling := is_array_like(z_or_scaling, ((3,), (2,), (1,))):
                self.scaling = scaling
            else:
                self.scaling = (scx, scy, scz)

    def set_matrix(self, matrix=None):
        """Create a point from a 4x4 matrix"""
        if matrix is not None:
            try:
                matrix = np.array(matrix)
            except ValueError:
                raise ValueError("matrix must be 4x4 or 3x3 array or list")
        if matrix.shape == (3, 3):
            matrix = np.eye(4)
            matrix[:3, :3] = matrix
        elif matrix.shape == (4, 4):
            self.matrix[:] = matrix
        else:
            raise ValueError("matrix must be 4x4 or 3x3")

    def set_rotation(self, rotation=None, rotx=0, roty=0, rotz=0, degrees=True, seq="zxy"):
        """Set rotation from Rotation, 3x3 matrix, euler angles or quaternion"""
        if rotation is None:
            rotmat = Rotation.from_euler(
                seq, (rotx, roty, rotz), degrees=degrees
            ).as_matrix()
        elif isinstance(rotation, Rotation):
            rotmat = rotation.as_matrix()
        elif rotation is not None:  # try to use array
            try:
                rotation = np.array(rotation)
            except ValueError:
                raise ValueError("rotation must Rotation, 3x1 or 4x1 array")
            if rotation.shape == (3, 3):
                self.matrix[:3, :3] = rotation
            elif rotation.shape == (4,):
                self.matrix[:3, :3] = Rotation.from_quat(rotation).as_matrix()
            else:
                self.matrix[:3, :3] = Rotation.from_euler(
                    seq, rotation, degrees=degrees
                ).as_matrix()
        else:
            raise ValueError("rotation must be Rotation, 3x1 or 4x1 array")
        self.matrix[:3, :3] = rotmat

    def apply_scaling(self, scaling):
        """Apply scaling to point"""
        scalingv = np.ones(4)
        if scaling is not None:
            if scaling := is_array_like(scaling, ((3,), (2,), (1,))):
                scalingv[: len(scaling)] = scaling
            else:
                try:
                    scaling[:3] = scaling
                except ValueError:
                    raise ValueError("scaling must be 3x1 array or list")
            self.matrix @= scaling

    def set_xyz(
        self,
        x=None,
        y=None,
        z=None,
        rotx=None,
        roty=None,
        rotz=None,
        scx=None,
        scy=None,
        scz=None,
        seq="zxy",
        degrees=True,
    ):
        """Set position, rotation and scaling"""
        self.set_position((x, y, z))
        self.set_rotation((rotx, roty, rotz), seq=seq, degrees=degrees)
        self.apply_scaling((scx, scy, scz))

    @property
    def position(self):
        return self.matrix[3, :3]

    @position.setter
    def set_position(self, value):
        self.matrix[3, :len(value)] = value

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
        return self.rotation.as_euler("zxy")

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
        return self.rotation.as_euler("x")

    @rotx.setter
    def rotx(self, rotx):
        self.rotation = Rotation.from_euler(
            "xyz", (rotx, self.roty, self.rotz)
        ).as_matrix()

    @property
    def roty(self):
        return self.rotation.as_euler("y")

    @roty.setter
    def roty(self, roty):
        self.rotation = Rotation.from_euler(
            "xyz", (self.rotx, roty, self.rotz)
        ).as_matrix()

    @property
    def rotz(self):
        return self.rotation.as_euler("z")

    @rotz.setter
    def rotz(self, rotz):
        self.rotation = Rotation.from_euler(
            "xyz", (self.rotx, self.roty, rotz)
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
            return self.moveby(other.position, inplace=False)
        else:
            return self.moveby(other, inplace=False)

    def __mul__(self, other):
        """Return lhs rotate by rhs"""
        if isinstance(other, Point):
            return self.rotateby(other.rotation, inplace=False)
        else:
            return self.rotateby(other, inplace=False)

    def __sub__(self, other):
        """Return lhs translated by -rhs"""
        if isinstance(other, Point):
            return self.moveby(-other.position, inplace=False)
        else:
            return self.moveby(-other, inplace=False)

    def __truediv__(self, other):
        """Return lhs rotate by inv(rhs)"""
        if isinstance(other, Point):
            return self.rotateby(-other.rotation, inplace=False)
        else:
            return self.rotateby(-other, inplace=False)

    def __iadd__(self, other):
        """Translate lhs by rhs"""
        if isinstance(other, Point):
            return self.moveby(other.position, inplace=True)
        else:
            return self.moveby(other, inplace=True)

    def __imul__(self, other):
        """Rotate lhs by rhs"""
        if isinstance(other, Point):
            return self.rotateby(other.rotation, inplace=True)
        else:
            return self.rotateby(other, inplace=True)

    def __isub__(self, other):
        """Translate lhs by -rhs"""
        if isinstance(other, Point):
            return self.moveby(-other.position, inplace=True)
        else:
            return self.moveby(-other, inplace=True)

    def __itruediv__(self, other):
        """Rotate lhs by inv(rhs)"""
        if isinstance(other, Point):
            return self.rotateby(-other.rotation, inplace=True)
        else:
            return self.rotateby(-other, inplace=True)

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

    def translate(self, position, local=True):
        if local:
            self.position += self.rotation.apply(position)
        return self

    def rotate(self, axis, angle, degrees=True):
        self.rotation *= Rotation.from_euler(axis, angle, degrees=degrees)

    def transform(self, other):
        return self * other
