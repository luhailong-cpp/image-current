from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name='r12_c13_deck_corner_whole_v03';g=R/'guides'/f'{name}.png';assert not g.exists();body=R/'native/r12_c13_deck_corner_whole_v02.png';im=Image.open(body).convert('RGB')
box=(230,230,530,1060);im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(35)),(230,230));im.save(g)
write(Path(str(g)+'.generation.json'),{'file':g.as_posix(),'sha256':sha(g),'width':1254,'height':1254,'tileRelativeOrigin':[-115,2452],'operation':'native detailed edit reference; soften only complete affected intervening board faces for redraw; not final','derivedFrom':[{'file':body.as_posix(),'sha256':sha(body),'role':'fixed accepted west230 and complete physical end joints/body'}],'guideOnlySoftenedRegion':box,'usableAsFinalArt':False})
prompt="""Use case: precise-object-edit. Restore the softened region in image 1 into the same complete native 1254-square pier artwork. The left 230 pixels and every sharp surrounding region must stay fixed at the existing coordinates. Last three references give layout, materials and style only.
The blurred rectangle is the COMPLETE left portions of the affected physical boards and deck edge beam, not a new object. Continue each sharp black plank groove entering from the left straight through the blurred region until it meets the actual sharp plank end joint on the right. These grooves must CONNECT to the end joint: no vertical rectangular boundary at x230, no line ending mid-plank, no extra groove from an obsolete layout. Restore rounded board bevels, restrained golden painted wood grain and shading within the same boards.
The gold dock beam enters from the sharp left near y900..1050: continue its exact solid top face and lower shaded edge across the softened region to the existing right beam. A coherent timber, no separate panels or steps. Preserve water, boat and posts. One opaque square, exact same crop, no text, UI or comparison."""
pp=R/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8');refs=[{'file':g.as_posix(),'sha256':sha(g),'role':'native edit target; soft complete board portions require coherent repaint, all sharp geometry fixed'}]+read(R/'references.json');write(R/'prompts'/f'{name}.request.json',{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'tileRelativeOrigin':[-115,2452],'resumeAuthorization':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','dispatchStatus':'prepared_not_submitted'})
d=read(R/'production-resume-right-sol-20261012.json');d.setdefault('preparedRequests',[]).append({'id':name,'request':str(R/'prompts'/f'{name}.request.json'),'promptSha256':sha(pp),'guideSha256':sha(g),'dispatchStatus':'prepared_not_submitted'});write(R/'production-resume-right-sol-20261012.json',d)
print(json.dumps({'name':name,'guide':g.as_posix(),'sha256':sha(g)}))

