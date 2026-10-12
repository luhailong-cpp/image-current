from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
S='r12c08-wall-rock-rail-coordinated-v1'
prev=json.loads((D/'r12c08-wall-rock-conditioned-v8.border-adoption-check.json').read_text(encoding='utf-8'))
railpath=BASE/'r12_c08/repairs/r12c08-rail-joint-v4-edge-color.png';rail=Image.open(railpath).convert('RGB')
railframe=[32150,44941,33404,46195];railbox=[32470,45066,32800,45491]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
patches=[]
for rec in prev['patches']:
    im=Image.open(rec['file']).convert('RGB');before=np.asarray(im).copy();nb=rec['nativeFrameWorld']
    inter=[max(railbox[0],nb[0]),max(railbox[1],nb[1]),min(railbox[2],nb[2]),min(railbox[3],nb[3])]
    railuse=None
    if inter[0]<inter[2] and inter[1]<inter[3]:
        crop=[inter[0]-railframe[0],inter[1]-railframe[1],inter[2]-railframe[0],inter[3]-railframe[1]]
        dest=[inter[0]-nb[0],inter[1]-nb[1]];part=rail.crop(crop);im.paste(part,dest)
        assert im.crop((dest[0],dest[1],dest[0]+part.width,dest[1]+part.height)).tobytes()==part.tobytes()
        allowed=np.zeros((1254,1254),bool);allowed[dest[1]:dest[1]+part.height,dest[0]:dest[0]+part.width]=True
        assert np.array_equal(before[~allowed],np.asarray(im)[~allowed])
        railuse={'worldBox':inter,'sourceCrop':crop,'destinationNative':dest,'nativeBox':[dest[0],dest[1],dest[0]+part.width,dest[1]+part.height],
                 'pixelReplayExact':True,'changedPixels':int(np.any(before!=np.asarray(im),axis=2).sum())}
    else:assert im.tobytes()==Image.open(rec['file']).convert('RGB').tobytes()
    path=D/(S+'-'+rec['tile']+'-'+rec['patch']+'-provisional-native1254.png');assert not path.exists();im.save(path)
    patches.append({'tile':rec['tile'],'patch':rec['patch'],'file':str(path),'sha256':sha(path),'nativeFrameWorld':nb,
                    'source':rec['file'],'sourceSha256':sha(rec['file']),'wallRockCoreAdoption':rec['coreAdoptionIntersection'],
                    'railReplay':railuse,'formalAccepted':False,'selected':False})
record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'geometry_candidate_material_finish_pending',
        'wallRockWorldBox':[32500,45530,33100,46080],'railWorldBox':railbox,
        'railSource':str(railpath),'railSourceSha256':sha(railpath),'railSourceFrameWorld':railframe,
        'patches':patches,'coreChanges':['r12_c08/p14','r12_c09/p11'],'haloOnlyChanges':['r12_c08/p24','r12_c09/p21'],
        'operation':'Exact approved rail source crops pasted into new wall-rock provisional patches only. No resampling/color operation/blend/warp/synthetic geometry.',
        'canonicalSelectionsModified':False,'zoneProgressModified':False,'historicalAuditsModified':False,'formalAccepted':False,'selected':False,
        'note':'This candidate also replays the locally approved32px rail extension into c09 core. Owner must coordinate both p14 and p11 before final canonical adoption. Visible tone/texture transitions still require material review.'}
(D/(S+'.patch-manifest.json')).write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(D/(S+'.patch-manifest.json')),'patches':[{'tile':r['tile'],'patch':r['patch'],'railPixelsChanged':None if r['railReplay'] is None else r['railReplay']['changedPixels']} for r in patches]}))
