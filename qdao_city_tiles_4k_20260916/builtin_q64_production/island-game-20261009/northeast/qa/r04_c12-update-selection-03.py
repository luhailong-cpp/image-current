from native_work import *
p=ZONE/'selection-r04_c12.json';d=read(p);d['cores'][1]=['r04_c12_p02_01','r04_c12_p02_02_v2','r04_c12_p02_03','r04_c12_p02_04_v3'];d['cores'][2]=['r04_c12_p03_01','r04_c12_p03_02','r04_c12_p03_03',None];write(p,d)

