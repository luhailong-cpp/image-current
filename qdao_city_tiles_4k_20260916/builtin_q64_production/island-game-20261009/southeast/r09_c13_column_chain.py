"""Whole column geometry from lower fixed foot upward, exact native crops only."""
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,progress
import sys,json,shutil
mode,key=sys.argv[1:3]
version=sys.argv[4] if mode=='ingest' and len(sys.argv)>4 else (sys.argv[3] if mode=='prepare' and len(sys.argv)>3 else 'v01')
name=f'r09_c13_column_{key}_{version}'
box={'lower':[1100,2445,2354,3699],'upper':[1100,1421,2354,2675]}[key]
target=ROOT/'guides'/f'{name}.native-target.png'; pf=ROOT/'prompts'/f'{name}.prompt.txt';rf=ROOT/'prompts'/f'{name}.request.json'
candidate=ROOT/'tiles/r09_c13.candidate.png'
if mode=='prepare':
    assert not target.exists() and not rf.exists()
    im=Image.open(candidate).convert('RGB').crop(box)
    sources=[{'file':str(candidate),'sha256':sha(candidate),'sourceCrop':box}]
    if key=='upper':
        lower=ROOT/'native/r09_c13_column_lower_v01.png'
        im.paste(Image.open(lower).crop((0,0,1254,230)),(0,1024))
        sources.append({'file':str(lower),'sha256':sha(lower),'sourceCrop':[0,0,1254,230],'destination':[0,1024],'role':'real lower native overlap, authoritative post axis'})
    im.save(target)
    write(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'operation':'exact native crop/paste; no resizing','derivedFrom':sources})
    desc=('Rebuild the entire long wooden upright from the intact bottom section UPWARD. The current image has a horizontal assembly step at y627. The BOTTOM 115 rows are the sole correct wooden-post geometry anchor: both side edges and the bright vertical bevel there define the true straight post. Make the entire post above it the same width and aligned with that bottom anchor; remove the horizontal notch. The TOP wooden post section IS allowed to change to match the bottom. Do NOT attempt to preserve the current wrong upper wood width, upper contour, or upper bevel. The top wood will be used as the anchor for another upper tile. Keep the fixed bottom 115 rows exactly unchanged, including post, grain and surrounding garden/stone. Preserve all golden chime shape, nearby plants and stone. The post has no new cap, beam, ornament or base in this crop.' if key=='lower' else 'Rebuild the complete cap and beam/post junction as one coherent object. The BOTTOM 230 rows contain the corrected native lower post and are the authoritative geometry anchor. The cap and the entire post above must match that straight post axis, width, side contours and bright bevel. Resize the existing cap BODY only by redrawing its contour if needed, keeping its type, height and placement; do not retain the old wrong wider upper post. Continue the diagonal upper beam and gold top face into the post continuously; remove the horizontal break at y627. Keep all existing beams, chimes, foliage and flowers; no new objects. The TOP outer115 rows, left/right outer115 columns and bottom230 rows must remain unchanged.')
    if key=='lower' and version=='v02':
        desc='The LOWER HALF of the wooden post, below the horizontal seam y627, is already correct and MUST remain pixel-identical. Only correct the UPPER half of the post above y627. Move its left contour about 23 pixels LEFT so the whole post left edge is x519, and move its right contour about 8 pixels LEFT so the whole post right edge is x882; move the bright bevel to x746. These are exact image1 coordinates. The correct bottom half must NOT be widened or moved right. Extend the unchanged lower post straight upward to those same x positions, with its same width, wood grain, dark front face and bright right face. Continue the existing diagonal wood beam into the post at its present height, without adding anything. Adjust only the narrow strips of foliage exposed or covered by the corrected upper post edges. The entire lower half, chime, leaves, stone, background, fixed bottom and side borders stay identical. The uppermost WOOD is allowed to change because the next upper patch will inherit it; do not preserve the incorrect upper width. Output must not merely smooth the horizontal seam by copying the wrong upper shape downward.'
    prompt='Use case: precise-object-edit. Edit image1 at its exact native 1254x1254 square crop. '+desc+' Redraw the complete visible existing wooden structure where needed, not a thin correction band. Keep the left and right outermost115 columns, all non-wood top-border foliage, and all non-wood background in the central region unchanged. Crisp straight post contours, matching warm wood grain and continuous sunlight, no soft blend, blur, feather, image warp, camera shift or pixel scaling. Image2 is an unscaled long crop of the entire existing visible post for object identity only; it contains old alignment defects and must not override the bottom anchor or be fit into the square. Last three references are full island layout, independent material detail and approved Q Daoist painting style. Daylight; no UI, text or characters. Return a single opaque native square.'
    pf.write_text(prompt,encoding='utf-8')
    whole=ROOT/'guides/r09_c13_joint2_v03.whole-visible-post.png'
    refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET, bottom-native post geometry is authoritative'},{'file':str(whole),'sha256':sha(whole),'role':'whole visible upright identity, old defects not geometry authority'}]+read(ROOT/'references.json')
    write(rf,{'promptPath':str(pf),'promptSha256':sha(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'nativeBoxRelativeToTile':box,'intendedSourceCrop':[115,115,1139,1139],'intendedDestinationBox':[box[0]+115,box[1]+115,box[0]+1139,box[1]+1139]})
    progress(status='column_rebuild_prepared',currentPatch=name)
    print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
elif mode=='ingest':
    src=Path(sys.argv[3]);out=ROOT/'native'/f'{name}.png';assert not out.exists()
    req=read(rf);receipt=read(ROOT/'receipts'/f'{name}.json')
    assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==pf.read_text(encoding='utf-8')
    assert receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]
    im=Image.open(src);assert im.size==(1254,1254);shutil.copy2(src,out)
    rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress-r09_c13.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool has no model/quality selectors or disclosed actual values.','prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'coordinate':{'tile':'r09_c13','nativeBoxRelativeToTile':box,'intendedSourceCrop':req['intendedSourceCrop'],'intendedDestinationBox':req['intendedDestinationBox']},'status':'pending_visual_review'}
    write(Path(str(out)+'.generation.json'),rec)
    q=Image.open(target).convert('RGB');q.paste(im.crop((115,115,1139,1139)),(115,115));qp=ROOT/'qa'/f'{name}.hard-insert.png';q.save(qp)
    write(Path(str(qp)+'.generation.json'),{'file':str(qp),'sha256':sha(qp),'operation':'exact core paste, no blend/resize','derivedFrom':[{'file':str(target),'sha256':sha(target),'role':'perimeter anchors'},{'file':str(out),'sha256':sha(out),'sourceCrop':[115,115,1139,1139],'destination':[115,115]}]})
    progress(status='column_rebuild_received',currentPatch=name,generatedNativeCount=len(list((ROOT/'native').glob('r09_c13_*.png'))))
    print(json.dumps({'file':str(out),'sha256':sha(out),'qa':str(qp)}))
