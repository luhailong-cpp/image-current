"""Owned r05_c13 proposed workflow. Native art only uses integer crop/paste."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import north_extension as north

Z=Path(__file__).resolve().parent
B=north.base
T='r05_c13'
SEL=Z/'records'/'r05_c13.selection-sol-proposed-20261012.json'

def write(p,d):
    Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def initial():
    assert not SEL.exists()
    d=json.loads((Z/'records'/f'{T}.working-selection.json').read_text(encoding='utf-8'))
    d[f'{T}_p32']='r05_c13_p32-v3.png'
    write(SEL,{'tile':T,'patches':d,'status':'proposed_partial_native_candidates','formalAccepted':False})
def prepare(p,v,target=None):
    north.configure(T);co=B.coords(p);r,c=int(p[-2]),int(p[-1])
    d=json.loads(SEL.read_text())['patches'];sources=[]
    im=Image.open(Z/'native'/target).convert('RGB') if target else Image.open(B.C['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
    assert im.size==(1254,1254)
    sides=[]
    if c>1 and f'{T}_p{r}{c-1}' in d:sides.append((Z/'native'/d[f'{T}_p{r}{c-1}'],'left',[1024,0,1254,1254],[0,0]))
    if c<4 and f'{T}_p{r}{c+1}' in d:sides.append((Z/'native'/d[f'{T}_p{r}{c+1}'],'right',[0,0,230,1254],[1024,0]))
    if c==4:
        east=json.loads((Z/'records'/'r05_c14.working-selection.json').read_text())
        if f'r05_c14_p{r}1' in east:sides.append((Z/'native'/east[f'r05_c14_p{r}1'],'right',[0,0,230,1254],[1024,0]))
    if r<4 and f'{T}_p{r+1}{c}' in d:sides.append((Z/'native'/d[f'{T}_p{r+1}{c}'],'bottom',[0,0,1254,230],[0,1024]))
    if r==4:
        ds=json.loads((Z/'records'/'r06_c13.selection-proposed-v1.json').read_text(encoding='utf-8-sig'))['patches'][f'r06_c13_p1{c}']
        path=Path(ds if isinstance(ds,str) else ds['path']);path=path if path.is_absolute() else Z/path
        if isinstance(ds,dict):assert B.sha(path)==ds['sha256']
        sides.append((path,'bottom',[0,0,1254,230],[0,1024]))
    for path,side,box,xy in sides:
        a=Image.open(path).convert('RGB');assert a.size==(1254,1254);im.paste(a.crop(box),xy)
        rr=B.ref(path,'exact_native_'+side+'_230px');rr.update(cropBox=box,pasteAt=xy);sources.append(rr)
    guide=Z/'guides'/f'{p}-{v}.sol-native-edge-layout.png'
    if guide.exists():assert Image.open(guide).convert('RGB').tobytes()==im.tobytes()
    else:im.save(guide)
    refs=[B.ref(B.C['layoutReference'],'full-map layout only'),B.ref(B.C['detailStyleReference'],'independent materials only'),B.ref(B.C['primaryStyleReference'],'primary Q style only'),B.ref(guide,'local native target or layout geometry with exact edge anchors')]
    if target:refs.append(B.ref(Z/'native'/target,'native edit target original'))
    for path,side,box,xy in sides:
        if all(q['path']!=str(path).replace('\\','/') for q in refs):refs.append(B.ref(path,'real native '+side+' neighbor'))
    plan={'patchId':p,'createdAtUtc':B.now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'configSnapshot':json.loads(B.CONFIG.read_text(encoding='utf-8-sig')) if B.CONFIG.exists() else None,'configSource':B.ref(B.CONFIG,'configured preference only; not actual selector') if B.CONFIG.exists() else {'path':str(B.CONFIG),'available':False},'intent':'native repair' if target else 'native redraw using layout-only geometry'}
    pp=Z/'records'/f'{p}-{v}.plan.json';assert not pp.exists();write(pp,plan)
    write(str(guide)+'.derived.json',{'purpose':'generation input geometry only; never final art','coordinates':co,'sources':sources,'target':B.ref(Z/'native'/target,'original native') if target else B.ref(B.C['layoutReference'],'layout only'),'operations':'integer opaque native strips; overview EXTENT bicubic only if no target; bottom owns corners'})
    print(json.dumps(plan,ensure_ascii=False))
def select(p,v,note):
    n=Z/'native'/f'{p}-{v}.png';assert Image.open(n).size==(1254,1254)
    rp=Z/'qa'/f'{p}-{v}.sol-review.json';assert not rp.exists()
    seams=list((Z/'qa').glob(f'{p}-{v}-exact_native_*.png'))
    write(rp,{'reviewer':'central_sol','createdAtUtc':B.now(),'native':B.ref(n,'native candidate'),'nativeSize':[1254,1254],'fullNativeViewed':True,'nativeSeamsViewed':[B.ref(s,'native1:1 seam') for s in seams],'verdict':'provisional_geometry_pass','note':note,'formalAccepted':False})
    d=json.loads(SEL.read_text());d['patches'][p]=n.name;d['updatedAtUtc']=B.now();write(SEL,d)
    print(json.dumps({'selectedProposed':n.name,'review':str(rp)}))

def assemble(v):
    d=json.loads(SEL.read_text())['patches']
    expected={f'{T}_p{r}{c}' for r in range(1,5) for c in range(1,5)}
    assert set(d)==expected
    out=Z/'tiles'/f'{T}.candidate-{v}.png'
    assert not out.exists()
    im=Image.new('RGB',(4096,4096));contrib=[]
    origin=(49152,16384)
    for r in range(1,5):
        for c in range(1,5):
            p=f'{T}_p{r}{c}';n=Z/'native'/d[p]
            a=Image.open(n).convert('RGB');assert a.size==(1254,1254)
            core=a.crop((115,115,1139,1139));x=(c-1)*1024;y=(r-1)*1024
            im.paste(core,(x,y))
            contrib.append(dict(B.ref(n,'native source'),patchId=p,sourceDimensions=[1254,1254],sourceCrop=[115,115,1139,1139],destinationBox=[x,y,x+1024,y+1024],globalCoreBox=[origin[0]+x,origin[1]+y,origin[0]+x+1024,origin[1]+y+1024],coreRawRGBPixelSha256=hashlib.sha256(core.tobytes()).hexdigest()))
    im.save(out)
    saved=Image.open(out).convert('RGB');assert saved.size==(4096,4096)
    for q in contrib:
        assert saved.crop(q['destinationBox']).tobytes()==Image.open(q['path']).convert('RGB').crop(q['sourceCrop']).tobytes()
    qa=Z/'qa'/f'{T}-{v}';qa.mkdir(exist_ok=False);items=[]
    def crop(name,box):
        path=qa/f'{name}.native-1to1.png';a=saved.crop(box);a.save(path)
        items.append(dict(B.ref(path,'native1:1 QA crop'),name=name,size=list(a.size),tileBox=list(box),rawRGBPixelSha256=hashlib.sha256(a.tobytes()).hexdigest()))
    for r in range(1,5):
        for c in range(1,5):
            x=(c-1)*1024;y=(r-1)*1024
            crop(f'core_p{r}{c}',[x,y,x+1024,y+1024])
            if c<4:crop(f'v_p{r}{c}_p{r}{c+1}',[x+896,y,x+1152,y+1024])
            if r<4:crop(f'h_p{r}{c}_p{r+1}{c}',[x,y+896,x+1024,y+1152])
    for r in range(1,4):
        for c in range(1,4):crop(f'junction_r{r}_c{c}',[c*1024-128,r*1024-128,c*1024+128,r*1024+128])
    assert len(items)==49
    manifest={'tile':B.ref(out,'4096 candidate'),'tileSize':[4096,4096],'createdAtUtc':B.now(),'sourceSelection':B.ref(SEL,'owned proposed source selection'),'nativeCoreContributions':contrib,'nativePixelOperationsOnly':['integer crop','opaque integer paste'],'resized':False,'warp':False,'paint':False,'feather':False,'all16SavedCorePixelsEqualNativeSource':True,'qa':items,'review':'pending full internal native QA','formalAccepted':False}
    write(qa/'manifest.json',manifest)
    write(Z/'records'/f'{T}.selection-{v}.json',{'tile':T,'patches':{p:B.ref(Z/'native'/n,'native selected source') for p,n in d.items()},'candidate':B.ref(out,'4096 proposed candidate'),'nativeQaManifest':B.ref(qa/'manifest.json','native QA manifest'),'status':'pending_internal_and_external_qa','formalAccepted':False})
    print(json.dumps({'saved':str(out),'sha256':B.sha(out),'qaCount':len(items),'all16SavedCorePixelsEqualNativeSource':True}))
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('op');q.add_argument('patch',nargs='?');q.add_argument('--version',default='v1');q.add_argument('--target');q.add_argument('--source');q.add_argument('--note',default='');a=q.parse_args()
    if a.op=='initial':initial()
    elif a.op=='prepare':prepare(a.patch,a.version,a.target)
    elif a.op=='ingest':B.ingest(a.patch,a.source,a.version)
    elif a.op=='select':select(a.patch,a.version,a.note)
    elif a.op=='assemble':assemble(a.version)
