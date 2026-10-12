from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,patch
name='r12_c13_p34_v03';pid='r12_c13_p34'
body=ROOT/'native/r12_c13_p34_v01.png';north=ROOT/'native/r12_c13_p24_v01.png'
out=ROOT/'guides/r12_c13_p34.native-edit-v03.png';assert not out.exists()
im=Image.open(body).convert('RGB');ni=Image.open(north).convert('RGB');im.paste(ni.crop((0,1024,1254,1254)),(0,0));im.save(out)
sources=[{'file':body.as_posix(),'sha256':sha(body),'role':'coordinate-valid rejected native draft body requiring targeted mast/stitched-line correction'},{'file':north.as_posix(),'sha256':sha(north),'role':'immutable exact north overlap from accepted native artwork'}]
write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'operation':'unscaled full native draft plus exact accepted north230 crop/paste; EDIT TARGET guide only','derivedFrom':sources,'placements':[{'source':body.as_posix(),'sourceCrop':[0,0,1254,1254],'destination':[0,0]},{'source':north.as_posix(),'sourceCrop':[0,1024,1254,1254],'destination':[0,0]}],'usableAsFinalArt':False,'coordinate':patch(pid)})
rp=ROOT/'prompts'/f'{name}.request.json';r=read(rp);r['references'][0]={'file':out.as_posix(),'sha256':sha(out),'role':'EDIT TARGET native p34 draft body with exact accepted top230. Preserve top230; correct mast contour and new stitched borders only.'}
pp=Path(r['promptPath']);s=pp.read_text(encoding='utf-8-sig');start=s.index('Attached image 1');end=s.index('Attached adjacent native images',start)
s=s[:start]+'Attached image 1 is the EDIT TARGET: a coordinate-valid detailed native p34 draft with the exact accepted north230 pixels pasted at its top. Keep those top230 pixels fixed. Edit ONLY the requested mast-contour and stitched-line errors in the body below. Match the same upper cream shade and subtle weave with no visible horizontal strip boundary. Preserve remaining scene geometry and scale. Output one complete native square crop, no comparison panel.\n'+s[end:];pp.write_text(s,encoding='utf-8');write(rp,r)
print(out.as_posix())
