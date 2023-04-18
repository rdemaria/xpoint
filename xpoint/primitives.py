class Line(Point):
    def __init__(self, start, end, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = {'start': start, 'end': end}

    @property
    def start(self):
        return self.body['start']

    @start.setter
    def start(self, value):
        self.body['start'] = value

    @property
    def end(self):
        return self.body['end']

    @end.setter
    def end(self, value):
        self.body['end'] = value


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
