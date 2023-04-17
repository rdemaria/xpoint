"""
Each part has at least a pose.
A part can have a dictionary of parts.
Each part can inherit attributes from a template
Part can be subclassed to obtain special behaviours

clone(pose):  generate a part with a new pose, and a self parent

__init__: convenient initialization
from_parent(): setclass and parent

.parts[]: contains defintions of subparts in the local reference frame
[]: returns clones at the part reference frame

edit(): makes a shallowcopy and store under root




"""

from symbol import return_stmt
import numpy as np

from .style import ProxyDict, apply_style
from .pose import Pose
from .canvas import Canvas3D

class Part:
    @classmethod
    def from_parent(cls, template, container):
        self = cls.__new__(cls)
        self.container = container
        self.template = template
        self.parts = ProxyDict().set_proxy(template.parts)
        self._cached={}
        return self

    def __init__(self, pose=None, name=None, template=None, parts=None, container=None):
        self.name = name
        if pose is None:
            self.local_pose = Pose()
        elif isinstance(pose, Pose):
            self.local_pose = pose
        elif isinstance(pose, Part):
            self.local_pose = pose.pose
        else:
            self.local_pose = Pose(pose)
        self.container = container
        self.set_template(template, parts)
        self._cached={}

    def __repr__(self):
        if self.name is not None:
            name=f"'{self.name}'"
        else:
            name=f"{hex(id(self))}"
        return f"<{self.__class__.__name__} {name} at {self.pose.position}>"

    @property
    def pose(self):
        if self.container is None:
            return self.local_pose
        else:
            return self.container.pose.transform(self.local_pose)

    def set_template(self, template, parts):
        if parts is None:
            parts = {}
        self.template = template
        if template is None:
            self.parts = parts
        else:
            self.parts = ProxyDict(parts).set_proxy(template.parts)

    def __getitem__(self, k):
        if k in self._cached:
            return self._cached[k]
        else:
            if k in self.parts:
                return self.parts[k].clone(container=self)

    def clone(self, container=None):
        return self.__class__.from_parent(template=self, container=container)

    def __getattr__(self, k):
        if self.template is not None and hasattr(self.template, k):
            return getattr(self.template, k)
        elif k in self.parts:
            return self[k]
        else:
            raise AttributeError


    def get_primitives(self, style):
        style = apply_style(self, style)
        out=[]
        if style.get("draw_subparts",True) == True:
            for k, part in self.parts.items():
                out += part.get_primitives(style)
        if style.get("draw_pose",False) == True:
            pose=self.pose
            out.append((Point(pose=self.pose), style, self))
        return out

    def translate(self, position):
        self.local_pose.translate(position)
        return self

    def rotate(self, axis, angle, degrees=True):
        self.local_pose.rotate(axis, angle, degrees)
        return self


class Primitive(Part):

    def get_primitives(self, style=None):
        style=apply_style(self, style)
        if style.get("draw",True) == True:
            return [(self,style,self)]
        else:
            return []

class Point(Primitive):
    """A part that does not contain parts"""

class Text(Primitive):
    def __init__(self,text,**kwargs):
        super().__init__(**kwargs)
        self.text=text

class PolyLine(Primitive):
    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.local_points = [Point(pose=Pose(position=p)) for p in points]

    @property
    def points(self):
        return [p.clone(self) for p in self.local_points]

class Line(Primitive):
    def __init__(self, a, b, **kwargs):
        super().__init__(**kwargs)
        self.parts["a"] = Point(a)
        self.parts["b"] = Point(b)

class Rectangle(Primitive):
    def __init__(self, width, height, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
    
    @property
    def nw(self):
        return Point([-self.width/2, self.height/2,0],container=self)

    @property
    def ne(self):
        return Point([self.width/2, self.height/2,0],container=self)

    @property
    def sw(self):
        return Point([-self.width/2, -self.height/2,0],container=self)

    @property
    def se(self):
        return Point([self.width/2, -self.height/2,0],container=self)

    def get_primitives(self, style=None):
        style=apply_style(self, style)
        if style.get("draw",True) == True:
            return [
                (Line(self.nw, self.ne), style, self),
                (Line(self.ne, self.se), style, self),
                (Line(self.se, self.sw), style, self),
                (Line(self.sw, self.nw), style, self),
            ]
        else:
            return []



class Box(Part):
    def __init__(self, sizes, **kwargs):
        self.sizes = sizes

    @property
    def points(self):
        points = np.zeros((3, 8), dtype=float)
        l, h, p = self.sizes
        points[:, 0] = [l / 2, 0, -p / 2]
        points[:, 1] = [-l / 2, 0, -p / 2]
        points[:, 2] = [0, -h / 2, -p / 2]
        points[:, 3] = [0, -h / 2, -p / 2]
        points[:, 4] = [l / 2, 0, p / 2]
        points[:, 5] = [-l / 2, 0, p / 2]
        points[:, 6] = [0, -h / 2, p / 2]
        points[:, 7] = [0, -h / 2, p / 2]
        return self.pose.transform(points)

    @property
    def edges(self):
        return [(0, 1), (1, 2), (2, 3), (3, 4), (0, 1), (1, 2), (2, 3), (3, 4)]

    @property
    def lines(self):
        points = self.points()
        return [Line(points[a], points[b]) for a, b in self.edges]

    def get_primitives(self, style):
        style = apply_style(self, style)
        if style["draw"] == True:
            return [(l, self) for l in self.lines()]


class Arc(Part):
    pass


class Box(Part):
    pass


class Tube(Part):
    def __init__(self, sections, positions, angles, rolls):
        self.sections = sections
        self.positions = positions
        self.angles = angles
        self.rolls = rolls
