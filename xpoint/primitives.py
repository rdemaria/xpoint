import numpy as np

from .point import Point, Rotation

class Line(Point):
    def __init__(self, start, end, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start=np.array(start)
        self._end=np.array(end)
        self._update()

    def _update(self):
        rot=Rotation.from_vectors(self._end-self._start, np.array([0,0,1]))
        self.parts['start']=Point(self._start,rotation=rot)
        self.parts['end']=Point(self._end,rotation=rot)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start=value
        self._update()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end=value
        self._update()

    def __repr__(self):
        return f"Line({self.start}, {self.end}, location={self.location}):"


class PolyLine(Point):
    def __init__(self, points, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = points

    def __getitem__(self, idx):
        return Point(self.matrix@self.points[:, idx])

    @property
    def positions(self):
        return self.matrix@self.points

    def __len__(self):
        return len(self.points)

class Text(Point):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text


    def __str__(self):
        return f"Text({self.text}, {self.position})"

    def __repr__(self):
        return f"Text({self.text}, {self.position})"