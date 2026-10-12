"""Rebuild current contact sheets and preview data from runtime, not deleted natives."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
profiles=json.loads((ROOT/'run-timing.json').read_text(encoding='utf-8-sig')) if (ROOT/'run-timing.json').exists() else {}
grouped={}
for f in manifest['frames']:
    grouped.setdefault(f['slot'].rsplit('/',1)[0],[]).append(f)
groups=[]
for key,frames in grouped.items():
    frames.sort(key=lambda f:f['slot'])
    action,direction=key.split('/')
    profile=profiles.get('directions',{}).get(direction) if action=='run' else None
    ms={'run':60,'hit':40,'attack':30,'cast':45}[action]
    g={'key':key,'ms':ms,'frames':['../'+f['file']+'?v='+f['sha256'][:12] for f in frames]}
    if profile:g.update({'frameMs':profile['frameMs'],'phases':profile['phases'],'cycleMs':sum(profile['frameMs'])})
    sheet=Image.new('RGB',(1024,((len(frames)+3)//4)*282),'#e9e4d5')
    for i,f in enumerate(frames):
        out=Image.open(ROOT/f['file']).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
        x=i%4*256;y=i//4*282
        sheet.paste(out,(x,y+24),out)
        label=f'{key} {i+1:02}'
        if profile:label+=f'  {profile["frameMs"][i]}ms'
        ImageDraw.Draw(sheet).text((x+8,y+5),label,fill='#173c31')
    sheet.save(ROOT/'preview'/f'{action}-{direction}-contact.png')
    groups.append(g)
data=ROOT/'preview/data.js'
data.write_text('window.PREVIEW_DATA='+json.dumps(groups,ensure_ascii=False)+';',encoding='utf-8')
html=ROOT/'preview/index.html'
s=html.read_text(encoding='utf-8')
s=re.sub(r'src="data\.js(?:\?v=[^"]*)?"','src="data.js?v='+sha(data)[:12]+'"',s)
html.write_text(s,encoding='utf-8')
print(json.dumps({'groups':len(groups),'images':sum(len(g['frames']) for g in groups),'profiles':len(profiles.get('directions',{}))}))
