import whereisit as wh

l1=wh.Line([1,2],[4,5],name='line1')
l2=wh.PolyLine([[2,1],[5,4],[1,-3]],name='line2')
p1=wh.Point([1,3],name='point1')
r1=wh.Rectangle(2,3,name='rectangle1')

canvas=wh.CanvasMPL2D()
canvas.add(l1, l2, p1, r1)
canvas.draw({'#line1': {'color': 'red'}})
