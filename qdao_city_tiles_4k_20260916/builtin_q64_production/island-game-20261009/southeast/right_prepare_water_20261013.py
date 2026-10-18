from workflow import ROOT,read,write,sha,context
from pathlib import Path
import sys
pid,v=sys.argv[1:3];neighbors=sys.argv[3:]
assert pid[:7] in ['r13_c13','r14_c13','r13_c14','r12_c14']
context(pid,neighbors,v);g=ROOT/'guides'/f'{pid}.native-context-{v}.png'
prompt='Edit the single supplied image in its EXACT crop, square 1254 x 1254 pixels. This is a close-up of nothing but turquoise sea water in a polished hand-painted Daoist Q game map. Complete only the blurry or empty water areas with sharp natural connected turquoise wave caustics, continuing the scale, contours, blue hues and style of the existing sharp side strips. Preserve the wave positions along existing sharp edges. Connect the wave network smoothly into the interior so no rectangular strip or patch boundary remains. If warm reflected light is present in the guide, preserve its exact position and restrained strength, never add another reflection. Replace any black outer padding with matching water. No scene or zoom-out, land, boat, buildings, docks, fish, plants, people, lettering, border, diagram or watermark. One opaque square, entirely water.'
args={'prompt':prompt,'referenced_image_paths':[str(g)],'transparent_background':False}
pp=ROOT/'prompts'/f'{pid}_{v}.water-only.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{pid}_{v}.water-only.args.json',args)
write(ROOT/'prompts'/f'{pid}_{v}.water-only.request.json',{'args':args,'references':[{'file':str(g),'sha256':sha(g)}],'actualModel':None,'actualQuality':None})
print(g)
