from produce import *
tile=sys.argv[1];records=[json.loads(p.read_text()) for p in (ROOT/'native').glob('*.generation.json')]; selected=[r for r in records if r.get('selected') and r['tile']==tile]
assert len(selected)==16
(ROOT/'candidates').mkdir(exist_ok=True);(ROOT/'qa').mkdir(exist_ok=True)
canvas=Image.new('RGB',(4096,4096));sources=[]
for r in selected:
    pr,pc=int(r['patch'][1:3]),int(r['patch'][4:6]);im=Image.open(r['file']);canvas.paste(im.crop((115,115,1139,1139)),((pc-1)*1024,(pr-1)*1024));sources.append({'file':r['file'],'sha256':r['sha256'],'sourceBox':[115,115,1139,1139],'destination':[(pc-1)*1024,(pr-1)*1024]})
p=ROOT/'candidates'/f'{tile}-4096-v1.png';canvas.save(p);canvas.resize((1254,1254)).save(ROOT/'qa'/f'{tile}-preview-v1.png')
write(ROOT/'candidates'/f'{tile}-4096-v1.manifest.json',{'file':p.as_posix(),'sha256':sha(p),'dimensions':[4096,4096],'method':'unaltered 1024 core crops, hard joins, no resizing native pixels','sources':sources,'status':'full_coverage_pending_internal_and_external_qa'})
print(p)
