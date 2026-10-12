from pathlib import Path
from PIL import Image
import sys,json,hashlib
from datetime import datetime,timezone
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
con=read(B.parent/'production-contract.json')
id='r06_c04_bench_right_bridge_v01_20261012';box=[2440,140,3694,1394];g=[box[0]+12288,box[1]+20480,box[2]+12288,box[3]+20480]
base=W/'final-v1/r06_c04.candidate.png';out=W/'guides'/(id+'.target.png');Image.open(base).crop(box).save(out)
write(str(out)+'.derivation.json',{'source':str(base),'sha256':sha(base),'cropBox':box,'method':'exact integer1254crop; no scaling or raster edits','guide':str(out),'guideSha256':sha(out),'globalNativeBox':g})
prompt='Use case: precise-object-edit. Output opaque1254x1254. IMAGE1 is the only actual close-up edit target; keep exact camera, crop, native scale. IMAGE2 is village identification only, IMAGE3 material reference only, IMAGE4 primary approved refined rounded Q Daoist style. Repair ONLY the broken right end of this existing wooden bench. Its main seat boards currently end in a jagged diagonal splice near the middle-right, followed by a dislocated narrow extension plank and a duplicate outside leg. Make the existing broad seat finish as one coherent rounded timber end with straight connected plank edges in the existing isometric direction. Remove the offset extra narrow plank and its duplicate outside leg, replacing them with the same nearby sandy ground and soft shadow. Keep the real supporting right bench leg directly beneath the main seat, existing blue cloth/back rail and upright, all remaining wood grain and sand exactly in their current positions. Preserve the whole blue cloth silhouette and scale; do not add arms, props, furniture or new legs. Keep bright warm daylight, natural rounded warm timber, refined material texture. No zoom-out, no complete village recreation, no buildings or lanterns. Seam repair only, no extra objects.'
pf=W/'prompts'/(id+'.prompt.txt');pf.write_text(prompt,encoding='utf-8');refs=[str(out),con['layoutReference'],con['detailStyleReference'],con['primaryStyleReference']]
write(W/'receipts'/(id+'.request.json'),{'id':id,'createdAt':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(pf),'referenced_image_paths':refs,'referenceRoles':['actual exact native bench right-end repair target','layout only','material only','primary approved style'],'referenceHashes':[sha(p) for p in refs],'globalNativeBox':g,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
print(json.dumps({'id':id,'target':str(out),'globalNativeBox':g}))
