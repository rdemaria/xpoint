from whereisit import Part, Pose

point = Part(name='point')

box=Part(name='Box')
box.add('ne',point, Pose(1,0,0))
box.add('nw',point, Pose(0,1,0))
box.add('sw',point, Pose(-1,0,0))
box.add('se',point, Pose(0,-1,0))

box['ne']

boxes=Part(name='Boxes')
boxes.add('box1',box, Pose(1,0,0))
boxes.add('box2',box, Pose(0,1,0))
boxes.add('box3',box, Pose(-1,0,0))
boxes.add('box4',box, Pose(0,-1,0))

boxes.box1.ne.edit()
"""
boxes.parts['box1'] is box? False

"""

Part(template=point,
    pose=boxes.transform(boxes.parts['box1'].pose).transform(box.part['ne'].pose))


mbb = Part('mbb')
mbb.add('mb1',mb,-3)
mbb.parts['mb2']=mb.clone(-2,parent=mbb)

line = Part('line')
line.add('ip1')
line.add('mb1')
line.add('mb1',mb, at=4,from_='ip1')
line.add('mb2',5,mb)
line.add('mbb1',7,mbb)
line.add('mbb2',8,mbb)
line.add('start',0)
line.add('end',10)

mb.add('pipe',0)

line.parts['mb1'] is mb
line.parts['mb2'] is mb
line.parts['mbb1'] is mbb
line.parts['mbb2'] is mbb

line['mb1'] # specific mb in line
line['mb2'] # specific mb in line
line['mbb1']['mb1'] # specific mb in line/mbb1
line['mbb2']['mb2'] # specific mb in line/mbb2

line.parts['mb1'].parts['pipe'] #pipe of "mb"
line['mb1'].parts['pipe'] # pipe of "line/mb1"
line.parts['mb1']['pipe'] # pipe of "mbb/m1
line['mb1']['pipe']

dx=2
line['mb1'].pipe.move(dx) # move pipe of all mb in the world frame
line.parts['mb1']['pipe'].move(dx) # move pipe of all mb in the line frame
line.parts['mb1'].parts['pipe'].move(dx) # move pipe of all mb in the mb frame

line.edit('mb1').pipe.move(dx) # deep copy mb into mb1 and move pipe in the world frame
line.edit('mb1')

line.parts['mb1']=Clone(line.parts['mb1'])





