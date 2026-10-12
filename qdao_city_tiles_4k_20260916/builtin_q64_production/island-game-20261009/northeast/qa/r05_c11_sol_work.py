from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
TID='r05_c11'; mode=sys.argv[1]
def selection():return read(ZONE/f'selection-{TID}.json')
def patched_native(i):
    p=ZONE/'native'/f'{i}.png';rec=read(p.with_suffix('.png.generation.json'));im=Image.open(p).convert('RGB');a=rec['nativeWorldBox'];tid='_'.join(i.split('_')[:2]);sel=read(ZONE/f'selection-{tid}.json');full=Path(sel.get('candidatePath',ZONE/'tiles'/f'{tid}.png'));ev={'file':p.as_posix(),'sha256':sha(p),'nativeWorldBox':a}
    if full.exists():
        d=read(full.with_suffix('.png.derivation.json'));b=d['worldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        if box[0]<box[2] and box[1]<box[3]:
            crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];im.paste(Image.open(full).crop(crop),at);ev['currentFullTileOverride']={'file':full.as_posix(),'sha256':sha(full),'sourceCrop':crop,'targetPaste':at}
    return im,ev
if mode=='ingest':
    ident=sys.argv[2];src=Path(sys.argv[3]);dest=ZONE/'native'/f'{ident}.png'
    if dest.exists():
        assert sha(src)==sha(dest),'Different existing PNG; refusing overwrite'
    else:shutil.copy2(src,dest)
    gp=dest.with_suffix('.png.generation.json');assert not gp.exists(),'Refusing overwrite generation record'
    im=Image.open(dest);p=patch(ident);refs=read(ZONE/'prompts'/f'{ident}.inputs.json')
    rec={'id':ident,'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':now(),'nativeWidth':im.width,'nativeHeight':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':None,'configSnapshotReason':'Shared ingest expected a missing config file; actual submitted arguments are recorded here.','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in tool exposes no model/quality selectors or verifiable metadata.','prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').as_posix(),'references':refs,'evidence':{'receipt':(ZONE/'receipts'/f'{ident}.tool.json').as_posix(),'originalToolPath':src.as_posix(),'fields':['output_hint'],'nativeSizeMeasuredBy':'Pillow PNG decode'},'coreWorldBox':p['coreWorldBox'],'nativeWorldBox':p['nativeWorldBox'],'coreCrop':p['coreCrop'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'candidate_unreviewed','internalSeams':'unreviewed','externalSeams':'unreviewed'}
    write(gp,rec);print(json.dumps({'file':dest.as_posix(),'size':list(im.size),'sha256':rec['sha256']}));sys.exit()
if mode=='init':
    p=ZONE/f'selection-{TID}.json';assert not p.exists();write(p,{'tileId':TID,'cores':[[None]*4 for _ in range(4)],'overlays':[],'selectionIsPartialCandidate':True,'formalAccepted':False,'pendingIssues':[],'updatedAtUtc':now()})
    write(ZONE/'qa/r05_c11-sol-progress.json',{'tileId':TID,'status':'active_native_generation','worldBox':[40960,16384,45056,20480],'order':'columns4,3,2,1; rows1,2,3,4 within eachcolumn','generated':[],'accepted':[],'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeSize':1254,'core':1024,'halo':115,'sharedProgressModified':False,'updatedAtUtc':now()})
else:
    i=sys.argv[2];assert i.startswith(TID+'_p');r,c=map(int,i.split('_p')[1].split('_v')[0].split('_'));s=selection()
    up=read(ZONE/'selection-r04_c11.json')['cores'][3][c-1] if r==1 else s['cores'][r-2][c-1]
    right=read(ZONE/'selection-r05_c12.json')['cores'][r-1][0] if c==4 else s['cores'][r-1][c]
    assert up and right
    if mode=='guide':
        p=patch(i);base=ZONE/'native'/f'{sys.argv[3]}.png' if len(sys.argv)>3 else Path(p['guide']);out=Image.open(base).convert('RGB');a=p['nativeWorldBox'];plate=Image.new('RGB',(2508,1254));anchors=[]
        for n,(ident,direction) in enumerate([(up,'UPPER'),(right,'RIGHT')]):
            im,e=patched_native(ident);plate.paste(im,(n*1254,0));b=e['nativeWorldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])];crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];out.paste(im.crop(crop),at);e.update(id=ident,direction=direction,sourceCrop=crop,targetPaste=at);anchors.append(e)
        dest=ZONE/'guides'/f'{i}.anchored-layout-only.png';assert not dest.exists();out.save(dest);pp=ZONE/'guides'/f'{i}.native-neighbors.png';plate.save(pp)
        d={'operation':'exact native anchor strip copy; current full adjacent tile overrides its original core artwork wherever available; no final artwork resampling','base':{'file':base.as_posix(),'sha256':sha(base)},'patch':p,'anchors':anchors,'finalArt':False};write(dest.with_suffix('.png.derivation.json'),d);write(pp.with_suffix('.png.derivation.json'),{'operation':'no-resize native upper then right reference plate','sources':anchors,'finalArt':False})
        refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: exact TOP230 and RIGHT230 native anchors, blurry remainder is layout only','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},{'file':pp.as_posix(),'sha256':sha(pp),'role':'native adjacent plate, LEFT PANEL=UPPER '+up+', RIGHT PANEL=RIGHT '+right+'; full current tile artwork overrides older core where applicable','sources':anchors},*current_references()];write(ZONE/'prompts'/f'{i}.inputs.json',refs);print(json.dumps({'id':i,'up':up,'right':right,'nativeWorldBox':a,'guide':dest.as_posix()}))
    elif mode=='inspect':
        cur=Image.open(ZONE/'native'/f'{i}.png').convert('RGB');assert cur.size==(1254,1254)
        u,ue=patched_native(up);v,ve=patched_native(right)
        strip=Image.new('RGB',(1024,512));strip.paste(u.crop((115,883,1139,1139)),(0,0));strip.paste(cur.crop((115,115,1139,371)),(0,256));strip.save(ZONE/'qa'/f'{i}.up.png')
        strip=Image.new('RGB',(512,1024));strip.paste(cur.crop((883,115,1139,1139)),(0,0));strip.paste(v.crop((115,115,371,1139)),(256,0));strip.save(ZONE/'qa'/f'{i}.right.png')
        write(ZONE/'qa'/f'{i}.joins.json',{'id':i,'nativeSha256':sha(ZONE/'native'/f'{i}.png'),'upper':ue,'right':ve,'evidence':[str(ZONE/'qa'/f'{i}.up.png'),str(ZONE/'qa'/f'{i}.right.png')],'status':'pending_visual_review','resized':False})
    elif mode=='accept':
        p=ZONE/'qa'/f'{i}.joins.json';q=read(p);q.update(status='passed_native_and_two_joins_at100pct',reviewedAtUtc=now());write(p,q)
        p=ZONE/'native'/f'{i}.png.generation.json';q=read(p);q.update(status='passed_internal_native_and_recorded_joins',qa=(ZONE/'qa'/f'{i}.joins.json').as_posix());write(p,q)
        s['cores'][r-1][c-1]=i;s['updatedAtUtc']=now();write(ZONE/f'selection-{TID}.json',s)
        p=ZONE/'qa/r05_c11-sol-progress.json';q=read(p)
        for k in ['generated','accepted']:
            if i not in q[k]:q[k].append(i)
        q.update(currentId=i,selectedCoreIds=s['cores'],selectedCoreCount=sum(bool(v) for row in s['cores'] for v in row),updatedAtUtc=now());write(p,q);print(json.dumps({'id':i,'selectedCount':q['selectedCoreCount']}))
    elif mode=='prompt':
        subject=sys.argv[3]
        prompt=f'''Use case: precise-object-edit
Asset type: native1254x1254 Q-style Daoist daylight game map patch with a1024pixel central core.
Primary request: Complete Image1 into sharp original painted game artwork. It is an exact-coordinate crop, not a whole scene. Its blurred region is layout-only: render that region crisply while preserving composition, scale and every cropped object's position. {subject}
Input images: Image1 edit target, blurred layout and exact TOP230px and RIGHT230px native anchor strips. Image2 unscaled adjacent native reference plate, LEFT=UPPER and RIGHT=RIGHT neighbor. Image3 sole full-map layout authority only; Image4 approved material/festival art reference only; Image5 primary approved Daoist Q painting style only, ignore its UI and night.
Style/medium: crisp painterly Q game artwork identical to the sharp neighbors, rich red wood, blue glazed tile and gold ornament where already visible, natural varied cool pale gray/cyan fitted stone and quiet moss, original clear warm daylight and soft shadows.
Constraints: Exactly preserve TOP y0..229 and RIGHT x1024..1253 sharp native anchors, including shapes, geometry, texture, lighting and object contours. Continue them smoothly into the new sharp region without a straight stripe, height jump, duplicate objects or frozen rectangle. Keep same1254square framing, pixel scale and camera. Existing architecture, residence location and footprint, courtyard layout and connected roads remain exactly in place. The blurry layout is not final texture; paint rich native detail for that part only. No potted plants, no additional buildings, no extra characters, no UI, no labels, no watermark, no nighttime, no all-red paving, no new burning piles. Do not copy the reference as a small whole island. Return only the finished exact crop.'''
        (ZONE/'prompts'/f'{i}.prompt.txt').write_text(prompt,encoding='utf-8');print(prompt)
