from xpoint import Point

# Create a point at the origin
p=Point()

# Create a point at (1,2,0)
p=Point(1,2)

# Create a point at (1,2,3)
p=Point(1,2,3)

# Create a point at (1,2,3)
p=Point([1,2,3])

# Create a point with the same position as p
p=Point(p)

# Create a point with the same position as p
p=Point(p.matrix)

# Create a point with the same position as p
p=Point(p)


Point((1,2,3), rx=0, ry=0, rz=0)
Point(p)
Point(p._matrix)

