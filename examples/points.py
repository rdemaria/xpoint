from xpoint import Point

# Create a point at the origin
p=Point()

# Create a point at (1,2,3)
p=Point((1,2,3))

# Create a point at (1,2,3) with rotation (alpha,beta,gamma)=(1,2,3)
p=Point((1,2,3),(1,2,3))

# Create a point at (1,2,3) with rotation (alpha,beta,gamma)=(1,2,3) in degrees
p=Point((1,2,3),(1,2,3),degrees=True)

# Create a point at (1,2,3) with rotation (alpha,beta,gamma)=(1,2,3) in radians
p=Point((1,2,3),(1,2,3),degrees=False)



Point(x=0, y=0, z=0, rotx=0, roty=0, rotz=0)
Point(p)
Point([1,2,3])
Point(1,2,3)
Point(p._matrix)

