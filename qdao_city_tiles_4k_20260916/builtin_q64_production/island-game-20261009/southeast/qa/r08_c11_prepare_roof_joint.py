from pathlib import Path
from PIL import Image
import json,hashlib,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid='r08_c11_roof_joint';ver='v01';origin=[2957,2413];world=[43917,31085,45171,32339];im=Image.new('RGB',(1254,1254));placements=[]
def paste(f,crop,dest,role):
 a=Image.open(f).convert('RGB').crop(crop);im.paste(a,dest);placements.append({'file':str(f),'sha256':sh(f),'sourceCrop':crop,'destination':dest,'role':role})
paste(R/'native/r08_c11_p34_v01.png',[0,480,1254,1139],[0,0],'upper wall and complete top gold curl; current core')
paste(R/'native/r08_c11_p44_v01.png',[0,115,1254,710],[0,659],'lower gold ridge and roof; current core')
paste(R/'native/r08_c11_p43_v02.png',[1024,115,1139,710],[0,659],'actual left neighboring core, outside right-column boundary')
paste(R/'tiles/r08_c12.candidate-v15.png',[0,2413,115,3667],[1139,0],'actual fixed east tile core edge; authoritative')
target=R/'guides/r08_c11_roof_joint.native-context-v01.png';assert not target.exists();im.save(target)
coord={'id':pid,'nativeGlobalBox':world,'coreGlobalBox':[world[0]+115,world[1]+115,world[0]+1139,world[1]+1139],'originInTile':origin,'layoutReferenceBox':[x*1254/57344 for x in world]}
wr(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sh(target),'operation':'Exact original-coordinate crop/paste repair guide spanning actual p34/p44 joint; no resize or RGB modifications.','placements':placements,'coordinate':coord,'usableAsFinalArt':False})
refs=[{'file':str(target),'sha256':sh(target),'role':'Full native same-coordinate repair TARGET spanning the complete gold scroll/ridge joint. Repair interior source break, keep true outer structural connections.'}]+rd(R/'references.json')
prompt='''Use case: precise-object-edit. Make ONE opaque native1254x1254 square by repairing image1 at exactly the same scale and framing. This is a complete gold-scroll and roof-ridge junction, not a narrow strip repair.
Image1 contains a bad horizontal source cut near localy659: the upper drawing of the gold cap/red ridge and downward gold hook is displaced from the lower drawing, making double gold edges and a shifted ornament. Rebuild the ENTIRE connected foreground gold scroll, gold cladding on the diagonal red ridge, lower sweeping gold hook, and their immediate red/blue contact as coherent complete objects. Keep the whole top gold spiral and one downward hook, one sequence of gold cap pieces and one continuous red ridge. Connect their outer silhouette, thickness and single shadow continuously, eliminate the doubled/scalloped cap at the interior cut, and let each gold piece remain whole. No horizontal seam, duplicated hook, extra cap or shift step.
The surrounding pale stone wall/recessed panel and paving are already in correct perspective; keep those shapes and material scale. The existing blue glazed barrel tiles below are also correct and must meet the red ridge coherently. Match the actual unchanged outer115 connection geometry, especially exact left/right and bottom connections. The wrong interior y659 boundary is NOT an immutable anchor: reconstruct through it. Internal position adjustments are allowed only as needed to make the whole object continuous, without adding/removing objects.
Image2 is sole full-map layout reference, image3 independent material reference, image4 approved Q Daoist painted style only (no UI/text/characters/night). Clean bright daylight, rounded elegant gold, red wood, blue roof, natural pale stone. Fine restrained paint texture; no blur, photoreal noise, glow, fake sharpening, new scratches or filter. Do not crop, zoom, rotate, rescale or move the view. Output single full square only.'''
pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists();pf.write_text(prompt,encoding='utf-8');wr(rf,{'createdAt':datetime.now(timezone.utc).isoformat(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':coord,'status':'prepared_not_submitted'})
wr(Q/'r08_c11-p34-p44-cut-review.json',{'status':'rectilinear_cuts_rejected_complete_object_repair_prepared','trials':[1024,1082,1139,1196,1254],'finding':'All inspected true overlap hard cuts retain a shifted gold cap/hook or roof contact, so cut relocation alone cannot repair the source mismatch. A1254 complete-object repair puts the bad cut at localy659, safely interior.','request':str(rf),'formalAccepted':False})
p=R/'progress-r08_c11.json';d=rd(p);d.update({'status':'submitting_whole_roof_joint_repair','currentPatch':pid,'inFlight':True});wr(p,d)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
