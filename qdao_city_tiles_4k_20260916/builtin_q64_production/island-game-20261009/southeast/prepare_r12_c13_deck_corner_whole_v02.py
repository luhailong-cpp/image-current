from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name='r12_c13_deck_corner_whole_v02';g=R/'guides'/f'{name}.png';assert not g.exists();body=R/'native/r12_c13_deck_corner_whole_v01.png';im=Image.open(body).convert('RGB');src=[{'file':body.as_posix(),'sha256':sha(body),'role':'native coherent object edit body; frozen endpoints replaced'}];places=[{'source':body.as_posix(),'sourceCrop':[0,0,1254,1254],'destination':[0,0]}]
p34=R/'native/r12_c12_p34_v02.png';p44=R/'native/r12_c12_p44_v02.png';overlay=R/'native/r12_c12_board_end_joint_v01.png';candidate=R/'tiles/r12_c12.candidate-sol-20261012-v01.png'
for p,c,dest in [(p34,(1024,519,1254,1139),(0,0)),(p44,(1024,115,1254,749),(0,620)),(overlay,(1024,775,1254,1139),(0,0)),(candidate,(3981,2452,4096,3706),(0,0))]:
 im.paste(Image.open(p).convert('RGB').crop(c),dest);src.append({'file':p.as_posix(),'sha256':sha(p),'role':'accepted exact west registered overlap; core candidate final precedence'});places.append({'source':p.as_posix(),'sourceCrop':c,'destination':dest,'resampled':False})
old=R/'guides/r12_c13_deck_corner_whole_v01.png';oi=Image.open(old).convert('RGB')
for c,dest in [((230,0,1254,115),(230,0)),((1139,115,1254,1254),(1139,115)),((230,1139,1139,1254),(230,1139))]:
 im.paste(oi.crop(c),dest);places.append({'source':old.as_posix(),'sourceCrop':c,'destination':dest,'resampled':False})
src.append({'file':old.as_posix(),'sha256':sha(old),'role':'exact registered north east and lower accepted boundary source guide; pixel sources in its trace'})
im.save(g);write(Path(str(g)+'.generation.json'),{'file':g.as_posix(),'sha256':sha(g),'width':1254,'height':1254,'tileRelativeOrigin':[-115,2452],'operation':'exact native full-body and accepted west 230 plus frozen boundary crop/paste guide only','derivedFrom':src,'placements':places,'usableAsFinalArt':False})
prompt="""Use case: precise-object-edit. Edit image 1 into the SAME exact 1254-square native crop of a hand-painted daylight golden wood pier corner. Last three references are layout, material and painting style only.
The entire LEFT 230-pixel strip is accepted original artwork and MUST REMAIN EXACTLY UNCHANGED. Keep the rightmost 115, topmost 115 and bottommost 115 pixels unchanged too. Do not move any groove or edge endpoint in those regions. Only the interior can change.
Repair the COMPLETE physical floorboard assembly where the left 230px strip meets the interior: entering plank grooves have different spacings. Around x400 create one real restrained perpendicular plank end seam extending fully from the upper long boundary near y130 to the lower long boundary near y760. Every offset groove entering from the left or right must meet this end seam cleanly as a T. Keep the long grooves at their frozen edge endpoints; do not turn them into fading scratches or shift the frozen strip to match the interior. This is a legitimate end joint across complete planks, no metal or decorative frame.
Also smoothly rebuild the entire broad dock perimeter beam in the interior from its exact left fixed gold top-face and lower shadow outline to its exact right outline. One continuous solid beam, no dead ends. Preserve boat interior, support posts, water, color, scale and painted grain. Opaque one square, no panels, no text or UI."""
pp=R/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
refs=[{'file':g.as_posix(),'sha256':sha(g),'role':'native whole-object edit target; first230 exact accepted west fixed, other outer115 fixed'}]+read(R/'references.json')
write(R/'prompts'/f'{name}.request.json',{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'tileRelativeOrigin':[-115,2452],'resumeAuthorization':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','dispatchStatus':'prepared_not_submitted'})
d=read(R/'production-resume-right-sol-20261012.json');d.setdefault('preparedRequests',[]).append({'id':name,'request':str(R/'prompts'/f'{name}.request.json'),'promptSha256':sha(pp),'guideSha256':sha(g),'dispatchStatus':'prepared_not_submitted'});write(R/'production-resume-right-sol-20261012.json',d)
print(json.dumps({'name':name,'guide':g.as_posix(),'sha256':sha(g)}))

