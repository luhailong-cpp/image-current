from native_work import *
p=ZONE/'selection-r04_c12.json';d=read(p);d['cores'][2][3]='r04_c12_p03_04_v5';d['cores'][3]=['r04_c12_p04_01_v2','r04_c12_p04_02_v2','r04_c12_p04_03',None];d['overlays']=['r04_c12_cross_01_03_jar_repair'];d['pendingIssues'][0]['status']='resolved_by_r04_c12_cross_01_03_jar_repair';write(p,d)
p=ZONE/'qa/r04_c12_cross_01_03_jar_repair.overlay.json';d=read(p);d['independentReview']='passed root and south_tile center and all four1:1 edge crops';write(p,d)

