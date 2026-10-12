from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib
base=Path(__file__).resolve().parents[1]
out=base/'records'/'W-QA';out.mkdir(exist_ok=True)
report={'scope':['hit/W','cast/W'],'checks':[],'duplicates':[],'runtimeIntegration':'not performed'}
seen={}
for action,count,dur in [('hit',6,40),('cast',16,45)]:
    cell=320 if action=='hit' else 256
    cols=3 if action=='hit' else 4
    rows=(count+cols-1)//cols
    sheet=Image.new('RGB',(cols*cell,rows*(cell+28)),(218,224,219));d=ImageDraw.Draw(sheet)
    for i in range(1,count+1):
        p=base/'runtime'/action/'W'/f'{i:02}.png';im=Image.open(p);im.load()
        h=hashlib.sha256(p.read_bytes()).hexdigest();a=im.getchannel('A')
        if h in seen:report['duplicates'].append([str(p),seen[h]])
        seen[h]=str(p)
        bounds=a.point(lambda x:255 if x>=128 else 0).getbbox()
        record=p.with_suffix('.png.generation.json');r=json.loads(record.read_text(encoding='utf-8'))
        report['checks'].append({'file':str(p.relative_to(base)),'size':im.size,'mode':im.mode,'alphaRange':a.getextrema(),'opaqueBoundingBox':bounds,'shaMatchesGenerationRecord':h==r['sha256'],'edgeAlphaMax':[a.crop((0,0,1,1024)).getextrema()[1],a.crop((1023,0,1024,1024)).getextrema()[1],a.crop((0,0,1024,1)).getextrema()[1],a.crop((0,1023,1024,1024)).getextrema()[1]]})
        x=(i-1)%cols*cell;y=(i-1)//cols*(cell+28)
        thumb=im.resize((cell,cell),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
        d.text((x+10,y+cell+5),f'{action} W {i:02} / {dur}ms',fill=(16,45,35))
    sheet.save(out/f'{action}-contact.png')
report['technicalPass']=all(x['size']==(1024,1024) and x['mode']=='RGBA' and x['alphaRange']==(0,255) and x['shaMatchesGenerationRecord'] for x in report['checks']) and not report['duplicates']
(out/'technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(report['checks']),'technicalPass':report['technicalPass'],'duplicates':report['duplicates'],'touchingEdges':[x['file'] for x in report['checks'] if max(x['edgeAlphaMax'])>127]},ensure_ascii=False))

