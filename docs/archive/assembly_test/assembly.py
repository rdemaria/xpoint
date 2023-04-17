class Part:
    def __init__(self, name, pose, assembly=None):
        self.name = name
        self.pose = pose
        self.assembly = assembly

    @property
    def parts(self):
        return self.assembly.parts

    def __getitem__(self,k):
        return self.assembly[k]

    def __repr__(self):
        return f"<Part {self.name} {self.pose} {self.assembly}>"


class Assembly:
    def __init__(self, name, *parts, **kwargs):
        self.name = name
        self.parts = {p.name: p for p in parts}
        self.__dict__.update(kwargs)

    def add(self, name, pose, assembly=None):
        self.parts[name] = Part(name, pose, assembly)

    def __repr__(self):
        return f"<{self.name}>"

    def __getitem__(self,k):
        part=self.parts[k]
        return View(self,part)

class View:
    def __init__(self,container,part):
        self.container = container
        self.part = part
        self.name = f"{self.container.name}/{self.part.name}"
        self.assembly=part.assembly

    @property
    def pose(self):
        if hasattr(container,'pose'):
           return container.pose+part.pose # + is compose...

    def clone(self):
        if isinstance(self.container,View):
            container=self.container.clone()
        else:
            container=self.container
        if self.part.assembly is not None:
            assembly=Clone(self.part.assembly)
        else:
            assembly=None
        container.add(self.part.name,self.part.pose,assembly)
        return container

    def __getitem__(self,k):
        part=self.part.assembly.parts[k]
        return View(self,part)

    def __repr__(self):
        return f"<View {self.name} {self.pose} {self.assembly}>"

class Clone:
    def __init__(self, assembly):
        self.orig = assembly

    def __repr__(self):
        if self.orig is None:
            return 'None'
        else:
            return f"<Clone {self.orig.name}>"

    def __getattr__(self,k):
        return getattr(self.orig,k)
