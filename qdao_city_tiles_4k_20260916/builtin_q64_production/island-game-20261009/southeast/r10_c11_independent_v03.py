"""Read-only independent source replay and exact final-candidate review crops."""
from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).parent;Q=R/'qa/r10_c11-independent-v03';Q.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
candidate=R/'tiles/r10_c11.candidate-v03.png';h=sha(candidate)
assert h=='cf5621335febecacf1a48b145a4eece1c8947a3b8e69740935e6cd89af4fcbf9'
im=Image.open(candidate).convert('RGB');assert im.size==(4096,4096)
audit=read(R/'qa/r10_c11-source-audit.json')
checks=[]
for item in audit['items']:
    p=Path(item['file']);rec=read(str(p)+'.generation.json')
    assert sha(p)==rec['sha256'] and Image.open(p).size==(1254,1254)
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert sha(rec['prompt'])==rec['promptSha256']
    assert sha(rec['sourceOutputPath'])==sha(p)
    for ref in rec['references']:assert sha(ref['file'])==ref['sha256']
    checks.append({'file':str(p),'sha256':sha(p),'native1254':True,'sourcePromptReferencesVerified':True,'actualModel':None,'actualQuality':None})
replay=Image.new('RGB',(4096,4096))
for e in audit['coreContributions']:
    assert sha(e['file'])==e['sha256']
    replay.paste(Image.open(e['file']).crop((115,115,1139,1139)),e['destinationBox'][:2])
for e in audit['overlays']:
    assert sha(e['file'])==e['sha256']
    replay.paste(Image.open(e['file']).crop(e['sourceCrop']),e['destination'])
assert replay.tobytes()==im.tobytes()
qaChecks=[]
for e in read(R/'qa/r10_c11-final-v03/index.json')['items']:
    assert sha(e['file'])==e['sha256']
    assert Image.open(e['file']).convert('RGB').tobytes()==im.crop(e['box']).tobytes()
    qaChecks.append(e['id'])
crops=[]
for kind in ['junction','pillar']:
    for e in read(R/'qa'/f'r10_c11-{kind}-repair-v01.json'):
        box=e['sourceBox'];name=Path(e['file']).name.replace('r10_c11-', '').replace('-repair-v01','')
        path=Q/name;crop=im.crop(box);crop.save(path)
        crops.append({'id':name[:-4],'file':str(path),'sha256':sha(path),'sourceBox':box,
                      'pixelIdenticalToPriorQACrop':crop.tobytes()==Image.open(e['file']).convert('RGB').tobytes()})
extra={'wall-whole':[1330,2120,2740,3590],'pillar-whole':[2480,2040,3380,3740],
       'pillar-base-detail':[2490,3310,2920,3600],'table-h11-detail':[884,280,1164,650]}
for name,box in extra.items():
    path=Q/(name+'.png');im.crop(box).save(path)
    crops.append({'id':name,'file':str(path),'sha256':sha(path),'sourceBox':box})
out={'candidate':str(candidate),'sha256':h,'dimensions':[4096,4096],'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'nativeEvidence':checks,'nativeEvidenceCount':len(checks),'full16Plus2ReplayIdentical':True,
     'all33IndexedQACropsExact':True,'qaCropIds':qaChecks,'independentCrops':crops,'formalAcceptedCount':0}
write(Q/'evidence.json',out)
print(json.dumps({'candidateHash':h,'nativeCount':len(checks),'exactSourceReplay':True,'all33QACropsExact':True,
                  'cropInheritance':[{k:e[k] for k in ['id','pixelIdenticalToPriorQACrop']} for e in crops if 'pixelIdenticalToPriorQACrop' in e]}))
