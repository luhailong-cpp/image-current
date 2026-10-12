"""Export selected pose edits with unchanged registration; promote only SHA-bound approvals."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
REVIEW=ROOT/'provenance/ground-contact-20261004'
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(direction,frame,version):
    reg=load(ROOT/'registration.json');scale=reg['globalScale'];sx,sy=reg['sequences']['run/'+direction]['sourceRoot'];tx,ty=reg['targetRoot']
    assert scale==0.65 and [tx,ty]==[512,942]
    matrix=(1/scale,0,sx-tx/scale,0,1/scale,sy-ty/scale)
    native=f'staging/run/{direction}/{frame:02}-v{version}.native.png';record=f'provenance/run/{direction}{frame:02}-v{version}.generation.json'
    generation=load(ROOT/record);assert sha(ROOT/native)==generation['sha256']
    im=Image.open(ROOT/native);im.load();assert im.size==(1254,1254) and im.mode=='RGBA'
    out=f'staging/run/{direction}/ground-{frame:02}-v{version}.png'
    exported=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
    alpha=exported.getchannel('A');border=max(alpha.crop(b).getextrema()[1] for b in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])
    assert border==0;exported.save(ROOT/out)
    meta={'operation':'uniform_resample_and_constant_sequence_registration','status':'pending_visual_review','createdAt':datetime.now(timezone.utc).isoformat(),'file':out,'sha256':sha(ROOT/out),'width':1024,'height':1024,'mode':'RGBA','source':{'file':native,'sha256':generation['sha256'],'nativeSize':[1254,1254],'generationRecord':record},'actualModel':None,'actualQuality':None,'transform':{'globalScale':scale,'sourceRoot':[sx,sy],'targetRoot':[tx,ty],'inverseAffine':matrix,'registrationFile':'registration.json','perFrameNormalization':False},'edgeMaxAlpha':border,'finalVisualPassed':False,'clientValidated':False,'sourceGeneration':generation,'nativeSourceRecord':record}
    save(ROOT/(out+'.generation.json'),meta)
    return {'direction':direction,'frame':frame,'version':version,'reviewFile':out,'sha256':meta['sha256'],'nativeSha256':generation['sha256']}
if __name__=='__main__':
    if sys.argv[1]=='prepare': print(json.dumps(prepare(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))))
    elif sys.argv[1]=='promote':
        accepted=load(REVIEW/'acceptance.json');assert accepted['accepted'] and not accepted['clientValidated']
        selection=load(ROOT/'final-selection.json');manifest=load(ROOT/'final/manifest.json');old=[]
        for item in accepted['repairs']:
            row=next(r for r in selection if r['action']=='run' and r['direction']==item['direction'] and r['frame']==item['frame'])
            meta=load(ROOT/(item['reviewFile']+'.generation.json'))
            assert sha(ROOT/row['file'])==item['previousSha256']==row['sha256']
            assert sha(ROOT/item['reviewFile'])==meta['sha256']==item['sha256']
            assert sha(ROOT/meta['source']['file'])==meta['source']['sha256']==item['nativeSha256']
            old.append({'selection':dict(row),'generationRecord':load(ROOT/row['generationRecord'])})
        assert not (REVIEW/'superseded-records.json').exists()
        now=datetime.now(timezone.utc).isoformat();save(REVIEW/'superseded-records.json',{'replacedAt':now,'records':old})
        for item in accepted['repairs']:
            row=next(r for r in selection if r['action']=='run' and r['direction']==item['direction'] and r['frame']==item['frame']);meta=load(ROOT/(item['reviewFile']+'.generation.json'))
            shutil.copyfile(ROOT/item['reviewFile'],ROOT/row['file'])
            meta.update(file=row['file'],status='offline_artwork_accepted_client_pending',finalVisualPassed=True,offlineAcceptance='provenance/ground-contact-20261004/acceptance.json',sourceRetention='native/intermediate PNG removed after final-reference verification per user policy; text lineage retained')
            save(ROOT/row['generationRecord'],meta)
            row.update(sha256=meta['sha256'],nativeSourceFile=meta['source']['file'],nativeSha256=meta['source']['sha256'],visualStatus='连续四帧接地与膝踝鞋掌方向复核通过；客户端未验收',finalVisualPassed=True,clientValidated=False)
        manifest.update(frames=selection,artworkUpdatedAt=now,status='offline_artwork_complete_client_pending',latestVisualAcceptance='provenance/ground-contact-20261004/acceptance.json')
        save(ROOT/'final-selection.json',selection);save(ROOT/'final/manifest.json',manifest)
        save(REVIEW/'promotion.json',{'promotedAt':now,'repairs':accepted['repairs']})
        print(json.dumps({'promoted':len(accepted['repairs'])}))
