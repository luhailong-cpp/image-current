import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, argparse
from types import SimpleNamespace
from PIL import Image
B = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(B/'tools'))
import batch_pipeline as p
ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
q=sub.add_parser('prepare');q.add_argument('--row',type=int,required=True);q.add_argument('--col',type=int,required=True);q.add_argument('--attempt',type=int,default=1);q.add_argument('--south');q.add_argument('--west');q.add_argument('--east');q.add_argument('--north');q.add_argument('--content',required=True)
q=sub.add_parser('review');q.add_argument('--stem',required=True);q.add_argument('--version',type=int,required=True);q.add_argument('--previous',type=int,default=0);q.add_argument('--note',required=True);q.add_argument('--issue',action='append',default=[])
a=ap.parse_args()
if a.command=='prepare':
    assert 1<=a.row<=4 and 1<=a.col<=4
    stem=f'r01_c02_s{a.row:02d}_{a.col:02d}_a{a.attempt:02d}'
    sides=[x for x in ('south','west','east','north') if getattr(a,x)]
    text=(f'Generate ONE native opaque1254x1254 game-map PNG patch {stem}; 1024 core at(115,115). '
    'There is only ONE reference image: the exact target layout guide. Its blurry interior supplies the exact spatial layout and requires freshly hand-painted native detail; never upscale its pixels. '
    f'EXACT CONTENT: {a.content} '
    f'The sharp230px strips on these sides are fixed existing native overlaps: {",".join(sides)}. Keep their shape, color, wave scale and every shore contour in their exact canvas coordinates. Continue them smoothly through the new interior without horizontal or vertical pasted bands. '
    'Same approved Daoist Q hand-painted game-map style in bright daylight: fine rounded brushwork, turquoise and blue seawater with moderate irregular small wave reflections matching native strips; natural grey/blue-grey coastal rock only where the exact guide shows it. '
    'Most northern sea patches contain WATER ONLY; do not import coast from a neighboring scene or draw extra rocks, islands, foliage, houses, sandbars, mountains, people, animals, boats, props, UI, text, grid, watermark or frame. Preserve the exact camera, coordinate mapping, object scale and blue/cyan distribution of the guide. No dense noise, repetitive patterns, dramatic long white breakers, lighting changes, new shorelines, blurry bands or padding. Output exactly1254x1254 detailed to all edges.')
    prompt=p.save_bytes(B/f'prompts/{stem}.custom.txt',text.encode('utf-8'))
    args=SimpleNamespace(tile='r01_c02',subrow=a.row,subcol=a.col,attempt=a.attempt,prompt_file=prompt['path'],no_neighbor_contact=True,geometry_references_only=True,north=None,north_record=None)
    for side in ('south','west','east','north'):
        setattr(args,side,getattr(a,side));setattr(args,side+'_record',None)
    prep=p.prepare(args)
    # Explicitly read current rules before every generated patch.
    rules=(Path('D:/work/image')/'AGENTS.md').read_text(encoding='utf-8-sig'); split=(Path('D:/work/image')/'docs/MAP_PARALLEL_SPLIT_20261013.json').read_text(encoding='utf-8-sig')
    assert 'allocated_root_reserved' in split and 'Image' in rules
    pre=p.precall(SimpleNamespace(stem=stem,retry_reason=None))
    assert pre['ready']
    inp=p.read_json(B/f'guides/{stem}.input.json')
    print(json.dumps({'stem':stem,'guide':prep['guide']['path'],'prompt':text,'refs':inp['imageGenReferencedImagePaths'],'precall':pre['precallRecord']['path'],'rulesAndSplitRead':True}))
else:
    assert a.stem.startswith('r01_c02_')
    image=B/f'native/{a.stem}.png';gen=p.read_json(image.with_name(image.name+'.generation.json'));inp=p.read_json(B/f'guides/{a.stem}.input.json')
    with Image.open(image) as im: assert im.size==(1254,1254)
    assert gen['nativeGeometryEligible'] and not gen['requiresReferenceRecheck']
    qdir=B/f'qa/c02-north-review/{a.stem}';qdir.mkdir(exist_ok=False)
    qa={'createdAtUtc':p.now(),'stem':a.stem,'image':p.file_record(image),'decision':'continue','selectedForContinuedProduction':True,'note':a.note,'openIssues':a.issue,'reviewBasis':'Generated native original visually inspected by production agent; geometry and declared neighbor strips quick-checked. Internal full-tile seam QA pending.','nativeSize':[1254,1254],'sourceCoordinates':gen['globalBox'],'formalAccepted':False,'internalFullTileQA':'pending','externalAcceptance':'pending'}
    qrec=p.save_json(qdir/'quick-review-v01.json',qa)
    if a.previous:
        prev=p.read_json(B/f'c02-north-progress-v{a.previous:02d}.json');sources=prev['selectedSources']
    else:sources=[]
    assert not any(x['subrow']==gen['subrow'] and x['subcolumn']==gen['subcolumn'] for x in sources)
    sources.append({'stem':a.stem,'subrow':gen['subrow'],'subcolumn':gen['subcolumn'],'path':image.as_posix(),'sha256':gen['sha256'],'generationRecord':image.with_name(image.name+'.generation.json').as_posix(),'quickReview':qrec,'openIssues':a.issue})
    result={'schemaVersion':1,'createdAtUtc':p.now(),'tileId':'r01_c02','selectedNativeCoreCount':len(sources),'expectedCoreCount':16,'selectedSources':sources,'internalFullTileQA':'pending','formalAccepted':False,'remainingCoordinates':[[r,c] for r in range(1,5) for c in range(1,5) if not any(x['subrow']==r and x['subcolumn']==c for x in sources)]}
    print(json.dumps(p.save_json(B/f'c02-north-progress-v{a.version:02d}.json',result)))
