from native_work import *
import sys,argparse
ident=sys.argv[1];neighbors=sys.argv[2:]
assert ident.startswith('r03_c09_')
for suffix in ('.anchored-layout-only.png','.native-neighbors.png'):
 assert not (ZONE/'guides'/f'{ident}{suffix}').exists()
guide(argparse.Namespace(id=ident,neighbor=neighbors,base=None))
ip=ZONE/'prompts'/f'{ident}.inputs.json';refs=read(ip);target=patch(ident)['coreWorldBox']
roles=[]
for n in neighbors:
 b=patch(n)['coreWorldBox'];roles.append('UPPER' if b[1]<target[1] else 'RIGHT' if b[0]>target[0] else 'LEFT')
if len(neighbors)>1:refs[1]['role']='native neighbor reference plate, left to right: '+', '.join(roles)+'; both1254-square unscaled'
else:refs[1]['role']='exact native '+roles[0]+' neighbor and overlap anchor'
write(ip,refs)
prompt=f'''Use case: sketch-to-render. Native opaque1254×1254 square island map patch {ident}.
Edit Image1 in its exact framing. The sharp230px overlap strips are accepted native anchors on the {" and ".join(roles)} sides; blurry interior is coordinate layout only, never finished pixels. Image2 contains the {", ".join(roles)} native neighbor(s), left-to-right in that order. Images3–5 are the approved complete island layout and bright Daoist Q hand-painted material style; do not introduce their buildings or UI into this crop.
Complete the empty stone courtyard interior as freshly painted crisp native details. Extend the exact large diagonal rectangular slab joints, positions and scale entering from each anchor. Pale gray/cyan stone faces with irregular cream mineral flecks, soft rounded bevels, thin warm joints and sparse tiny moss in cracks. Keep slab geometry continuous across the entire square, including x1024 and y230: no straight texture-density or color boundary. Natural stone mottling, no repeated tiny square-grid ornament, no artificial panel seams. Preserve even daylight and existing sparse shadows only.
Keep outer115px contour positions aligned. Empty paving belongs here; no new props, architecture, plants, characters, text or invented shadows. No blur, placeholders, crop, zoom, reframing or moved map coordinates. Finished opaque square1254×1254.'''
fp=ZONE/'prompts'/f'{ident}.prompt.txt';assert not fp.exists();fp.write_text(prompt,encoding='utf-8')
print(json.dumps({'id':ident,'prompt':prompt,'references':[e['file'] for e in refs]}))
