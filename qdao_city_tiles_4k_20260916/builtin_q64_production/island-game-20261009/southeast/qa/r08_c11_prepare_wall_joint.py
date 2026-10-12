from pathlib import Path
from PIL import Image
import json,hashlib,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid='r08_c11_wall_joint';ver='v01';origin=[2445,1933];world=[43405,30605,44659,31859];im=Image.new('RGB',(1254,1254));placements=[]
def place(file,srcOrigin,domain,role):
 x0=max(origin[0],domain[0]);y0=max(origin[1],domain[1]);x1=min(origin[0]+1254,domain[2]);y1=min(origin[1]+1254,domain[3])
 if x0>=x1 or y0>=y1:return
 crop=[x0-srcOrigin[0],y0-srcOrigin[1],x1-srcOrigin[0],y1-srcOrigin[1]];dest=[x0-origin[0],y0-origin[1]];im.paste(Image.open(file).convert('RGB').crop(crop),dest);placements.append({'file':str(file),'sha256':sh(file),'sourceCrop':crop,'destination':dest,'role':role})
place(R/'native/r08_c11_p33_v04.png',[1933,1933],[1933,1933,3187,3187],'complete left wall/paving target; current proposed whole close-up')
place(R/'native/r08_c11_p34_v01.png',[2957,1933],[3072,1933,4211,3187],'actual right wall core plus upper native halo')
for fn in rd(R/'selected-native-r08_c11.json')['selected'].values():
 f=R/'native'/fn;g=rd(Path(str(f)+'.generation.json'))['coordinate']['nativeGlobalBox'];o=[g[0]-40960,g[1]-28672];place(f,o,[o[0]+115,o[1]+115,o[0]+1139,o[1]+1139],'actual selected native core')
for z in rd(R/'selected-overlays-r08_c11.json')['overlays']:place(Path(z['file']),z['originInTile'],z['destinationBox'],'actual selected roof joint core')
target=R/'guides'/f'{pid}.native-context-{ver}.png';assert not target.exists();im.save(target)
coord={'id':pid,'nativeGlobalBox':world,'coreGlobalBox':[world[0]+115,world[1]+115,world[0]+1139,world[1]+1139],'originInTile':origin,'layoutReferenceBox':[x*1254/57344 for x in world]}
wr(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sh(target),'operation':'Original-coordinate crop/paste of full rendered natives and current selected cores, no RGB edits or resampling; true bad boundary x3072 is now interior local627. Guide only.','placements':placements,'coordinate':coord,'usableAsFinalArt':False})
refs=[{'file':str(target),'sha256':sh(target),'role':'Complete rendered wall object edit target. Bad x627 source boundary is interior and must be reconstructed; outer230 wall/paving are endpoint anchors.'}]+rd(R/'references.json')
prompt='''Use case: precise-object-edit. Output ONE opaque native1254x1254 square editing image1 at the exact same crop, scale and camera. Repair the complete broad pale stone wall panel and its lower bevel/base/contact shadow across the center of the image.
At localx627 there is a bad vertical source cut: the long single diagonal wall lower bevel suddenly steps upward, the base depth changes, and its floor shadow breaks. This is NOT architecture. Reconstruct the entire wall panel, ONE continuous narrow recessed bevel with its fine light lower rim, the base and the whole cast/contact shadow as one uninterrupted perspective object. The complete wall-floor contact must connect the actual left and right endpoints smoothly, with no step, jog, double line or rectangular source boundary. Adjust the interior line and panel geometry as a whole; do not merely paint a tiny bridge across the bad cut or keep the old center kink. Rebuild the neighboring paving as needed so every stone joint meets consistently.
LEFT230 and RIGHT230 are the true endpoint/material anchors. TOP115 wall/coping context and BOTTOM230 paving/foreground are the true connections. Preserve their single outline connections. The interior wrong x627 boundary is explicitly editable and must disappear. Keep the foreground gold-red roof scroll silhouette at the right/lower edge, its one complete curl, and existing lower-left foliage unchanged in size, position and number. No new ornament or duplicated curl. Preserve the wall top only where already visible in image1; no new top coping, column, ball finial, divider or rail. No new objects or layout expansion. This is a native close-up, not the complete island.
Image2 full-map layout only; image3 independent natural-stone material; image4 approved refined Q Daoist painting style only, without text/UI/people/night. Crisp bright daylight, rounded painted forms, pale natural stone, restrained fine brush texture matching the surrounding pixels. No blur, extra scratches, noise, sharpness filter, altered view or rescale. Single full square only.'''
pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists();pf.write_text(prompt,encoding='utf-8');wr(rf,{'createdAt':datetime.now(timezone.utc).isoformat(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':coord,'status':'prepared_not_submitted'})
p=R/'progress-r08_c11.json';d=rd(p);d.update({'status':'submitting_complete_wall_joint','currentPatch':pid,'inFlight':True});wr(p,d)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
