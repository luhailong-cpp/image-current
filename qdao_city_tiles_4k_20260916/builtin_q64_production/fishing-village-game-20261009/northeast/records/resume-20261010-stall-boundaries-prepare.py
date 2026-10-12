from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,role):return {'path':str(p),'sha256':sha(p),'role':role}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8'))
s=B/'native/resume-20261010-stall-v1.png';im=Image.open(s).convert('RGB')
for side,orig,world in [('upper','r06_c12_p34-v1.png',[48013,22413,49267,23667]),('lower','r06_c12_p44-v1.png',[48013,23437,49267,24691])]:
 o=B/'native'/orig;g=Image.open(o).convert('RGB')
 if side=='upper':g.paste(im.crop((0,0,1254,742)),(0,512));box=[0,0,1254,742];dest=[0,512,1254,1254]
 else:g.paste(im.crop((0,512,1254,1254)),(0,0));box=[0,512,1254,1254];dest=[0,0,1254,742]
 gp=B/f'guides/resume-20261010-stall-{side}-native-guide-v1.png';g.save(gp)
 write(str(gp)+'.derived.json',{'purpose':'native edit guide only','sources':[rec(o,'existing surrounding pixel plane'),rec(s,'corrected stall native source')],'operation':'opaque crop/paste only, no resizing','worldBox':world,'nativeSourceBox':box,'destinationBox':dest,'formalAccepted':False})
 lp=B/f'guides/resume-20261010-stall-{side}-layout-only-v1.png';overview=[v*1254/57344 for v in world];Image.open(C['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,overview,Image.Resampling.BICUBIC).save(lp)
 write(str(lp)+'.derived.json',{'purpose':'layout-only, never final pixels','source':rec(C['layoutReference'],'authoritative map'),'worldBox':world,'overviewBox':overview,'operation':'EXTENT bicubic layout guide only'})
 if side=='upper':
  action='Repair the horizontal composition discontinuity around y512, especially x700..1254 where the lower native fish/rim must grow upward naturally into the existing right-edge cropped small stall. Reconstruct the entire missing rear rim and fish continuation across y300..650. Keep the upper-left large neighboring stall post exactly in place; it is a separate existing object. Preserve top band y0..230 and left band x0..180. Preserve the corrected small-stall front protruding rim around (410,862), its post starts near x570,y1000 and continues out the bottom; preserve bottom band y1024..1254 and all its fish/rim positions. Do not move the new small stall back toward the right. The top edge right section is gray floor, the small stall enters through RIGHT edge farther down, as layout5 confirms. This should be one continuous isometric scene with intact floor joints, never a straight composition seam.'
 else:
  action='Repair the horizontal composition discontinuity around y742 where the upper native corrected stall base/wood panel/shadow is cut against old warm floor below. Keep the complete long front support centered x590 with its foot at y470 unchanged. Keep all tabletop/wood/fish geometry in the TOP band y0..230 unchanged and retain the LEFT band x0..180. Continue the wooden front bottom brace naturally down-right so it exits RIGHT edge near y850, with its cast shadow on nearby warm stones. This is a real table front, do not cut it off with floor at y742. Restore warm stone flooring beneath and surrounding it, connecting to unchanged BOTTOM band y1024..1254 and the existing partial lantern base at bottom-left. No new posts, fish, boxes or freestanding objects. No horizontal tone band. Image5 supplies correct remaining stall footprint only; derive exact fish/wood detail from native image4.'
 prompt=f'''Use case: precise-object-edit. Output exactly one native 1254 x 1254 square. Edit image4, an exact-coordinate native composite with a broken join, into continuous finished game artwork. Image1 is authoritative global layout; image2 independent materials; image3 primary rounded Daoist Q illustration style only, ignore its UI/text/night. Image5 is the exact same coordinate crop as image4, layout-only, never copy its blur. {action}
 Preserve isometric perspective, scale, pale gray/blue-gray natural stone and existing warm stones, light direction, detailed hand-painted wood, ice and tapered blue/silver fish. Preserve all marked edge bands and connect inside them without shifts or borders. Match the existing native clarity and gently rounded forms. Do not add buildings, trees, characters, words, UI, watermark or borders. No upscaled blurry content, no multi-panel output. Return only the square native art.'''
 pf=B/f'records/resume-20261010-stall-{side}-v1.prompt.txt';pf.write_text(prompt,encoding='utf-8')
 refs=[rec(C['layoutReference'],'global layout'),rec(C['detailStyleReference'],'independent materials'),rec(C['primaryStyleReference'],'primary Daoist Q style'),rec(gp,'exact native composite edit target'),rec(lp,'exact layout-only guide')]
 write(B/f'records/resume-20261010-stall-{side}-v1.submission.json',{'tool':'image_gen.imagegen','route':'builtin','submittedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promptFile':str(pf),'promptSha256':sha(pf),'references':refs,'worldBox':world,'target':{'model':'gpt-image-2.5-sunburst','quality':'max'},'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'expectedNativeSize':[1254,1254]})
 print(str(gp))
