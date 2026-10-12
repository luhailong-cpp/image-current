from pathlib import Path
from PIL import Image
import json, hashlib, datetime, numpy as np
OUT=Path(__file__).resolve().parent
BASE=OUT.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
entries=[]
previous={}
rp=OUT/'partial-qa.json'
if rp.exists():
    previous={e['segment']:e for e in json.loads(rp.read_text(encoding='utf-8'))['segments']}
for tile,north,ver in [('r05_c10','r04_c10',2),('r05_c11','r04_c11',3)]:
    npth=BASE/north/'candidate'/f'{north}-4096-candidate-v{ver}.png'
    n=Image.open(npth).convert('RGB')
    for c in range(1,5):
        name=f'{tile}-north-c{c}'
        s=BASE/tile/'records'/f'p1{c}.selection.json'
        if not s.exists():
            entries.append({'segment':name,'status':'waiting_for_selected_native','formalAccepted':False})
            continue
        sel=json.loads(s.read_text(encoding='utf-8-sig')); source=Path(sel['file']); srcsha=sha(source)
        native=Image.open(source).convert('RGB'); assert native.size==(1254,1254)
        core=native.crop((115,115,1139,1139))
        im=Image.new('RGB',(1024,256)); im.paste(n.crop(((c-1)*1024,3968,c*1024,4096)),(0,0)); im.paste(core.crop((0,0,1024,128)),(0,128))
        path=OUT/(name+'-native.png'); im.save(path)
        wide=Image.new('RGB',(1024,512)); wide.paste(n.crop(((c-1)*1024,3840,c*1024,4096)),(0,0)); wide.paste(core.crop((0,0,1024,256)),(0,256)); wide.save(OUT/(name+'-wide-native.png'))
        ar=np.asarray(im).astype(float); d=np.abs(np.diff(ar,axis=0))
        old=previous.get(name,{}); stillsame=old.get('southSha256')==srcsha
        entries.append({'segment':name,'status':old.get('status','awaiting_visual_review') if stillsame else 'awaiting_visual_review','formalAccepted':False,'northCandidate':str(npth),'northSha256':sha(npth),'southNative':str(source),'southSha256':srcsha,'coreCrop':[115,115,1139,1139],'seamFile':str(path),'dimensions':[1024,256],'boundaryMeanAbsChannelDelta':round(float(d[127].mean()),3),'nearbyMeanDelta':round(float(d[112:144].mean()),3),'visualFindings':old.get('visualFindings') if stillsame else None})
report={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'scope':'8 native north-boundary segments only; no candidate mutation','readySegments':sum(e['status']!='waiting_for_selected_native' for e in entries),'requiredSegments':8,'priorityRange':{'tile':'r05_c11','northLocalXInclusive':[958,1591],'reason':'r04_c11 v3 repaired net reaches final bottom edge'},'segments':entries}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'segment':e['segment'],'status':e['status'],'delta':e.get('boundaryMeanAbsChannelDelta')} for e in entries],ensure_ascii=False))
