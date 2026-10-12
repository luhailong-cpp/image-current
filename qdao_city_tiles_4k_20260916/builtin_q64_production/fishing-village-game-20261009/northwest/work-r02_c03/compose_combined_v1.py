from repair_composite import *
D=W/'combined-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
patch(a,i,s,'r02_c03_rail_continuity_v01',103,top=(0,150),bottom=(1200,1253),left=(0,150),right=(1200,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_a_v01',104,top=(280,420),bottom=(1120,1253),left=(0,115),right=(1100,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_b_v01',105,top=(180,300),bottom=(1120,1253),left=(0,115),right=(1100,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_c_v01',106,top=(0,250),bottom=(1100,1253),left=(0,230),right=(1100,1253),out=D)
patch(a,i,s,'r02_c03_paving_join_d_v01',107,top=(450,500),bottom=(1100,1253),left=(0,230),right=(1100,1253),out=D)
patch(a,i,s,'r02_c03_blue_ridge_v01',108,top=(200,320),bottom=(1100,1253),left=(0,115),right=(1100,1253),out=D)
patch(a,i,s,'r02_r03_roof_phase_left_v01',101,left=(115,115),right=(1100,1253),mode='roof',out=D)
patch(a,i,s,'r02_r03_roof_phase_right_v01',102,left=(0,230),right=(1120,1253),mode='roof',out=D)
finish(D,a,i,s)

