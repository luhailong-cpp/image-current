from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
from PIL import Image
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B))
from native_pipeline import Pipeline
T=B/'r11_c07'; patch='p01_02'; attempt='layout-fix-20261013c-v01'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'pipeline/prompts/p01_02.recover-20261013b-v01.request.json';r=read(base)
guide=T/'guides/p01_02.layout-only.png'
pipeline=Pipeline('r11_c07')
left=pipeline.neighbor(1,2,'left')
top=pipeline.anchor(str(T/'pipeline/anchors/top-r10_c07-recover-20261013b-v01.png'),1,2,'top')
seed=Image.open(guide).convert('RGB');seed.paste(left[0],(0,0));seed.paste(top[0],(0,0))
sp=T/f'pipeline/guides/{patch}.{attempt}.continuity-seed.png';assert not sp.exists();seed.save(sp)
neighbors=[]
for obj,target,effective in [(left,[0,0,230,1254],[0,230,230,1254]),(top,[0,0,1254,230],[0,0,1254,230])]:
 q=obj[1];q.update(targetBox=target,effectiveTargetBox=effective);neighbors.append(q)
derivation={'file':str(sp),'sha256':sha(sp),'guide':str(guide),'guideSha256':sha(guide),'neighbors':neighbors,'operation':'explicit refinement guidance: exact selected left native and top anchor cropped/pasted onto existing coarse layout; not final art','sourceResampling':False,'gameArt':False,'allAcceptanceFalse':True}
sp.with_name(sp.name+'.derivation.json').write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefix=(T/f'pipeline/prompts/{patch}.{attempt}.content-prefix.txt').read_text(encoding='utf-8-sig')
prompt=prefix+'\n\n'+r['prompt'][r['prompt'].index('Use case:'):]
pp=T/f'pipeline/prompts/{patch}.{attempt}.prompt.txt';rp=T/f'pipeline/prompts/{patch}.{attempt}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),neighborSources=neighbors,preparedAtUtc=datetime.now(timezone.utc).isoformat(),explicitRefinementOf={'file':str(base),'sha256':sha(base)},cornerTreatment={'priority':'upper','pasteOrder':['left','upper'],'bothSourcesPresent':True,'blendingOrResampling':False,'visualReviewRequired':True})
r['references'][0]={'file':str(sp),'sha256':sha(sp),'role':'explicit refinement edit target: approved coarse layout plus exact corrected native left/top strips; not final art'}
r['referenced_image_paths']=[x['file'] for x in r['references']]
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'seed':str(sp),'correctedLeft':neighbors[0]['file'],'leftSha256':neighbors[0]['sha256']},ensure_ascii=False))

