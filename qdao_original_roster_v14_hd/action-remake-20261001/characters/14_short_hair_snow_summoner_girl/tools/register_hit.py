from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
rows=[]
for d,xs in {'E':[595,637,683,638,579,585],'W':[497,486,448,482,486,504]}.items():
    for i,x in enumerate(xs,1):
        p=R/'hit'/d/f'{i:02d}.png'
        rows.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'srcRoot':[x,960],'basis':'人工查看带100px横坐标的靴/踝窗口；x取双脚解剖支撑中心，y全序列统一960。保留后仰/下蹲，没有逐帧最低像素贴地。','confidence':'manual approx +/-8px; final dynamic review required'})
r={'schemaVersion':1,'coordinateSpace':'whole-canvas normalized 1024px source before global affine','globalScale':.8,'targetRoot':[512,942],'applyTransform':False,'method':'manual anatomical support-root registration; one global scale for all actions','frames':rows}
(R/'hit'/'registration.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
