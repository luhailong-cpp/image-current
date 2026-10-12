from workflow import ROOT,read,write,sha,now
from PIL import Image
import json
T='r12_c13_p11';v='v02';target=ROOT/'guides'/f'{T}.north-authority-repair-{v}.png';old=ROOT/'native/r12_c13_p11_v01.png';north=ROOT/'native/r11_c13_p41_v01.png';west=ROOT/'native/r12_c12_p14_v04.png'
assert not target.exists()
im=Image.open(old).convert('RGB');ni=Image.open(north).convert('RGB');wi=Image.open(west).convert('RGB')
im.paste(wi.crop((1024,0,1139,1254)),(0,0));im.paste(ni.crop((0,1024,1254,1254)),(0,0));im.save(target)
write(target.with_suffix('.png.generation.json'),{'file':str(target),'sha256':sha(target),'operation':'guide only exact native composite. West true core last115; north full230 wins at corner. No final pixels.','sources':[{'file':str(old),'sha256':sha(old),'crop':[0,0,1254,1254],'destination':[0,0]},{'file':str(west),'sha256':sha(west),'crop':[1024,0,1139,1254],'destination':[0,0]},{'file':str(north),'sha256':sha(north),'crop':[0,1024,1254,1254],'destination':[0,0]}]})
refs=[{'file':target.as_posix(),'sha256':sha(target),'role':'EDIT TARGET. Full native with corrected exact 230 north authority and 115 west true core; correct yellow panel transition only.'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit FIRST attached 1254 x 1254 native image. Preserve identical canvas, crop, perspective, scale and object locations. Repair the single stepped geometry of the cream-yellow paper panel at upper left.

The top 230 pixels are a correct immutable northern neighbor overlap; the leftmost 115 pixels are the correct immutable western neighbor core overlap. Keep both exactly fixed. All wooden deck boards, seams, gold finials, rail posts, fastener, railing, water and their locations are already correct. Keep those unchanged. The sole problem is that the rightmost edge of the cream paper panel and gold rim does not continue smoothly at y=230. Continue the slanted edge from the exact top anchor naturally down to its existing lower gold frame. Redraw the affected panel as one coherent object with a continuous slightly sloping silhouette, no horizontal step, detached golden stripe, broken frame or square guide boundary. Match the soft ivory-gold surface and thin edge to the top. Its lower frame still ends beside the same rail and deck at the same place. Do not invent a second panel, pedestal, extra support, green base or any new object.

The last three images give global layout/material/style context only. Do not recreate their buildings here. No zoom, color shifts, blur or perspective changes. Bright clean hand-painted game art. Output a single opaque native square, desired exactly 1254 x 1254 pixels.
"""
pp=ROOT/'prompts'/f'{T}_{v}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8');write(ROOT/'prompts'/f'{T}_{v}.request.json',{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))

