import assembly

mb = assembly.Assembly(name='mb')
mbb = assembly.Assembly(name='mbb')
mbb.add('mb1',-3,mb)
mbb.add('mb2',3,mb)

line = assembly.Assembly('line')
line.add('mb1',3,mb)
line.add('mb2',5,mb)
line.add('mbb1',7,mbb)
line.add('mbb2',8,mbb)
line.add('start',0)
line.add('end',10)

mb.add('pipe',0)

line.parts['mb1'].parts['pipe']
line.parts['mbb1'].parts['mb1'].parts['pipe']

line['mb1']


line['mb1'].assembly['pipe'] #pipe of "mb"
line['mb1']['pipe'] # specific pipe of "mb1"
line['mb1/pipe']    # same as before specific pipe of "mb1"
line['mb1']['pipe'] # view of "mb1/pipe" in the frame of line
line['mb1']['pipe'] # view of "mb1/pipe" in the frame of world


line['mb1'].pipe.move(dx) # move pipe of all mb in the world frame
line.parts['mb1']['pipe'].move(dx) # move pipe of all mb in the line frame
line.parts['mb1'].parts['pipe'].move(dx) # move pipe of all mb in the mb frame

line.edit('mb1').pipe.move(dx) # deep copy mb into mb1 and move pipe in the world frame
line.edit('mb1')

line.parts['mb1']=Clone(line.parts['mb1'])
return line.parts['mb1']




