"""Record built-in outputs and mechanically prepare adjacent guides; no AI drawing."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json, shutil, os, time, uuid
from datetime import datetime, timezone

ZONE=Path(__file__).resolve().parent
ROOT=ZONE.parents[3]
def read(p):
    p=Path(p)
    if p==ROOT/'config/image-generation.json' and not p.exists(): return None
    return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p); temporary=p.with_name(p.name+'.tmp-'+uuid.uuid4().hex[:8])
    temporary.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(6):
        try:
            os.replace(temporary,p)
            return
        except OSError:
            if attempt==5: raise
            time.sleep(0.15)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def current_references():
    p=ZONE/'reference-audit-resumed-20261010.json'
    return read(p if p.exists() else ZONE/'reference-audit.json')['references']
def patch(ident):
    if '_cross_' in ident:
        d=read(ZONE/'guides'/f'{ident}.png.derivation.json')
        return {k:d[k] for k in ['nativeWorldBox','coreWorldBox','coreCrop']}
    tile='_'.join(ident.split('_')[:2])
    return next(x for x in read(ZONE/f'patch-plan-{tile}.json')['patches'] if x['id']==ident.split('_v')[0])

def ingest(args):
    src=Path(args.source); dest=ZONE/'native'/f'{args.id}.png'
    if dest.exists(): raise RuntimeError('Refusing to overwrite native output')
    shutil.copy2(src,dest)
    with Image.open(dest) as im: size=list(im.size); fmt=im.format; mode=im.mode
    refs=current_references()
    p=patch(args.id)
    inp=ZONE/'prompts'/f'{args.id}.inputs.json'
    if inp.exists(): refs=read(inp)
    else: refs=[{'file':p['guide'],'sha256':p['guideSha256'],'role':p['guideRole']},*refs]
    receipt=ZONE/'receipts'/f'{args.id}.tool.json'
    rec={'id':args.id,'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':now(),'nativeWidth':size[0],'nativeHeight':size[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool exposes no model/quality selectors and returns no verifiable model/quality metadata.','prompt':(ZONE/'prompts'/f'{args.id}.prompt.txt').as_posix(),'references':refs,'evidence':{'receipt':receipt.as_posix(),'originalToolPath':src.as_posix(),'fields':['output_hint'],'nativeSizeMeasuredBy':'Pillow PNG decode'},'coreWorldBox':p['coreWorldBox'],'nativeWorldBox':p['nativeWorldBox'],'coreCrop':p['coreCrop'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'candidate_unreviewed','internalSeams':'unreviewed','externalSeams':'unreviewed'}
    if rec['configSnapshot'] is None:
        rec['configSnapshotMissingReason']='Optional workspace config file absent at archival time: '+str(ROOT/'config/image-generation.json')
    write(dest.with_suffix('.png.generation.json'),rec)
    if not getattr(args,'no_progress',False):
        progress=read(ZONE/'progress.json'); progress['generatedNativeCount']=len(list((ZONE/'native').glob('*.png.generation.json'))); progress['updatedAtUtc']=now(); progress['status']='native_inspection'; progress['currentTile']='_'.join(args.id.split('_')[:2]); progress['currentPatch']=args.id; progress['nextStep']='Inspect native geometry, then generate adjacent patch with source overlap constraints.'; write(ZONE/'progress.json',progress)
    print(json.dumps({'file':dest.as_posix(),'size':size,'sha256':rec['sha256']},ensure_ascii=False))

def guide(args):
    p=patch(args.id); base=ZONE/'native'/f'{args.base}.png' if args.base else Path(p['guide']); out=Image.open(base).convert('RGB'); anchors=[]
    for ident in args.neighbor:
        q=patch(ident); src=ZONE/'native'/f'{ident}.png'; rec=read(src.with_suffix('.png.generation.json')); im=Image.open(src).convert('RGB')
        if im.size!=(1254,1254): raise RuntimeError('Unexpected native size: recalculate coverage, no scaling')
        a=p['nativeWorldBox']; b=q['nativeWorldBox']; box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        if box[0]>=box[2] or box[1]>=box[3]: raise RuntimeError('No shared native overlap')
        crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]]; at=[box[0]-a[0],box[1]-a[1]]
        out.paste(im.crop(crop),tuple(at))
        anchors.append({'file':src.as_posix(),'sha256':sha(src),'role':'adjacent native geometry and exact overlap anchor','overlapWorldBox':box,'sourceCrop':crop,'targetPaste':at,'generationRecord':src.with_suffix('.png.generation.json').as_posix()})
    dest=ZONE/'guides'/f'{args.id}.anchored-layout-only.png'; out.save(dest)
    anchor_refs=anchors
    if len(anchors)>1:
        plate=Image.new('RGB',(1254*len(anchors),1254))
        for index,anchor in enumerate(anchors):
            plate.paste(Image.open(anchor['file']).convert('RGB'),(index*1254,0))
        plate_path=ZONE/'guides'/f'{args.id}.native-neighbors.png'; plate.save(plate_path)
        write(plate_path.with_suffix('.png.derivation.json'),{'operation':'no-resize exact native neighbor reference plate, left to right in anchor order','sources':anchors,'finalArt':False})
        anchor_refs=[{'file':plate_path.as_posix(),'sha256':sha(plate_path),'role':'native neighbor reference plate: left=upper neighbor, right=left neighbor; both1254-square unscaled','sources':anchors}]
    refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: sharp overlap strips are native anchors to preserve; blurry remaining region is coordinate layout only'},*anchor_refs,*current_references()]
    write(dest.with_suffix('.png.derivation.json'),{'operation':'mechanical exact native overlap copy; no artwork generation or resampling of native pixels','base':{'file':base.as_posix(),'sha256':sha(base),'native':bool(args.base)},'patch':p,'anchors':anchors,'finalArt':False})
    write(ZONE/'prompts'/f'{args.id}.inputs.json',refs)
    print(json.dumps({'guide':dest.as_posix(),'anchors':anchors,'refs':refs},ensure_ascii=False))

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('ingest'); p.add_argument('id'); p.add_argument('source'); p.add_argument('--no-progress',action='store_true')
    p=sub.add_parser('guide'); p.add_argument('id'); p.add_argument('neighbor',nargs='+'); p.add_argument('--base')
    args=ap.parse_args()
    {'ingest':ingest,'guide':guide}[args.cmd](args)
