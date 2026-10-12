from production import *
r,c,v=map(int,sys.argv[1:4]);n=name(r,c,v);scene=Path(sys.argv[4]).read_text(encoding='utf8')
guide=read(str(W/'guides'/(n+'.guide.png'))+'.derivation.json');borders=[]
for z in guide['neighbors']:
 x,y=z['destination'][:2];borders.append(('RIGHT230' if x==1024 else 'LEFT230' if x==0 and y==0 else 'BOTTOM230' if y==1024 else 'TOP230')+' ('+z['role']+')')
prompt=f'''Use case: sketch-to-render.
Asset type: one opaque exact native 1254x1254 close-up crop of a daylight isometric Q-style Daoist game village map.
Input images: Image1 is the actual registered EDIT TARGET with sharp existing native neighbor borders and a blurred layout-only center. Image2 is whole village layout only. Image3 is material detail only. Image4 is the PRIMARY Q-style Daoist game painting reference.
Primary request: Render only the blurred unfinished portions of Image1 into crisp newly painted game artwork while retaining the EXACT scale, camera, framing, object coordinates and all sharp existing border structures. Continue the real native textures from {', '.join(borders)} naturally through the center. All repeated tile rows, wood edges, stone slab joins, foliage and highlights must physically connect at the same pixel positions where they meet those sharp strips.
Scene: {scene}
Style/materials: rounded hand-painted Q Daoist game illustration, clear warm daylight, detailed but clean surfaces, azure and warm orange ceramic where present, warm painted wooden grain, natural cool gray/cyan paving only where shown. Follow the precise existing material scale, highlights and shadow direction. The style reference contributes painting language only; never import its interface, characters or night setting.
Constraints: exactly 1254x1254 opaque PNG. Treat this as a very close crop of a much larger map: elements naturally continue off canvas. Do not zoom out, recenter, show a complete new building, shift rows, change roof pitch, alter camera, add objects or decorations, invent paths or add dark outline framing. Preserve all visible sharp native slab/roof joint lines at the guide-strip boundaries. No blur, photoreal noise, repeated fragments, text, UI, grid, watermark, transparency or resizing.'''
request(r,c,v,prompt);print(str(W/'receipts'/(n+'.request.json')))
