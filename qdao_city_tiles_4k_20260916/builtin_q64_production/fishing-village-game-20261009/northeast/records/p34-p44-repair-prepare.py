from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return {'path':str(p),'sha256':sha(p),'role':role}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p34=B/'native/r06_c12_p34-v1.png';p44=B/'native/r06_c12_p44-v1.png';fish=B/'native/r06_c12_p13-v2.png'
layout=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png')
a=Image.open(p34).convert('RGB');z=Image.open(p44).convert('RGB')
assert a.size==z.size==(1254,1254)
combo=Image.new('RGB',(1254,2278));combo.paste(a.crop((0,0,1254,1139)),(0,0));combo.paste(z.crop((0,115,1254,1254)),(0,1139))
target=combo.crop((0,512,1254,1766));tp=B/'native/p34-p44-repair-target-v1.png';target.save(tp)
world=[48013,22925,49267,24179];overview=[v*1254/57344 for v in world]
guide=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,overview,Image.Resampling.BICUBIC);gp=B/'guides/p34-p44-repair-layout-only-v1.png';guide.save(gp)
fb=[550,385,1254,1254];fi=Image.open(fish).convert('RGB').crop(fb)
composite=Image.new('RGB',(1254+fi.width,1254),(238,238,238));composite.paste(guide,(0,0));composite.paste(fi,(1254,0));rp=B/'guides/p34-p44-repair-reference-v1.png';composite.save(rp)
source=[ref(p34,'top native source'),ref(p44,'bottom native source')]
td={'file':str(tp),'sha256':sha(tp),'purpose':'native edit target only','nativeSize':[1254,1254],'worldBox':world,'derivedFrom':source,'operation':'compose 1254x2278 native plane at source stride1024 with hard core cut1139; crop [0,512,1254,1766]; no rescale, feather or paint','compositeContribution':[{'source':str(p34),'sourceBox':[0,0,1254,1139],'targetBox':[0,0,1254,1139]},{'source':str(p44),'sourceBox':[0,115,1254,1254],'targetBox':[0,1139,1254,2278]}],'formalAccepted':False};write(str(tp)+'.derived.json',td)
gd={'file':str(gp),'sha256':sha(gp),'purpose':'exact coordinate layout-only; never final game pixels','size':[1254,1254],'worldBox':world,'overviewBox':overview,'derivedFrom':[ref(layout,'only authoritative global layout')],'operation':'Pillow EXTENT bicubic on exact world-mapped overviewBox','formalAccepted':False};write(str(gp)+'.derived.json',gd)
rd={'file':str(rp),'sha256':sha(rp),'purpose':'mechanical side-by-side reference only, never final game pixels','size':list(composite.size),'panels':[{'source':str(gp),'sourceBox':[0,0,1254,1254],'targetBox':[0,0,1254,1254],'role':'LEFT exact layout-only at same coordinate crop as target'},{'source':str(fish),'sourceBox':fb,'targetBox':[1254,0,1958,869],'role':'RIGHT 1:1 original blue-fish material/proportion only; not map placement'}],'derivedFrom':[ref(gp,'layout-only guide'),ref(fish,'native fish visual reference')],'operation':'native crop and opaque side-by-side paste, no resizing of fish; neutral unused background; guide itself layout-only','formalAccepted':False};write(str(rp)+'.derived.json',rd)
manifest={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worldBox':world,'overviewBox':overview,'topPatch':ref(p34,'p34 source'),'bottomPatch':ref(p44,'p44 source'),'target':ref(tp,'edit target'),'layoutGuide':ref(gp,'exact layout-only coordinate crop'),'combinedReference':ref(rp,'layout-only plus native fish-style reference'),'oldCoreBoundaryInTargetY':627,'guardBands':{'top':[0,0,1254,180],'bottom':[0,1074,1254,1254],'left':[0,0,180,1254]},'candidateBackPastePlan':[{'patch':'p34','repairSourceBox':[0,0,1254,742],'destinationBox':[0,512,1254,1254]},{'patch':'p44','repairSourceBox':[0,512,1254,1254],'destinationBox':[0,0,1254,742]}],'expectedNativeSize':[1254,1254],'resizeAllowed':False,'formalAccepted':False}
write(B/'records/p34-p44-repair-plan.json',manifest)
print(json.dumps({'target':str(tp),'layoutGuide':str(gp),'reference':str(rp),'worldBox':world,'overviewBox':overview}))

