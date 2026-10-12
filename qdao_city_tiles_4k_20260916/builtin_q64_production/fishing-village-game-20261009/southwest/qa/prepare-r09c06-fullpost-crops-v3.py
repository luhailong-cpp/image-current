import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,datetime
Z=Path(__file__).resolve().parents[1]; source=Z/'qa/full-tile-r09_c06-context-native.png'; im=Image.open(source)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
items=[('a-complete-upper-posts',[260,-40,1514,1214]),('b-complete-center-post-upper',[1360,500,2614,1754]),('b-complete-center-post-lower',[1360,1524,2614,2778])]
for name,b in items:
 p=Z/'qa'/('repair-r09_c06-'+name+'-source-native-v3.png'); assert not p.exists(); box=[v+115 for v in b]; im.crop(box).save(p)
 rec={'file':p.as_posix(),'sha256':sha(p),'source':{'path':source.as_posix(),'sha256':sha(source)},'tileContextBox':b,'contextBox':box,'globalContextBox':[b[0]+20480,b[1]+32768,b[2]+20480,b[3]+32768],'dimensions':[1254,1254],'operation':'exact integer crop only','nativePixelsResampled':False}
 Path(str(p)+'.derivation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');records.append(rec)
report={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'native coordinate geometry and crop suggestions; no AI generation and no source status changes','source':{'path':source.as_posix(),'sha256':sha(source)},'crops':records,'objects':[{'id':'a-red-upper-post','tileXRange':[633,785],'naturalTop':'visible under sloped roof beam / square gold connector at tile y25..85','naturalBottom':'front counter top occlusion at tile y1160..1171','advice':'full visible red wood object only; preserve bracket/roof/counter as foreground occluders'},{'id':'a-rear-thin-post','tileXRange':[913,1024],'naturalTop':'under rear counter beam approx tile y820..880','naturalBottom':'front diagonal frame approx tile y1080..1150','advice':'full visible thin wood object and existing occluding support beam boundaries'},{'id':'b-center-long-post','tileXRange':[1904,2090],'capTopTileY':382,'woodTopTileY':[571,592],'footCollarTopTileY':[2592,2650],'footBottomTileY':2698,'advice':'retain existing healthy gold cap. Update complete shaft from curved underside of cap through foot using two native crops with 230px vertical overlap. Mask final object side contour and natural top/bottom; no mask edge across shaft.'}],'bOverlap':{'tileBox':[1360,1524,2614,1754],'pixels':230,'nextInput':'second patch guide should inherit first patch unchanged overlap before generation; match native overlap exactly in composition'},'visualVerification':['repair-r09_c06-a-upper-posts-measure-top-100pct.png','repair-r09_c06-a-upper-posts-measure-bottom-100pct.png','repair-r09_c06-b-centerpost-measure-top-100pct.png','repair-r09_c06-b-centerpost-measure-bottom-100pct.png']}
p=Z/'qa/repair-r09_c06-complete-post-coordinate-plan-v3.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(p),'sha256':sha(p),'crops':[{'path':r['file'],'sha256':r['sha256']} for r in records]}))
