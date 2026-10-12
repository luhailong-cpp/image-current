from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-resume-sol-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name='r12_c13_deck_corner_whole_v01';g=R/'guides'/f'{name}.png';assert not g.exists()
vs=read(R/'progress-r12_c13.json')['selectedVersions'];vs.update({'31':'v02','41':'v01'})
reg=(-115,2452,1139,3706);im=Image.new('RGB',(1254,1254));src=[];placements=[]
for row in [3,4]:
 for col in [1,2]:
  rc=f'{row}{col}';p=R/'native'/f'r12_c13_p{rc}_{vs[rc]}.png'
  own=((col-1)*1024,(row-1)*1024,col*1024,row*1024);b=(max(own[0],reg[0]),max(own[1],reg[1]),min(own[2],reg[2]),min(own[3],reg[3]))
  if b[2]>b[0] and b[3]>b[1]:
   crop=(b[0]-own[0]+115,b[1]-own[1]+115,b[2]-own[0]+115,b[3]-own[1]+115);dest=(b[0]-reg[0],b[1]-reg[1]);im.paste(Image.open(p).convert('RGB').crop(crop),dest);src.append({'file':p.as_posix(),'sha256':sha(p),'role':'registered native body features; rejected base retained for accepted geometry only'});placements.append({'source':p.as_posix(),'sourceCrop':crop,'destination':dest,'resampled':False})
w=R/'tiles/r12_c12.candidate-sol-20261012-v01.png';crop=(3981,2452,4096,3706);im.paste(Image.open(w).convert('RGB').crop(crop),(0,0));src.append({'file':w.as_posix(),'sha256':sha(w),'role':'exact accepted west outer115 native-derived core authority'});placements.append({'source':w.as_posix(),'sourceCrop':crop,'destination':[0,0],'resampled':False})
im.save(g);write(Path(str(g)+'.generation.json'),{'file':g.as_posix(),'sha256':sha(g),'width':1254,'height':1254,'operation':'exact registered source crop/paste only; guide not final','tileRelativeOrigin':[-115,2452],'derivedFrom':src,'placements':placements,'usableAsFinalArt':False})
prompt="""Use case: precise-object-edit. Edit image 1 into the SAME exact 1254-square native crop of a hand-painted daylight golden wood pier corner. Last three references are layout, material and painting style only. Preserve all outer 115 pixels, all blue water, the wooden boat side at lower-right and all real dock posts exactly. This is a registered whole physical wood assembly crossing two tile patch rows.
Repair the complete floorboard-to-perimeter-beam structure. At the left outer-strip boundary around x115,y540 a long board groove is offset from the current inner groove around y490. Also the broad dock-edge beam has two offset profiles around the left outer-strip boundary near y1000. Reconstruct the whole affected board and beam interior, not a thin scratch or faded blending patch. Make one physically valid plank end connection around x350: a restrained perpendicular end seam must join the adjacent real long board boundaries across the entire board width. The offset entering grooves must meet this seam cleanly as T junctions. Every long groove must enter and leave at its frozen boundary endpoint or close at a real full-width end joint. No floating lines or disappearing endpoints.
Continue the thick dock-edge timber from the exact left outline naturally to the exact existing right outline, one coherent solid beam with a consistent gold top face and shaded vertical face. Preserve the boat interior and posts below. Keep warm painted wood grain and daylight, no extra timbers, props, new boat or water area. Output one complete opaque square at the same crop and scale. No text, panel or UI."""
pp=R/'prompts'/f'{name}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
refs=[{'file':g.as_posix(),'sha256':sha(g),'role':'registered complete physical deck corner edit target; preserve outer115'}]+read(R/'references.json')
write(R/'prompts'/f'{name}.request.json',{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'tileRelativeOrigin':[-115,2452],'dispatchStatus':'prepared_not_submitted','resumeAuthorization':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
d=read(R/'production-resume-right-sol-20261012.json');d.setdefault('preparedRequests',[]).append({'id':name,'request':str(R/'prompts'/f'{name}.request.json'),'promptSha256':sha(pp),'guideSha256':sha(g),'dispatchStatus':'prepared_not_submitted'});write(R/'production-resume-right-sol-20261012.json',d)
print(json.dumps({'name':name,'guide':g.as_posix(),'prompt':pp.as_posix(),'tileRelativeOrigin':[-115,2452]}))

