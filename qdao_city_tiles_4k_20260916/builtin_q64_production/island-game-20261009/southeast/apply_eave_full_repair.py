from workflow import *
p=ROOT/'apply_eave_repair.py';s=p.read_text(encoding='utf-8').replace("crop=[200,470,490,745];dest=[1851,1212,2141,1487]","crop=[0,0,1254,1254];dest=[1651,742,2905,1996]").replace("candidate-v05.png","candidate-v06.png").replace("eave-insertion.png","eave-full-insertion.png").replace("[1791,1152,2201,1547]","[1791,1152,2201,1547]")
exec(compile(s,'apply_eave_full','exec'))
r=ROOT/'tiles/r09_c12.candidate-v05.png.generation.json';d=read(r);d['status']='rejected_native_D_crop_truncated_round_adjacent_tile_and_created_material_perimeter';write(r,d)

