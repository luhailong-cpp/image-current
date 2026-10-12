"""Own-tile continuation; deliberately suppress shared zone progress writes."""
import importlib.util,json,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('production',HERE.parent/'production.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.TILE=HERE;p.update=lambda *args,**kwargs:None
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['context','request','ingest']);parser.add_argument('patch');parser.add_argument('value',nargs='?');args=parser.parse_args()
assert args.patch in ['p32','p33','p34','p41','p42','p43','p44']
if args.mode=='context':
    assert not (HERE/'native'/f'{args.patch}.png').exists()
    target=HERE/'layout-only'/f'{args.patch}-mixed-context.png'
    assert not target.exists(), 'Do not overwrite input evidence'
    p.context(args.patch)
elif args.mode=='request':
    promptfile=HERE/'prompts'/f'{args.patch}.prompt.txt';reqfile=HERE/'prompts'/f'{args.patch}.request.json'
    assert not promptfile.exists() and not reqfile.exists()
    guide_record=json.loads((HERE/'layout-only'/f'{args.patch}-mixed-context.png.generation.json').read_text(encoding='utf-8'))
    has_left=any(s.get('crop')==[1024,0,1254,1254] for s in guide_record['derivedFrom'])
    bands='TOP230 and LEFT230' if has_left else 'TOP230 only; there is no native west neighbor in this input'
    preserved='topmost115 pixels and leftmost115 pixels' if has_left else 'topmost115 pixels; repaint the entire blurry left edge below the top strip'
    prompt=f'''Use case: precise-object-edit. Create the exact native1254x1254 opaque map crop r06_c13/{args.patch}.
Image 1 is the mixed edit target: crisp {bands} are existing original-pixel neighbor overlaps; remaining blurry pixels are a low-resolution layout guide that must be freshly painted. Images 2/3/4 are approved city layout, near-view materials/daylight and Daoist Mail art style only, never output framing.
{args.value}
Preserve {preserved} precisely so the tile's final core cut connects to the prior core. Continue full object contours naturally through the inner neighbor bands x115..300 and y115..300. Do not draw a horizontal or vertical strip boundary at x230/y230. Do not duplicate trim, roof ridges, flowers or architecture already entering from either neighbor. At their intersection, honor matching object continuity instead of imposing a new rectangle.
Draw all blurry layout-only pixels as real crisp native detail in the existing rounded polished Daoist Q illustration. Use natural pale grey/blue-grey stone where already present, blue-teal ceramic roofs with quiet broad highlights, warm red wood and gold accents only where inherited. Match soft upper-left daylight, perspective, scale, existing surface paths and tile course spacing. Keep image-1 exact framing,1254x1254 dimensions, orientation and object placement. No zoom, stretch, resize, crop, new objects, bokeh, blur, busy new texture, grids, frame, text, UI, watermark or transparency. The result must contain fully painted pixels and no layout blur.'''
    refs=[str(HERE/'layout-only'/f'{args.patch}-mixed-context.png'),p.CONTRACT['layoutReference'],p.CONTRACT['detailStyleReference'],p.CONTRACT['primaryStyleReference']]
    roles=['edit target mixed native left/top neighbors; remaining layout to repaint','approved full geography','approved material and daylight close view','approved Daoist Mail illustration style']
    promptfile.write_text(prompt,encoding='utf-8')
    p.save(reqfile,{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':roles})
    print(str(reqfile))
else:
    p.ingest(args.patch,args.value)
