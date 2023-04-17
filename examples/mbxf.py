from xpoint import Point

ip=Point()

mbxf_exit=ip.translate(z=-76)
mbxf_entry=ip.arcby(z=-7.61,angle=1.4e-3,axis='y')
rot_center=mbxf_exit.translate(z=1.2)

mbxf=Point(body={'entry':mbxf_entry,'exit':mbxf_exit})

mbxf.set_origin(mbxf_entry.lookat(mbxf_exit,up='y'))
mbxf_rotated=mbxf.rotate(center=mbxf_exit,yrot=1.4e-3,keep_origin=True)

print(f"entry: {mbxf_rotated.body['entry'].position}")
print(f"exit: {mbxf_rotated.body['exit'].position}")





