from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import hashlib,json,sys,datetime
B=Path(__file__).resolve().parent.parent
patch,topname,leftname=sys.argv[1:4]
assert patch in ('r06_c12_p24','r06_c12_p34','r06_c12_p44')
cp=B/'records/r06_c12.coordinates.json';coords=json.loads(cp.read_text(encoding='utf-8-sig'));c=next(x for x in coords['patches'] if x['id']==patch)
layout=Path(coords['references'][0]['path']);top=B/'native'/topname;left=B/'native'/leftname
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,c['overviewBox'],Image.Resampling.BICUBIC)
li=Image.open(left).convert('RGB');ti=Image.open(top).convert('RGB')
diff=ImageChops.difference(li.crop((1024,0,1254,230)),ti.crop((0,1024,230,1254)))
im.paste(li.crop((1024,0,1254,1254)),(0,0));im.paste(ti.crop((0,1024,1254,1254)),(0,0))
p=B/'records'/(patch+'-layout-native-guide-v1.png');assert not p.exists();im.save(p)
d={'file':str(p),'sha256':sha(p),'purpose':'exact coordinate layout-only guide with native top/left anchors, not final art','coordinates':c,'nativeSize':[1254,1254],'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'derivedFrom':[{'path':str(layout),'sha256':sha(layout),'operation':'layout-only crop/resample from exact overviewBox'},{'path':str(left),'sha256':sha(left),'generationRecord':str(left)+'.generation.json','operation':'1:1 crop [1024,0,1254,1254] to left [0,0,230,1254]'},{'path':str(top),'sha256':sha(top),'generationRecord':str(top)+'.generation.json','operation':'1:1 crop [0,1024,1254,1254] to top [0,0,1254,230], top wins shared corner'}],'overlapCornerConflict':{'rgbMeanAbsoluteDifference':ImageStat.Stat(diff).mean,'equal':diff.getbbox() is None,'note':'sources are candidates; corner compatibility not accepted'},'formalAccepted':False}
Path(str(p)+'.derived.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'path':str(p),'cornerConflict':d['overlapCornerConflict']}))

