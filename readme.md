# XPoint

## Intro

The library manages geometrical entities: `Point`, `Line`, ...

A `Point` defines location of space and a local reference frame.
A `Point` can have parts defined in the local reference frame.

All entities derive from Point and can be moved, rotated, scaled.
Some entities, called primitives, can be drawn by Canvas objects with a given style.
Entities have a `draw()` method that emit primitives to be drawn according to a style.


## Point

A `Point` is a location in space with an associated set of orthogonal axis and scaling that defines the local reference frame.  A point contains a `.parts` dictionary of entities expressed in the local frame.

### Initialization

```
p=Point()
p=Point(point)
p=Point(matrix4x5)
p=Point(location, rotation, scaling)
p=Point(x,y,z,rx,ry,rz,sx,sy,sx)
```


### Inspection

```
(p.x, p.y, p.z) == p.loc
(p.rx, p.ry, p.rz) == p.rotation
p.scx, p.scy, p.scz = p.scaling
np.r_[p.dx, p.dy. p.dz] == p.rotm
?np.r_[p.du, p.dv. p.dw] == p.rotation_matrix
p.rotation_axis_angle
p.rotation_quat
p.mat
```

### Copy

```
p.new
p.clone
p.copy()
```

### Translation
Methods to create or change an entity to a new a location without changing the orientation:
- using scalar coordinates, iterables, or existing point
- location specified in global or local frame
- create a new object or modify in place


```python
# in place movement
p.moveby(delta:Point) # move to point
p.moveby([dx,dy,dz]) # move using vector
p.moveby(dx=,dy=,dz=) # move using coordinates
p.moveby(du=,dv=,dw=) # move using localcoordinates
p+=delta
# create new object
p+delta # global coordinates
p+p.rot@delta #local coordinates



```


### Rotation

```python
# new point
p.rotate(rotation)
p.rotate_euler(rx,ry,rz,degree,seq)
p.rotate_axis_angle(axis,angle,degree)
p.rotate_quat(quaternion)
p*point
p*matrix

# in place
p.rotation=matrix
p.rotation*=matrix
p.rotation_euler=[rx,ry,rz]
p.rotation_euler+=[rx,ry,rz]
p.rotation_axis_angle=[ax,ay,az,angle]
#p.rotation_axis_angle+=[ax,ay,az,angle] does not make sense
p.rotation_quat(quaternion)
```

### Scaling
```python
# new point
p.scale(scaling, local=True, inplace)
p%=scaling
```

### Transformation
```python
p.transform(point)
p.transform(matrix)
p@point

```

### Acc transformations and curves
```python
p.arcby(du,dv,dw,angle,axis,tilt)
p.arcto(x,y,z,bigflag)
p.arcradius(radius,angle)
```


## Curve
Curve specify a path in space from a list of segments




## Beamline
Beamline specifies a path relative segments

API:
```
lhc=BeamLine(length=)

lhc.add(label,at=,from=,length=,angle=,tilt=,body=)
lhc.add(label,at=,from=,length='body',angle='body',tilt=,body=)
lhc.path.at
lhc[label] get point
lhc.center(label,point) # Point(matrix=lhc[label].matrix.inv(),body=lhc)
```

## Primitives and Canvas

Canvas can draw points and other entities

Primitives are special entities that can be drawn by a canvas 


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

A canvas contains parts to be drawns.

Artists[part]=set of artists
For each parts in the model frame
    primitives=part.get_primitives(view,frame)
    for primitive in part.get_primitives(view,frame)
        get_artists(primitives)


canvas draw:
   for part in self.parts:
      primitives=part.get_primitives(transformation,style)  # 3d view frame
      draw_primitive 

transform in the view space, project in x,y


A canvas defines how spatial primitives in a 3D euclidean space transform in drawing primitives.
Geometrical primitives are Polylines, Point, Text, Meshes
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


