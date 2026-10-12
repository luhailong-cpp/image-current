"""One full native tall-column attempt; no resizing is permitted on output."""
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,progress
import sys,json,shutil
name='r09_c13_full_column_v01'; target=ROOT/'guides'/f'{name}.native-target.png'
pf=ROOT/'prompts'/f'{name}.prompt.txt';rf=ROOT/'prompts'/f'{name}.request.json'
if sys.argv[1]=='prepare':
    assert not target.exists() and not rf.exists()
    image=Image.new('RGB',(1536,3835));sources=[]
    specs=[(ROOT/'tiles/r09_c13.candidate.png',[1000,1400,2536,4096],[0,0]),(ROOT/'native/r10_c13_p12_v01.png',[91,115,1139,1254],[0,2696]),(ROOT/'native/r10_c13_p13_v01.png',[115,115,603,1254],[1048,2696])]
    for p,c,d in specs:
        image.paste(Image.open(p).convert('RGB').crop(c),tuple(d));sources.append({'file':str(p),'sha256':sha(p),'sourceCrop':c,'destination':d})
    image.save(target);write(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'width':1536,'height':3835,'operation':'exact native coordinate crops and hard paste; no resize or painting','derivedFrom':sources,'nativeBoxRelativeToR09C13':[1000,1400,2536,5235]})
    prompt='''Use case: precise-object-edit. Image1 is a FULL NATIVE PORTRAIT CROP, exactly 1536 pixels wide by 3835 pixels tall, showing one complete existing timber post from cap to stepped foot, its connecting beams, nearby chimes, stone and garden. Preserve this exact pixel size and framing; do not make a square or scale any part.
Repair the TWO existing horizontal stitching defects through this one wooden post at image y648 and y1672. Rebuild the whole post as one continuous timber object from its existing cap at the top to its existing wooden foot at the bottom, preserving its identity, approximate outline, grain, light, beam connections and foot. Both sides of the post and its bright vertical bevel must be continuous with no horizontal steps or sudden color changes. The upper diagonal beam gold top face must reach and join the post continuously. It currently stops abruptly at a stitching line. Keep the other existing connected beams and chimes intact. Preserve the solid wooden foot, no extra pedestal, carving or ornament.
Keep every pixel outside the timber structure unchanged, especially every plant, flower, stone wall, ground joint, shadow and the entire outer 115-pixel perimeter on all four sides. Repair within the full object extent, without trying to hide defects with blurry bands. Do not add objects, move the post, turn wood into stone, change view angle, stretch, sharpen artificially, blur, feather, or zoom. This tall crop already contains the whole object and all surrounding native connection boundaries, so no outside invented geometry is needed. The last three images are full island layout, independent materials detail, and Daoist Q painting style references only. Existing bright clean daylight, no characters, text or UI. Return one opaque portrait with the SAME 1536x3835 pixel dimensions.'''
    pf.write_text(prompt,encoding='utf-8');refs=[{'file':str(target),'sha256':sha(target),'role':'EDIT TARGET, whole timber post with all native surrounding boundaries'}]+read(ROOT/'references.json')
    write(rf,{'promptPath':str(pf),'promptSha256':sha(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'requestedPixels':[1536,3835],'nativeBoxRelativeToR09C13':[1000,1400,2536,5235],'sizeAcceptance':'Returned dimensions must match native coordinates; no upscale/stretch allowed.'})
    print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))
elif sys.argv[1]=='ingest':
    src=Path(sys.argv[2]);out=ROOT/'native'/f'{name}.png';assert not out.exists();req=read(rf);receipt=read(ROOT/'receipts'/f'{name}.json')
    assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==pf.read_text(encoding='utf-8')
    shutil.copy2(src,out)
    with Image.open(out) as im: size=list(im.size);fmt=im.format
    rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress-r09_c13.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes no selector or actual model/quality.','prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'resizedAfterGeneration':False,'requestedPixels':[1536,3835],'nativeCoordinateSizeMatches':size==[1536,3835],'coordinate':{'nativeBoxRelativeToR09C13':[1000,1400,2536,5235]},'status':'pending_native_visual_review' if size==[1536,3835] else 'rejected_insufficient_or_different_native_dimensions_no_resize'}
    write(Path(str(out)+'.generation.json'),rec);progress(status=rec['status'],currentPatch=name,generatedNativeCount=len(list((ROOT/'native').glob('r09_c13_*.png'))))
    print(json.dumps({'file':str(out),'pixels':size,'sha256':sha(out),'coordinateSizeMatches':rec['nativeCoordinateSizeMatches']}))
