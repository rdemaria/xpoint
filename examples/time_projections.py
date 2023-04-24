import numpy as np
import timeit

nd=3
npt=100


def doit(nd,npt):
    v1=np.random.rand(nd)
    vv=np.random.rand(nd,npt)
    vt=np.random.rand(npt,nd)
    m=np.random.rand(nd,nd)
    for cmd in ["v1[[1,2]]","(m@v1)[:2]","(m@vv)[:,:2]","(m@vt.T)[:,:2]"]:
        print(cmd,timeit.timeit(cmd,number=10000,globals=locals()))

doit(3,1)
doit(3,100)
doit(3,1000)

