"""Mechanical coordinate guides only. Never exports final game pixels."""
from pathlib import Path
from PIL import Image
import hashlib, json, datetime

ZONE=Path(__file__).resolve().parent
ROOT=Path('D:/work/image')
CONTRACT=json.loads((ZONE.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

if __name__=='__main__':
    for folder in ['guides','native','records','qa','tiles']:
        (ZONE/folder).mkdir(exist_ok=True)
    refs=[{'path':CONTRACT[k],'sha256':sha(CONTRACT[k]),'role':role} for k,role in [
        ('layoutReference','only authoritative full-map composition'),
        ('detailStyleReference','material and close-up style only, NOT coordinate crop'),
        ('primaryStyleReference','primary approved Q Daoist painting style only; no UI/night copied')]]
    assert refs[0]['sha256']==CONTRACT['layoutSha256']
    assert refs[1]['sha256']==CONTRACT['detailSha256']
    source=Image.open(refs[0]['path'])
    assert source.size==(1254,1254)
    ratio=1254/57344
    patches=[]
    for row in range(4):
        for col in range(4):
            x,y=45056+col*1024,20480+row*1024
            box=[x-115,y-115,x+1024+115,y+1024+115]
            patches.append({'id':f'r06_c12_p{row+1}{col+1}','coreGlobalBox':[x,y,x+1024,y+1024],
                'nativeGlobalBox':box,'overviewBox':[v*ratio for v in box],
                'expectedSize':[1254,1254],'nativeCoreBox':[115,115,1139,1139]})
    manifest={'zone':'northeast','tile':'r06_c12','tileOrigin':[45056,20480],
        'tileCoreBox':[45056,20480,49152,24576],'references':refs,'patches':patches,
        'neighborOverlapPixels':230,'finalResizeAllowed':False}
    save(ZONE/'records/r06_c12.coordinates.json',manifest)
    first=patches[0]
    guide=ZONE/'guides/r06_c12_p11.layout-only.png'
    source.transform((1254,1254),Image.Transform.EXTENT,first['overviewBox'],Image.Resampling.BICUBIC).save(guide)
    save(str(guide)+'.derived.json',{'file':str(guide),'sha256':sha(guide),'purpose':'layout-only, enlarged coordinate guide, NOT game art',
        'derivedFrom':refs[0],'operation':'Pillow EXTENT bicubic; coordinate crop resampled to 1254 square for model guidance',
        'sourceBox':first['overviewBox'],'targetPixels':[1254,1254]})
    save(ZONE/'progress.json',{'zone':'northeast','status':'preparing_first_native_generation','updatedAtUtc':now(),
        'target4kCount':49,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,
        'formalAcceptedCount':0,'currentTile':'r06_c12','currentPatch':'p11',
        'nextStep':'Generate p11 from exact layout-only guide and three mandatory references using built-in image_gen.',
        'errors':[],'capacity5000Validated':False,'clientMappingValidated':False})
    print(json.dumps(first,ensure_ascii=False))
    print('All shared reference SHA256 verified; layout-only guide saved.')
