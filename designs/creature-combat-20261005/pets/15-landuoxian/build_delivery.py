from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
from io import BytesIO
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
COUNTS={'hit':6,'attack':12,'cast':16}
DURATIONS={'hit':40,'attack':30,'cast':45}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    frames=[]; groups=[]; errors=[]; hashes={}; pixels={}
    review_file=ROOT/'visual-review.json'
    review=json.loads(review_file.read_text(encoding='utf-8')) if review_file.exists() else {}
    reviewed=review.get('frameHashes',{})
    for action,count in COUNTS.items():
        for direction in ['E','W']:
            key=f'{action}/{direction}'; present=[]
            for n in range(1,count+1):
                path=ROOT/'runtime'/key/f'{n:02d}.png'
                if not path.exists():
                    errors.append({'type':'missing_frame','file':str(path.relative_to(ROOT))}); continue
                im=Image.open(path); im.load()
                digest=sha(path); pixel=hashlib.sha256(im.tobytes()).hexdigest()
                if digest in hashes: errors.append({'type':'duplicate_sha','files':[hashes[digest],str(path.relative_to(ROOT))]})
                if pixel in pixels: errors.append({'type':'duplicate_pixels','files':[pixels[pixel],str(path.relative_to(ROOT))]})
                hashes[digest]=str(path.relative_to(ROOT)); pixels[pixel]=str(path.relative_to(ROOT))
                if im.size!=(1024,1024) or im.mode!='RGBA': errors.append({'type':'dimensions_or_mode','file':str(path)})
                alpha=im.getchannel('A') if im.mode=='RGBA' else None
                extrema=alpha.getextrema() if alpha else None
                if extrema is None or extrema[0]!=0 or extrema[1]!=255: errors.append({'type':'alpha','file':str(path)})
                rec_path=path.with_suffix('.png.generation.json')
                if not rec_path.exists(): rec_path=ROOT/'provenance'/action/direction/f'{n:02d}.generation.json'
                if not rec_path.exists(): errors.append({'type':'generation_record_missing','file':str(path)})
                else:
                    rec=json.loads(rec_path.read_text(encoding='utf-8-sig'))
                    if rec.get('sha256')!=digest: errors.append({'type':'record_sha_mismatch','file':str(path)})
                event='hit_peak' if action=='hit' and n==3 else 'attack_release' if action=='attack' and n==7 else 'cast_release' if action=='cast' and n==9 else None
                frame={'file':path.relative_to(ROOT).as_posix(),'action':action,'direction':direction,'index':n,'width':im.width,'height':im.height,'durationMs':DURATIONS[action],'pivot':[0.5,0.08],'anchorTopLeft':[512,942],'event':event,'sha256':digest,'pixelSHA256':pixel,'alphaExtrema':extrema,'alphaBBox':alpha.getbbox() if alpha else None,'generationRecord':rec_path.relative_to(ROOT).as_posix(),'visualStatus':'pending_final_review'}
                if reviewed.get(frame['file'])==digest: frame['visualStatus']='inspected_static_and_preview'
                frames.append(frame);present.append(frame)
            groups.append({'id':key,'action':action,'direction':direction,'expectedFrames':count,'durationMs':DURATIONS[action],'totalDurationMs':count*DURATIONS[action],'frames':present})
    manifest={'schemaVersion':1,'character':'岚铎仙','slug':'15-landuoxian','expectedFrameCount':68,'frameCount':len(frames),'generatedAt':datetime.now(timezone.utc).isoformat(),'directions':{'E':'front three-quarter southeast','W':'true back three-quarter northwest'},'exportTransform':{'wholeCanvasResizedTo':[920,920],'offset':[52,37],'outputSize':[1024,1024],'perFrameAlignment':False},'groups':groups,'frames':frames,'clientIntegration':'not_performed'}
    dump(ROOT/'manifest.json',manifest)
    dump(ROOT/'validation.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed' if not errors and len(frames)==68 else 'incomplete_or_failed','frameCount':len(frames),'expected':68,'errors':errors,'checks':['expected filenames','RGBA dimensions','real alpha extrema','file SHA256','pixel duplicate hashes','generation record SHA'],'visualReview':'separate','clientIntegration':'not_performed'})
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['file']}\n" for f in frames),encoding='utf-8')
    preview=ROOT/'preview'; preview.mkdir(exist_ok=True)
    for group in groups:
        cols=4; rows=(len(group['frames'])+cols-1)//cols
        if not rows: continue
        board=Image.new('RGB',(cols*280,rows*310),'#e8eee9');draw=ImageDraw.Draw(board)
        for j,f in enumerate(group['frames']):
            x=(j%cols)*280; y=(j//cols)*310
            im=Image.open(ROOT/f['file']);im.thumbnail((280,280),Image.Resampling.LANCZOS)
            board.paste(im,(x,y),im)
            draw.text((x+10,y+284),f"{group['id']} {f['index']:02d} / {f['durationMs']}ms",fill='#19392d')
        contact=preview/(group['id'].replace('/','-')+'-contact.png')
        encoded=BytesIO();board.save(encoded,format='PNG');payload=encoded.getvalue()
        if not contact.exists() or contact.read_bytes()!=payload:
            temp=contact.with_suffix('.new.png');temp.write_bytes(payload);temp.replace(contact)
    template=(ROOT/'preview-template.html').read_text(encoding='utf-8')
    (preview/'index.html').write_text(template.replace('__GROUP_DATA__',json.dumps(groups,ensure_ascii=False)),encoding='utf-8')
    for group in groups:
        single=template.replace('__GROUP_DATA__',json.dumps([group],ensure_ascii=False)).replace('</style>','.grid{grid-template-columns:1fr;max-width:800px;margin:auto}</style>').replace('岚铎仙 · 受击 / 普攻 / 施法',f"岚铎仙 · {group['id']}")
        (preview/(group['id'].replace('/','-')+'.html')).write_text(single,encoding='utf-8')
    print(json.dumps({'frames':len(frames),'errors':len(errors)},ensure_ascii=False))

if __name__=='__main__': main()
