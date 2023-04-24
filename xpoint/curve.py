import numpy as np

from .point import Point


class Curve(Point):
    def __init__(self, segments=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.segments = segments
