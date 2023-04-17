import numpy as np

from . import pose
from .part import PolyLine

class Line:
    def __init__(self,a,b):
        self.a = a
        self.b = b

    def to_polyline(self, nstep=2):
        """return a polyline with n points"""
        return PolyLine([self.a*(1-t)+self.b*t for t in np.linspace(0, 1., nstep)])


class Arc:
    def __init__(self,center=None,axis1=None,axis2=None,theta1=None,theta2=None):
        self.center = center
        self.axis1 = axis1
        self.axis2 = axis2
        self.theta1 = theta1
        self.theta2 = theta2

    @classmethod
    def from_start_tangent(cls,start,tangent,angle,length):
        """ create a arc from start and tangent"""
        return cls(start=start,tangent=tangent)





class Path:
    def __init__(self, start=None, end=None, tangent=None, tangent_end=None):
        self.start = start
        self.end = end
        self.tangent = tangent
        self.tangent_end = tangent_end
        self.segments = []
        self.specs=[]


    def move(self,start=None,tangent=None):
        """change origin to point"""
        if start is not None:
            self.start = start
        if tangent is not None:
            self.tangent=tangent
        self.specs.append(("move",{"start":start,"tangent":tangent}))


    def rotate(self,point=None, tangent=None, alpha=0, beta=0, gamma=0):
        """change tangent last point"""
        if tangent is not None:
            self.tangent_end = tangent
        if point is not None:
            self.tangent_end=pose.direction(self.end,point)
        if alpha!=0 or beta!=0 or gamma!=0:
            self.tangent_end=pose.Rotation.from_euler("xyz", alpha, beta, gamma)*self.tangent_end
        self.specs.append(("rotate",{"point":point,"tangent":tangent,"alpha":alpha,"beta":beta,"gamma":gamma}))

    def line(self,point,ds):
        """ add line to point"""
        self.end=point
        self.tangent=pose.direction(self.start,point)
        self.segments.append(Line(self.start,point))
        self.specs.append(("line",{"point":point,"ds":ds}))

    def arc(self,ds=None,angle=0,tilt=0,radius=None,altradius=None,point=None,at=None):
        """ add an elliptical arc tangent to path"""

    def limit_line(self,a,b):
        """ limit previous segment to line"""

    def to_segments(self):
        """ return list of segments"""

    def to_polyline(self,nstep,dsstep,accuracy):
        """ limit previous segment to line"""







