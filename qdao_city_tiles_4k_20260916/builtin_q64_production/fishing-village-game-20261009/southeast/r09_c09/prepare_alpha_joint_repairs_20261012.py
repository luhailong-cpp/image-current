import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
specs=[
 ('canopy-cross-r2-c2-v3','canopy-cross-r2-c2-v1-input.png',[(600,480,890,725)],'''Reconstruct ONLY the transparent hole in image1. All opaque pixels in image1 are fixed existing art; do not redraw them. Image2 is the original exact geometry: its sharp-edged blurry leaf source block and upper blue ridge seam inside the hole are faults. Reconstruct crisp matching yellow-green leaves, and make one continuous blue ridge upper silhouette through the hole. The upper ridge slope must connect the exact visible fixed endpoints at the left and right hole edge. Keep the original ridge cap thickness, lower cap lip, grout and all tile contours below the hole unchanged, with no shifted lines. All five inputs share the same approved daylight appearance. Do not repaint the entire scene.'''),
 ('ridge-cross-r3-c3-v4','ridge-cross-r3-c3-v1-input.png',[(0,583,770,675),(590,470,775,675)],'''Reconstruct ONLY the transparent holes in image1. All opaque pixels are fixed existing art; do not redraw them. Image2 supplies the exact original curved barrel-tile geometry. Correct the unnatural horizontal source-strip color edge at local y627 toward x0..627, plus the rectangular shadow corner at x627,y510. Connect every visible white highlight, dark grout line, curved tile joint and shadow through the missing thin band at its EXACT visible top and bottom endpoints; preserve tile widths, courses and original layout. Use a continuous naturally painted blue material and diagonal ridge cast shadow with no horizontal rectangular color break. The fixed blue ridge lower edge above the hole and all remaining opaque pixels stay exactly unchanged. Do not repaint the scene.''')
]
refs=read(R/'coordinate-plan.json')['references']
for stem,targetname,holes,detail in specs:
 target=R/'repairs'/targetname
 image=Image.open(target).convert('RGBA');alpha=image.getchannel('A');draw=ImageDraw.Draw(alpha)
 for box in holes:draw.rectangle([box[0],box[1],box[2]-1,box[3]-1],fill=0)
 image.putalpha(alpha)
 guide=R/'repairs'/f'{stem}-alpha-hole-guide.png';image.save(guide)
 record={'file':str(guide),'sha256':sha(guide),'dimensions':[1254,1254],'classification':'mechanical input only; not final art','operation':'retain source RGB geometry and clear alpha in specified repair holes; no RGB redraw or resampling','source':str(target),'sourceSha256':sha(target),'holes':holes,'outputMode':'RGBA'}
 save(str(guide)+'.derivation.json',record)
 prompt='Use case: precise-object-edit. Output native1254x1254 opaque RGB game art at the exact same footprint. '+detail+' Image3(A) authoritative full-map layout only. Image4(B) independent daylight materials. Image5(C) approved mail-daoist QDaoist painterly style. Keep same rounded game forms, vivid blue roof, bright daylight, sharp gentle contours. No camera/layout/object movement, new objects, NPCs, UI text, grids, borders, fog, photographic grain or blur. Preserve all fixed endpoint geometry and reconstruct only missing pixels.'
 pp=R/'repairs'/f'{stem}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
 req={'prompt':prompt,'referenced_image_paths':[str(guide),str(target)]+[x['path'] for x in refs],'transparent_background':False,'route':'builtin','tool':'image_gen__imagegen','actualModel':None,'actualQuality':None,'referenceRoles':{'1':'Exact existing native geometry with alpha holes over repair areas','2':'Original target for exact geometry only; source-strip artifacts are faults','3':'Authoritative full-map layout only','4':'Independent daylight material style','5':'Approved Daoist painterly style only'},'tileBox':[1421,1421,2675,2675] if 'canopy' in stem else [2445,2445,3699,3699],'nativeBoxGlobal':[34189,34189,35443,35443] if 'canopy' in stem else [35213,35213,36467,36467],'createdAt':datetime.now(timezone.utc).isoformat()}
 req['referenceEvidence']=[{'path':p,'sha256':sha(p),'role':req['referenceRoles'][str(i)]} for i,p in enumerate(req['referenced_image_paths'],1)]
 save(R/'repairs'/f'{stem}.request.json',req)
 print(json.dumps({'stem':stem,'guide':str(guide),'sha256':sha(guide)}))

