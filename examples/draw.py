from xpoint import Point


p=Point(name='test')
canvas=p.draw2d()
p1=Point(name='p1').moveto(x=1,y=1)
canvas.add(p1)
canvas.draw()