from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
TID='r06_c12'
PROGRESS=ZONE/'qa/r06_c12-continued-progress-20261013.json'
def selection():return read(ZONE/f'selection-{TID}.json')
def patched_native(i):
    p=ZONE/'native'/f'{i}.png';rec=read(p.with_suffix('.png.generation.json'));im=Image.open(p).convert('RGB');a=rec['nativeWorldBox'];tid='_'.join(i.split('_')[:2]);sel=read(ZONE/f'selection-{tid}.json');full=Path(sel.get('candidatePath',ZONE/'tiles'/f'{tid}.png'));ev={'file':p.as_posix(),'sha256':sha(p),'nativeWorldBox':a}
    if full.exists():
        d=read(full.with_suffix('.png.derivation.json'));b=d['worldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        if box[0]<box[2] and box[1]<box[3]:
            crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];im.paste(Image.open(full).crop(crop),at);ev['currentFullTileOverride']={'file':full.as_posix(),'sha256':sha(full),'sourceCrop':crop,'targetPaste':at}
    return im,ev
mode=sys.argv[1]
if mode=='init':
    dest=ZONE/f'selection-{TID}.json';assert not dest.exists();write(dest,{'tileId':TID,'cores':[[None]*4 for _ in range(4)],'overlays':[],'selectionIsPartialCandidate':True,'formalAccepted':False,'pendingIssues':[],'updatedAtUtc':now()})
    write(PROGRESS,{'tileId':TID,'worker':'repair_continued','status':'active_native_generation','worldBox':[45056,20480,49152,24576],'order':'rows1..4;columns1..4','scope':'r06_c12 only; old repair queue continued by root','conflictCheck':'No native/selected/guide r06_c12 before init; qa references only historical missing inventories. Not allocated in current split.','splitSha256':sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'agentsSha256':sha(ROOT/'AGENTS.md'),'generated':[],'selected':[],'actualModel':None,'formalAccepted':False,'nativeSize':1254,'core':1024,'halo':115,'sharedProgressModified':False,'updatedAtUtc':now()})
    ref=current_references()[0];im=Image.open(ref['file']);crop=im.crop((975,435,1087,548));dest=ZONE/'guides/r06_c12.layout-context-nearest.png';assert not dest.exists();crop.resize((1008,1017),Image.Resampling.NEAREST).save(dest)
    write(dest.with_suffix('.png.derivation.json'),{'operation':'layout-only nearest enlargement; no final art','source':ref,'crop':[975,435,1087,548]})
    sys.exit()
i=sys.argv[2];assert i.startswith(TID+'_p');r,c=map(int,i.split('_p')[1].split('_v')[0].split('_'));s=selection()
up=read(ZONE/'selection-r05_c12.json')['cores'][3][c-1] if r==1 else s['cores'][r-2][c-1]
left=s['cores'][r-1][c-2] if c>1 else None
neighbors=[(up,'UPPER')]+([(left,'LEFT')] if left else [])
assert up
if mode=='guide':
    p=patch(i);a=p['nativeWorldBox'];base=ZONE/'native'/f'{sys.argv[3]}.png' if len(sys.argv)>3 else Path(p['guide']);out=Image.open(base).convert('RGB');anchors=[]
    for ident,direction in neighbors:
        im,e=patched_native(ident);b=e['nativeWorldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])];crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];out.paste(im.crop(crop),at);e.update(id=ident,direction=direction,sourceCrop=crop,targetPaste=at);anchors.append(e)
    dest=ZONE/'guides'/f'{i}.anchored-layout-only.png';assert not dest.exists();out.save(dest)
    d={'operation':'exact native anchor strip copy; current full adjacent tile overrides original core artwork wherever available; no final artwork resampling','base':{'file':base.as_posix(),'sha256':sha(base)},'patch':p,'anchors':anchors,'finalArt':False};write(dest.with_suffix('.png.derivation.json'),d)
    refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: sharp TOP230 and optionally LEFT230 native anchor strips; blurred remainder is layout only','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},*current_references()]
    write(ZONE/'prompts'/f'{i}.inputs.json',refs);q=read(PROGRESS);q.update(currentId=i,status='guide_prepared',updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'id':i,'neighbors':neighbors,'guide':dest.as_posix()}))
elif mode=='prompt':
    subject=sys.argv[3]
    prompt=f'''Use case: precise-object-edit. Complete Image1 into one native 1254x1254 crisp hand-painted Daoist Q game-map crop with 1024px central core and 115px halo. The sharp TOP230 and LEFT230 if present are exact native overlap anchors, and the blurred remaining region is coordinate layout only. Repaint the blurred part with original clear native detail while exactly preserving its composition, camera, scale and every cropped object position. {subject}
Image2 is sole full-map layout authority only. Image3 is material and spring-festival architecture style only, not a coordinate crop. Image4 is approved Daoist Q painting style only; ignore UI/night. Keep the exact native sharp anchors, including slab-joint endpoints, object contours, lighting and texture scale; continue them smoothly throughout the crop without a straight border, a frozen rectangle, a shifted joint or repeated objects. Natural pale gray/cyan fitted stone, gentle warm daylight, clear painterly details equally in focus everywhere, subtle moss only at joints where indicated. Keep all existing architecture and vegetation exactly in their layout positions. No new buildings, no characters, no pots, no text or UI, no watermark, no nighttime, no distant blur, no smeared upscaled pixels. Return only the finished exact 1254-square image.'''
    dest=ZONE/'prompts'/f'{i}.prompt.txt';assert not dest.exists();dest.write_text(prompt,encoding='utf-8')
    q=read(PROGRESS);q.update(status='imagegen_prepared',inFlight={'id':i,'tool':'image_gen.imagegen','actualModel':None,'preparedAtUtc':now()},updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'prompt':prompt,'refs':[v['file'] for v in read(ZONE/'prompts'/f'{i}.inputs.json')]}))
elif mode=='inspect':
    cur=Image.open(ZONE/'native'/f'{i}.png').convert('RGB');assert cur.size==(1254,1254);evidence=[];records=[]
    for ident,direction in neighbors:
        im,e=patched_native(ident)
        if direction=='UPPER':
            strip=Image.new('RGB',(1024,512));strip.paste(im.crop((115,883,1139,1139)),(0,0));strip.paste(cur.crop((115,115,1139,371)),(0,256))
        else:
            strip=Image.new('RGB',(512,1024));strip.paste(im.crop((883,115,1139,1139)),(0,0));strip.paste(cur.crop((115,115,371,1139)),(256,0))
        dest=ZONE/'qa'/f'{i}.{direction.lower()}.png';assert not dest.exists();strip.save(dest);evidence.append(dest.as_posix());records.append(e)
    write(ZONE/'qa'/f'{i}.joins.json',{'id':i,'nativeSha256':sha(ZONE/'native'/f'{i}.png'),'neighbors':records,'evidence':evidence,'status':'pending_visual_review','resized':False})
elif mode=='accept':
    note=sys.argv[3];p=ZONE/'qa'/f'{i}.joins.json';q=read(p);q.update(status='passed_native_and_recorded_joins_at100pct',reviewNote=note,reviewedAtUtc=now());write(p,q)
    p=ZONE/'native'/f'{i}.png.generation.json';q=read(p);q.update(status='passed_native_layout_and_recorded_joins',qa=(ZONE/'qa'/f'{i}.joins.json').as_posix());write(p,q)
    s['cores'][r-1][c-1]=i;s['updatedAtUtc']=now();write(ZONE/f'selection-{TID}.json',s);q=read(PROGRESS)
    for k in ['generated','selected']:
        if i not in q[k]:q[k].append(i)
    q.update(currentId=i,status='active_native_generation',inFlight=None,selectedCoreIds=s['cores'],selectedCoreCount=sum(bool(v) for row in s['cores'] for v in row),updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'id':i,'selectedCount':q['selectedCoreCount']}))

