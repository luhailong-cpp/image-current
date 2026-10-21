from workflow import *
from PIL import Image
tid='r13_c13';src=ROOT/'tiles/r13_c13.candidate-right-full-20261013-v01.png';im=Image.open(src).convert('RGB')
for name,x,y,note in [('j13',2330,397,'The obvious artificial vertical division in the blue water window below the wooden seat is at x627, from about y627 to y900. It is not an object. Replace the water on the two sides of that line with one continuous matching wave network, retaining its depth and the real window opening.'),('j33',2330,2445,'The artificial rectangular division in the middle sea is at x627 and y627, especially y627 to742. It is a leftover guide square, not a water wave. Repaint only that local sea so the wave contours, density and colors connect naturally across the rectangle.')]:
 pid=tid+'_repair_'+name;v='v01';g=ROOT/'guides'/f'{pid}_{v}.candidate-only.png';assert not g.exists();im.crop((x,y,x+1254,y+1254)).save(g)
 prompt='Use case: precise-object-edit. Edit this exact native 1254 by 1254 square crop. Keep the entire composition, scale, every wooden edge and water object in EXACTLY the same place. '+note+' Preserve every real wooden plank, joint, dark groove, bevel, rail and hull contour unchanged. Preserve the outer 150 pixel frame unchanged to permit exact world registration. Keep polished existing hand-painted game style and existing fine native detail. Do not blur, shift, rescale, distort perspective, add objects, new wood joints, grid, text, borders or comparisons. Return one opaque 1254 square.'
 write(ROOT/'prompts'/f'{pid}_{v}.registered.json',{'id':pid,'tile':tid,'tileRelativeOrigin':[x,y],'nativeGlobalBox':[49152+x,49152+y,49152+x+1254,49152+y+1254],'sourceCore':[115,115,1139,1139],'destinationCore':[x+115,y+115,x+1139,y+1139],'derivedFromCandidate':str(src),'candidateSha256':sha(src),'operation':'exact candidate crop, no resize; guide only'})
 write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(g)],'transparent_background':False})
 print(g)

