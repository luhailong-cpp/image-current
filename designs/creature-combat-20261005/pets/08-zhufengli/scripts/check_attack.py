from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
checks=[];sha_seen={};issues=[]
for d in ['E','W']:
    contact=Image.new('RGB',(1280,1032),(225,231,229));draw=ImageDraw.Draw(contact)
    for n in range(1,13):
        p=ROOT/'runtime'/'attack'/d/f'{n:02}.png'
        if not p.exists(): issues.append(f'Missing {d}/{n:02}');continue
        data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();im=Image.open(p);a=im.getchannel('A');h=a.histogram()
        rec=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8-sig'))
        threshold=a.point(lambda x:255 if x>128 else 0).getbbox()
        dup=sha_seen.get(sha);sha_seen[sha]=str(p)
        if dup:issues.append(f'Duplicate {p}: {dup}')
        refs_ok=all(Path(r['path']).exists() and hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'] for r in rec['references'])
        entry={'direction':d,'frame':n,'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha,'dimensions':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema()),'alphaCounts':{'zero':h[0],'partial':sum(h[1:255]),'opaque':h[255]},'alphaBBox':a.getbbox(),'alphaAbove128BBox':threshold,'hashMatchesRecord':sha==rec['sha256'],'promptExists':Path(rec['prompt']).exists(),'receiptExists':Path(rec['evidence']['receipt']).exists(),'allReferencesExistAndMatchSha':refs_ok,'native':rec['native']}
        checks.append(entry)
        if im.size!=(1024,1024) or im.mode!='RGBA' or h[0]==0 or not entry['hashMatchesRecord'] or not refs_ok: issues.append(f'Technical check failed {d}/{n:02}')
        thumb=im.resize((304,304),Image.Resampling.LANCZOS);x=(n-1)%4*320+8;y=(n-1)//4*344+8;contact.paste(thumb,(x,y),thumb);draw.text((x+6,y+310),f'{d} attack {n:02} | 30 ms',fill=(30,42,36))
    contact.save(qa/f'attack-{d}-contact.jpg',quality=95)
report={'action':'attack','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedFrames':24,'actualFrames':len(checks),'uniqueHashes':len(sha_seen),'passed':len(checks)==24 and not issues,'issues':issues,'frames':checks,'scopeNote':'Technical integrity only, does not certify animation continuity or client integration.'}
(qa/'attack-technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))
