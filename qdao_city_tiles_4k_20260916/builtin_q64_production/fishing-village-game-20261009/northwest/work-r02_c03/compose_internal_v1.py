from repair_composite import *
D=W/'internal-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
patch(a,i,s,'r02_c03_rail_continuity_v01',103,top=(0,150),bottom=(1150,1253),left=(0,150),right=(1190,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_a_v01',104,top=(280,420),bottom=(880,1050),left=(0,115),right=(1140,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_b_v01',105,top=(200,360),bottom=(880,1050),left=(0,115),right=(1140,1253),out=D)
finish(D,a,i,s)

