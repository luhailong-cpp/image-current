"""Native complete-joint repairs; exact crop/paste only, never resize output."""
from pathlib import Path
from PIL import Image
import sys,json,shutil
from workflow import ROOT,read,write,sha,now,progress

mode=sys.argv[1]
name='r09_c13_joint2_v03'
box=[1100,1421,2354,2675]
target=ROOT/'guides'/f'{name}.native-target.png'
whole=ROOT/'guides'/f'{name}.whole-visible-post.png'
candidate=ROOT/'tiles/r09_c13.candidate.png'
pf=ROOT/'prompts'/f'{name}.prompt.txt'
reqpath=ROOT/'prompts'/f'{name}.request.json'
if mode=='prepare':
    assert not reqpath.exists()
    for p,b in [(target,box),(whole,[1100,1400,2354,4096])]:
        assert not p.exists();Image.open(candidate).crop(b).save(p)
        write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'exact native crop without resize','derivedFrom':[{'file':str(candidate),'sha256':sha(candidate),'sourceCrop':b}]})
    prompt='''Use case: precise-object-edit. Rebuild the existing broken wooden post-and-crossbeam junction in image 1 as one coherent object. Output exactly the same square 1254x1254 framing, no zoom or layout shift.
Image 1 is the actual native EDIT TARGET. The full timber cap, upper beam/post joint, both faces of the post and background around them are included. There is a stitching defect at y627: the diagonal beam top suddenly ends and the post right edge jumps sideways. Redraw the WHOLE existing junction within the full central 1024x1024 core (x115..1139,y115..1139), including the cap if needed, to make the complete post and both connected beams structurally continuous. Do not just patch a thin seam band. Make the upper post align with the fixed lower post section visible at the bottom of the image; preserve the lower section width, right contour and bright bevel location as exact connection anchors. The post must have continuous straight vertical outer edges and bevel, not a taper that merely hides the mismatch. Continue the diagonal gold top surface to the wooden post naturally. Its visible straight top edge must not terminate at a horizontal line.
The outermost 115 pixels on all four sides are fixed native connection anchors: keep their geometry, colors, leaf positions, wood grain and silhouettes pixel-identical. All beam and post edges must meet the unchanged border without a step. Preserve the exact existing chime, surrounding foliage, small white flowers, post cap type and warm daylight. No new objects, no added ornament, no missing flowers or flattened leaves. Do not blur, feather, warp, shift, enlarge or rescale the image.
Image 2 is an UNRESIZED tall native crop of the entire currently visible post and adjacent structure from the same tile, for geometry only. It contains existing stitch defects; do not copy those defects. Do not squeeze or fit that tall reference into the square target. Last three images are, respectively, sole full island layout, independent material/architecture detail, and approved Daoist Q painting style only. Keep the existing scene and bright rounded clean daylight style; no UI, text, people, extra trees, dark lighting or changes to map layout. Return one opaque square image.'''
    pf.write_text(prompt,encoding='utf-8')
    refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET, native full joint with fixed 115px perimeter'},{'file':str(whole),'sha256':sha(whole),'role':'unscaled whole visible post geometry reference, not a target canvas'}]+read(ROOT/'references.json')
    for r in refs:assert sha(Path(r['file']))==r['sha256']
    write(reqpath,{'promptPath':str(pf),'promptSha256':sha(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'nativeBoxRelativeToTile':box,'intendedSourceCrop':[115,115,1139,1139],'intendedDestinationBox':[1215,1536,2239,2560]})
    progress(status='native_joint_rebuild_prepared',currentPatch=name,lastError=None)
    print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
elif mode=='ingest':
    src=Path(sys.argv[2]);out=ROOT/'native'/f'{name}.png';assert not out.exists()
    receipt=read(ROOT/'receipts'/f'{name}.json');req=read(reqpath)
    assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==pf.read_text(encoding='utf-8')
    assert receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]
    im=Image.open(src);assert im.size==(1254,1254)
    shutil.copy2(src,out)
    rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress-r09_c13.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin tool exposes no model or quality selector or returned model/quality.','prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'coordinate':{'tile':'r09_c13','nativeBoxRelativeToTile':box,'intendedSourceCrop':req['intendedSourceCrop'],'intendedDestinationBox':req['intendedDestinationBox']},'status':'pending_visual_review'}
    write(Path(str(out)+'.generation.json'),rec)
    q=Image.open(target).convert('RGB');q.paste(im.crop((115,115,1139,1139)),(115,115));qp=ROOT/'qa'/f'{name}.hard-insert.png';q.save(qp)
    write(Path(str(qp)+'.generation.json'),{'file':str(qp),'sha256':sha(qp),'operation':'exact core paste, no blend/resize','derivedFrom':[{'file':str(target),'sha256':sha(target),'role':'perimeter anchors'},{'file':str(out),'sha256':sha(out),'sourceCrop':[115,115,1139,1139],'destination':[115,115]}]})
    progress(status='native_joint_rebuild_received',currentPatch=name,generatedNativeCount=len(list((ROOT/'native').glob('r09_c13_*.png'))))
    print(json.dumps({'file':str(out),'sha256':sha(out),'qa':str(qp)}))
