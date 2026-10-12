"""Own sr2..4/sc4 source preparation, records and QA only; no shared state writes."""
from pathlib import Path
import sys,json,shutil,re
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import production as p
INDEX=ROOT/'qa'/'r10_c04-right-column-worker-map.json'
def state():
    return p.load(INDEX) if INDEX.exists() else {'r10_c04':[[None,None,None,'r10_c04_s01_04_v01']]+[[None]*4 for _ in range(3)],'tile':'r10_c04','ownership':'sr2/sc4, sr3/sc4, sr4/sc4 only; row1 anchor external','status':'in_progress','formalAccepted':False,'generationCount':0,'qa':{}}
def save(d):
    d['updatedAtUtc']=p.now();p.dump(INDEX,d)
def stemcheck(stem):
    assert re.fullmatch(r'r10_c04_s0[234]_0[234]_v[0-9]{2}',stem),'Outside assigned right-side sources'
def prepare(sr,attempt=1,sc=4):
    assert sr in (2,3,4)
    assert sc in (2,3,4)
    co=p.coords(10,4,sr,sc);stem=f'r10_c04_s{sr:02}_{sc:02}_v{attempt:02}'
    req_path=ROOT/'prompts'/(stem+'.request.json');assert not req_path.exists(),'Do not overwrite a prepared request'
    worker=ROOT/'qa'/'r10_c04-worker-map.json'
    main=p.load(worker)['r10_c04'] if worker.exists() else [[None]*4 for _ in range(4)]
    own=state();top=own['r10_c04'][sr-2][sc-1] or main[sr-2][sc-1];assert top,'Select above source first'
    left=main[sr-1][sc-2]
    right=own['r10_c04'][sr-1][sc] if sc in (2,3) else None
    if sc in (2,3):
        assert right,'Select right source first'
        own['r10_c04'][0][sc-1]=main[0][sc-1]
        own['ownership']='sr2..4/sc2..4 only; row1 anchors external';own['status']='in_progress';save(own)
    layout=ROOT/'guides'/(stem+'.layout-only.png')
    assert not layout.exists()
    with Image.open(p.REFS[0][0]) as im:im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
    p.dump(str(layout)+'.derivation.json',{'operation':'layout-only overview EXTENT; not a native art source','source':p.metadata(*p.REFS[0]),'coordinates':co,'sha256':p.hashfile(layout)})
    canvas=Image.open(layout).convert('RGB');sources=[p.metadata(layout,'layout-only base')]
    for neighbor in ([left] if left else [])+([right] if right else [])+[top]:
        path=ROOT/'native'/(neighbor+'.png');rec=p.load(str(path)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];box=co['nativeGlobalBox']
        ib=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        assert ib[0]<ib[2] and ib[1]<ib[3]
        crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
        with Image.open(path) as im:canvas.paste(im.crop(crop),dest)
        sources.append({**p.metadata(path,'native top constraint' if neighbor==top else ('selected right native constraint' if neighbor==right else 'selected left native constraint')),'sourceCrop':crop,'destinationTopLeft':dest})
    guide=ROOT/'guides'/(stem+'.native-overlap-guide.png');canvas.save(guide)
    p.dump(str(guide)+'.derivation.json',{'operation':'same-coordinate native crop/paste over layout-only guide; TOP wins corner; no native resampling','sources':sources,'coordinates':co,'sha256':p.hashfile(guide)})
    p.dump(ROOT/'prompts'/(stem+'.coordinates.json'),co)
    refs=[p.metadata(guide,'coordinate edit target; top native 230px and any right native 230px fixed; blurred remainder layout only'),p.metadata(ROOT/'native'/(top+'.png'),'above selected native source context')]+[p.metadata(*r) for r in p.REFS]
    p.dump(req_path,{'tool':'image_gen.imagegen','createdAtUtc':p.now(),'coordinates':co,'top':top,'rightAtPreparation':right,'leftAtPreparation':left,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
    print(json.dumps({'stem':stem,'guide':guide.as_posix(),'refs':[x['path'] for x in refs],'top':top,'right':right,'left':left,'coordinates':co}))
def ingest(stem,source):
    stemcheck(stem);src=Path(source);dst=ROOT/'native'/(stem+'.png');assert not dst.exists()
    shutil.copy2(src,dst)
    with Image.open(dst) as im:size=im.size;fmt=im.format;mode=im.mode
    req=p.load(ROOT/'prompts'/(stem+'.request.json'))
    rec={'file':dst.as_posix(),'sha256':p.hashfile(dst),'generatedAt':p.now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; builtin tool lacks selectors and actual model/quality disclosure.','prompt':(ROOT/'prompts'/(stem+'.prompt.txt')).as_posix(),'references':req['references'],'sourceToolPath':src.as_posix(),'evidence':[{'path':(ROOT/'receipts'/(stem+'.tool.json')).as_posix(),'type':'tool receipt; image data omitted'}],'coordinates':req['coordinates'],'status':'awaiting_visual_QA','nativeSizeMatchesPlan':list(size)==[1254,1254] and mode=='RGB'}
    p.dump(str(dst)+'.generation.json',rec)
    d=state();d['generationCount']+=1;d['lastGenerated']=stem;save(d)
    print(json.dumps({'file':dst.as_posix(),'dimensions':size,'sha256':rec['sha256'],'nativeSizeMatchesPlan':rec['nativeSizeMatchesPlan']}))
def check(stem):
    stemcheck(stem);req=p.load(ROOT/'prompts'/(stem+'.request.json'));sr=req['coordinates']['subrow'];sc=req['coordinates']['subcolumn'];paths=[]
    name=stem+'-right-column-top-native100';p.seamcheck(req['top'],stem,'vertical',name);paths.append((ROOT/'qa'/(name+'.png')).as_posix())
    main=ROOT/'qa'/'r10_c04-worker-map.json';left=p.load(main)['r10_c04'][sr-1][sc-2] if main.exists() else None
    if left:
        name=stem+'-right-column-left-native100';p.seamcheck(left,stem,'horizontal',name);paths.append((ROOT/'qa'/(name+'.png')).as_posix())
    right=state()['r10_c04'][sr-1][sc] if sc in (2,3) else None
    if right:
        name=stem+'-right-column-right-native100';p.seamcheck(stem,right,'horizontal',name);paths.append((ROOT/'qa'/(name+'.png')).as_posix())
    print(json.dumps({'checks':paths,'leftAtQA':left}))
def select(stem,note):
    stemcheck(stem);co=p.load(ROOT/'prompts'/(stem+'.coordinates.json'));d=state();d['r10_c04'][co['subrow']-1][co['subcolumn']-1]=stem;d['qa'][stem]={'status':'candidate','visualNote':note,'reviewedAtUtc':p.now()};d['status']='nine_sources_selected' if all(d['r10_c04'][r][c] for r in (1,2,3) for c in (1,2,3)) else 'in_progress';save(d)
    print(json.dumps({'selected':stem,'status':d['status']}))
if __name__=='__main__':
    op=sys.argv[1]
    if op=='prepare':prepare(*map(int,sys.argv[2:]))
    elif op=='prepare3':prepare(*map(int,sys.argv[2:]),sc=3)
    elif op=='prepare2':prepare(*map(int,sys.argv[2:]),sc=2)
    elif op=='ingest':ingest(*sys.argv[2:])
    elif op=='check':check(sys.argv[2])
    elif op=='select':select(*sys.argv[2:])
