from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent
base=Image.open(D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png').convert('RGB')
raw=Image.open(D/'r12c08-wall-rock-conditioned-v5-raw.png').convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports=[]
for right in [850,950,1050]:
    rect=[350,280,right,830]
    stem=f'r12c08-wall-rock-v5-cross-x{right}'
    adopt=base.copy();adopt.paste(raw.crop(rect),rect[:2])
    path=D/(stem+'-provisional-guide1254.png'); assert not path.exists();adopt.save(path)
    strips={'left':[286,280,414,830],'right':[right-64,280,right+64,830],
            'top':[350,216,right,344],'bottom':[350,766,right,894]}
    es=[]
    for name,box in strips.items():
        p=D/(stem+'-'+name+'-native.png');adopt.crop(box).save(p)
        es.append({'edge':name,'file':str(p),'sha256':sha(p),'guideBox':box})
    reports.append({'rectGuide':rect,'worldBox':[rect[0]+32150,rect[1]+45250,rect[2]+32150,rect[3]+45250],
                    'preview':str(path),'previewSha256':sha(path),'evidence':es,
                    'status':'provisional_cross_seam_probe_unreviewed','formalAccepted':False,'selected':False})
(D/'v5-cross-adoption-probes.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'probes':len(reports),'report':str(D/'v5-cross-adoption-probes.json')}))
