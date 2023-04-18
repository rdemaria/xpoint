The library manages spatial entities: region of space with given properties.

An entity is defined by:
  - pose: the position and rotation of the entity, the pose also defines a local reference system that is used to define subparts
  - parts: the sub parts which the entity is made of, defined in the local reference frame
  - owner: the entity which this entity is part of if, any
  - template: provide data for the entity when not present in the entity



Parts
-------------------------------------------------------------------------
Parts represents physical objects and have a pose (position and orientation)
Parts can have sub parts stored `.parts` dictionary.
Parts can have sub parts stored `.name`.
A sub part can be accessed using `[]`. This returns a `clone` of the part in the global reference frame.
Parts can have a `.template` that provides missing data for the parts.
.clone(pos) create

Example:

a=Part("A")
b=Part("B")
c=Part("C")
c.add('a1',a,at=1) #equiv c.parts['a1']=a.clone(1)
c.add('a2',a,at=2) #equiv c.parts['a2']=a.clone(2)
c.add('b',a,at=3) #equiv c.parts['b']=b.clone(3)

d=Part('D')
d.add('cl',c,-3)
d.add('cr',c,+3)

d.cr.a1.owner==d
d.cr.a1.path==d.cr
c.a1.owner==c



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



Alternatives
------------------------------

Using the pair Part(name,pose,assembly), Assembly(parts) solves the problems of sharing assemblies, but does not allow to add specific position behaviour to assemblies. Conversely the Entity(pose,parts,template) allows this. The template scheme is however not suitable for C++ environments for which it is not easy to mask array access. Each accessor should have be implemented as `if_xxx_defined get_x else template_get_x`.

On the other hand the use of __getattr__ is extremely delicate...


