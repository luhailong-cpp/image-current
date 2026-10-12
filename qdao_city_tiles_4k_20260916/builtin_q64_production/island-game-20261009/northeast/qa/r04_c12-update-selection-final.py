from native_work import *
p=ZONE/'selection-r04_c12.json';d=read(p);d['cores'][3][3]='r04_c12_p04_04_v3';d['overlays']=['r04_c12_cross_01_02_jar_paint_repair_v2','r04_c12_cross_01_03_jar_repair'];d['pendingIssues'][1]['status']='resolved_by_paired_r04_c12_cross_01_02_jar_paint_repair_v2';write(p,d)

