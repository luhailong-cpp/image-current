from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,o):assert not Path(p).exists();Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
resume=read(T/'production-resume-20261012.json');base=resume['baseline'];north=T.parent/'r14_c13/candidate/r14_c13-4k-north-v6.png';a=Image.open(north).convert('RGB');b=Image.open(base['candidate']['path']).convert('RGB')
for name,x in [('north-mid-fixed-v2',1000),('north-right-fixed-v2',2000),('north-left-fixed-v2',0)]:
 old=read(R/({'north-mid-fixed-v2':'north-roof-mid-v1','north-right-fixed-v2':'north-roof-right-v1','north-left-fixed-v2':'north-wood-left-v1'}[name]+'.preparation.json'))
 anchor=R/(name+'-immutable-north.png');assert not anchor.exists();a.crop((x,2842,x+1254,4096)).save(anchor)
 target=R/(name+'-target.png');im=Image.new('RGB',(1254,1254));im.paste(a.crop((x,3196,x+1254,4096)),(0,0));im.paste(b.crop((x,0,x+1254,354)),(0,900));im.save(target)
 mask=R/(name+'-edit-region.png');im=Image.new('L',(1254,1254),0);ImageDraw.Draw(im).rectangle([0,900,1253,1253],fill=255);im.save(mask)
 prompt='''Edit ONLY input6, the LAST IMAGE, a native 1254x1254 close-up across an existing north/south tile boundary. Inputs1..3 give approved hand-painted style. Input4 is an EXACT immutable northern-neighbor crop, whose BOTTOM EDGE is the fixed visual anchor. Input5 is an editing mask: BLACK means do not edit; WHITE is the only editable southern region. Do not render the mask.
In last input6, rows0..899 are the immutable north and must be copied unchanged. ONLY rows900..1253, below the obvious horizontal material mismatch, may be repainted. The boundary y900 is NOT an object line. Continue the exact upper material colors, exposure, paint texture scale, directional grain and existing diagonal contours across y900 into the bottom354 rows. Current lower tiles/wood are too orange/dark and have a coarse texture jump; repaint them with the same softer illuminated cream-gold glaze / same timber grain already visible immediately above y900. It is essential to repair the LOWER region, never harmonize by recoloring the upper900 rows. Input4 is the immutable color authority.
Keep precise tile ribs, overlapping curves, timber edges and ALL outlines in place. No perspective change, no new tile, no new border, no blur strip. Extend each existing paint feature naturally across the boundary. Let the very bottom gradually retain the original composition, but the first160 rows BELOW y900 must directly match the north in color/material and connect its fine texture. Never draw a whole house or add text/characters/foliage. Output opaque native1254x1254 PNG, same crop, no resizing.'''
 pp=R/(name+'.prompt.txt');pp.write_text(prompt,encoding='utf-8');req={'prompt':prompt,'referenced_image_paths':[v['path'] for v in old['references']]+[str(anchor),str(mask),str(target)],'transparent_background':False};rp=R/(name+'.request.json');write(rp,req)
 prep={'id':name,'tile':'r15_c13','preparedAt':datetime.now(timezone.utc).isoformat(),'source':base['candidate'],'northSource':info(north),'northCrop':[x,3196,x+1254,4096],'southCrop':[x,0,x+1254,354],'sourceGeneratedSouthCrop':[0,900,1254,1254],'target':{**info(target),'size':[1254,1254]},'request':info(rp),'prompt':info(pp),'references':old['references']+[dict(info(anchor),role='immutable_native_north'),dict(info(mask),role='explicit_edit_region_mask')],'resampled':False,'status':'prepared_only_no_generation','actualModel':None,'actualQuality':None,'authorization':old['authorization']};write(R/(name+'.preparation.json'),prep)
print('Prepared three fixed-reference targets. No new generation yet.')
