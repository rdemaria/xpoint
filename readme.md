XPoint
===========================

Intro
----------------------
The library manages spatial entities:

Point,
Path, Line, Dimension, Arrow
Mesh, Box, Pipe

API:
ent.transform(point)

Point
-----------------------

A `Point` is a position in space with an associated orthogonal reference frame
("local frame").  A point can contain a `.body` which is dictionary of entities
expressed in the local frame.


p=Point()

p=Point(1,2,3)
p=Point(position=[1,2,3],orientation=[30,50,60],scaling=[.5,.5,.5])
p=Point(position=[1,2,3],orientation=[30,60,50])
p=Point(position=[1,2],rotation=[30]) # 2D

a+b = a.move(b,inplace=False,local=False) 
a*b = a.rotate(b,inplace=False,local=False)
a@b = a.transform(b,inplace=False,local=False)
a%b = a.scale(b,inplace=False,local=False)

a.move(point,angle=None,tilt=None,local=True,inplace=True) # move the point by b
a.rotate(rotation,center=c,inplace=False,local=False) # rotate the point about center by b
a.lookat(point,axis='z',inplace=False,local=False) # change the orientation such that axis points to b



moveto  (stra)
moveby
translate 
scaleby
scaleto
rotateby
rotateto



API:

```
position=,rotation=,scaling=,label=,
matrix=,
x=,y=,z=,rotx,roty,rotz=,scx=,scy=,scz=



p=Point()

p.moveto(position=,point=,x=,y=,z=)
p.moveby(positino=,point=,x=,y=,z=,angle=,tilt=)
p.arcto(position=None,radius=,tilt=)
p.splineto() ....
p.alignto(point)


p.body={'n':Point([0,0,5]), 's':Point([0,0,-5])}
p['n'] # transformed Point

p.reframe() #change body and point while keeping transformed positions
```

Path
------------------------

A `Path` is a list of segments. Same API of points.

API:
```
pa=Path()
pa.moveto()
pa.arcto()

pa.at(s) # get a point
pa@s # get a point
pa.intersection(other) # get intersections
pa * other # get intersections
```


Beamline
------------------------------

Beamline specifies a path

API:
```
lhc=BeamLine(length=)

lhc.add(label,at=,from=,length=,angle=,tilt=,body=)
lhc.add(label,at=,from=,length='body',angle='body',tilt=,body=)
lhc.path.at
lhc[label] get point
lhc.center(label,point) # Point(matrix=lhc[label].matrix.inv(),body=lhc)
```



Spatial Primitives
--------------------------------------------------------------------------
Spation primitives are special parts.
Spatial primitives describe object of space like regions, fields etcc
Spatial primitives can be rigidily moved.
Spatial primitives can be transformed into drawing primitives in 2D or 3D Spaces


Backends
------------------------------------------------------------------------

The backend plot and interact with drawing primitives.
The primitives for the matplotlib backend is Polyline, Text, Point.
The primitive contains specs, the owner, style.

The draw command resolve the style, add a primitive on the figure, create actions.
The delete command remove a primitive from the plot.


Style
-------------------------------------------------------------------------
Order of specificity from less specific:
-  Backend.style
-  Canvas.style
-  Primitive.style
-  User passed style

selector `.<class_name>` , `#label`


Canvas:
----------------------------

A canvas defines how spatial primitives in a 3D euclidean space transform in drawing primitives.
Geometrical primitives are Polylines, Point, Text, Meshes of some sort [perhaps more???]
There are Canvas2D which can use different projections and canvas3D that defines only scaling and axis.


Todo
-----------------------------

- Consider Line taking poses instead of points
- Implement PlotPoint, PlotPolyline
- Path class to generate smooth path: needs for beam line and aperture cross sections.
- Test Canvas3D
- Improve pose library for user friendly movements
- Test Projection and Canvas2d
- Implement BackendVTK3D


