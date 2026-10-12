from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
TID='r04_c11'; mode=sys.argv[1]
def selection():return read(ZONE/f'selection-{TID}.json')
def patched_native(i):
    p=ZONE/'native'/f'{i}.png';rec=read(p.with_suffix('.png.generation.json'));im=Image.open(p).convert('RGB');a=rec['nativeWorldBox'];tid='_'.join(i.split('_')[:2]);full=ZONE/'tiles'/f'{tid}.png';ev={'file':p.as_posix(),'sha256':sha(p),'nativeWorldBox':a}
    if full.exists():
        d=read(full.with_suffix('.png.derivation.json'));b=d['worldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        if box[0]<box[2] and box[1]<box[3]:
            crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];im.paste(Image.open(full).crop(crop),at);ev['currentFullTileOverride']={'file':full.as_posix(),'sha256':sha(full),'sourceCrop':crop,'targetPaste':at}
    return im,ev
if mode=='init':
    p=ZONE/f'selection-{TID}.json';assert not p.exists();write(p,{'tileId':TID,'cores':[[None]*4 for _ in range(4)],'overlays':[],'selectionIsPartialCandidate':True,'formalAccepted':False,'pendingIssues':[],'updatedAtUtc':now()})
    write(ZONE/'qa/r04_c11-progress.json',{'tileId':TID,'status':'active_native_generation','worldBox':[40960,12288,45056,16384],'order':'columns4,3,2,1; rows1,2,3,4 within eachcolumn','generated':[],'accepted':[],'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeSize':1254,'core':1024,'halo':115,'sharedProgressModified':False,'updatedAtUtc':now()})
else:
    i=sys.argv[2];assert i.startswith(TID+'_p');r,c=map(int,i.split('_p')[1].split('_v')[0].split('_'));s=selection()
    up=read(ZONE/'selection-r03_c11.json')['cores'][3][c-1] if r==1 else s['cores'][r-2][c-1]
    right=read(ZONE/'selection-r04_c12.json')['cores'][r-1][0] if c==4 else s['cores'][r-1][c]
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
        p=ZONE/'qa/r04_c11-progress.json';q=read(p)
        for k in ['generated','accepted']:
            if i not in q[k]:q[k].append(i)
        q.update(currentId=i,selectedCoreIds=s['cores'],selectedCoreCount=sum(bool(v) for row in s['cores'] for v in row),updatedAtUtc=now());write(p,q);print(json.dumps({'id':i,'selectedCount':q['selectedCoreCount']}))
