from xpoint import Point

ip=Point()
l_mbxf=6.27

mbxf_exit=ip.copy().moveto(z=-77.534+l_mbxf/2) # 3) moveto always inplace

mbxf_entry=ip.copy().arcby(dz=-7.61,angle=1.4e-3,axis='y')
rot_center=mbxf_exit.copy().moveby(z=1.2)

mbxf=Point(parts={'entry':mbxf_entry,'exit':mbxf_exit})

mbxf.set_origin(mbxf_entry.lookat(mbxf_exit,up='y'))
mbxf_rotated=mbxf.rotate(center=mbxf_exit,yrot=1.4e-3,keep_origin=True)

print(f"entry: {mbxf_rotated.body['entry'].position}")
print(f"exit: {mbxf_rotated.body['exit'].position}")





