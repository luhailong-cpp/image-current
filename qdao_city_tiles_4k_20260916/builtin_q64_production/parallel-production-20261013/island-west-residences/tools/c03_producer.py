"""Mechanical c03-only prepare and quick-QA evidence. Does not generate artwork."""
import sys
sys.dont_write_bytecode = True
import argparse
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from PIL import Image

spec = importlib.util.spec_from_file_location('batch_pipeline', Path(__file__).with_name('batch_pipeline.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def prepare(a):
    assert a.tile in ('r02_c03','r01_c03')
    stem=f'{a.tile}_s{a.row:02d}_{a.col:02d}_a{a.attempt:02d}'
    core,box=m.boxes(a.tile,a.row,a.col)
    sides=[d for d in ('south','west','east','north') if getattr(a,d)]
    desc='; '.join({'south':'SOUTH top 230 pixels align to target bottom 230 pixels at y=1024',
                   'west':'WEST right 230 pixels align to target left 230 pixels at x=0',
                   'east':'EAST left 230 pixels align to target right 230 pixels at x=1024',
                   'north':'NORTH bottom 230 pixels align to target top 230 pixels at y=0'}[d] for d in sides)
    # Pipeline contact panel order is north, south, west, east.
    order=[d for d in ('north','south','west','east') if getattr(a,d)]
    text=f'''Generate ONE native opaque PNG exactly 1254x1254 for game-map patch {stem}. This is a tiny magnified crop of the existing island, NOT a whole scene. Image 1 is the exact target composition guide. Image 2 is the adjacent native contact, with full-size 1254-pixel panels ordered {', '.join(order)} from left to right. The contact is supporting continuity detail, not a composition to copy or fit into the target. Global target box {box}, central 1024 core {core}.
Only render the local objects, planes and silhouettes visible in Image 1 at exactly the same camera, magnification, positions, relative sizes and angles. {a.subject}
The sharp border strips in Image 1 are actual native neighbor pixels. Preserve their geometry and colors and continue them seamlessly into the remaining target area: {desc}. Never copy the entire adjacent image. Never shift the shared strips, invent a boundary, or change scale. Redraw the blurry overview interior into fine original hand-painted detail, not an enlargement. Use the sharp neighboring art for native brush quality, rounded Daoist Q shapes, bright daylight, blue ceramics, warm orange/gold trim, ivory walls, natural grey stone and turquoise sea only where actually present. Do not invent objects, ornament, paving, buildings, vegetation, lanterns or shore absent from the guide. No whole building or courtyard unless the guide actually contains one. No text, UI, people, watermark, frame or padding. All objects that run off-frame must remain cropped. Opaque 1254x1254, actual builtin included image route only.'''
    if a.no_neighbor_contact:
        text=text.replace(f'Image 2 is the adjacent native contact, with full-size 1254-pixel panels ordered {", ".join(order)} from left to right. The contact is supporting continuity detail, not a composition to copy or fit into the target. ', '')
    prompt=m.BATCH/f'prompts/{stem}.custom.txt'
    m.save_bytes(prompt,text.encode('utf-8'))
    kw=dict(tile=a.tile,subrow=a.row,subcol=a.col,attempt=a.attempt,geometry_references_only=True,
            prompt_file=str(prompt),no_neighbor_contact=a.no_neighbor_contact)
    for d in ('north','south','west','east'):
        p=getattr(a,d)
        kw[d]=p
        kw[d+'_record']=str(Path(p).with_suffix('.derivation.json')) if p and 'current-derived' in p else None
    result=m.prepare(SimpleNamespace(**kw))
    pre=m.precall(SimpleNamespace(stem=stem,retry_reason=a.retry_reason))
    print(json.dumps({'prepared':result,'ready':pre['ready'],'precall':pre['precallRecord'],
                      'inputDrift':pre['inputDrift'],'conflicts':pre['coordinateCheck']['externalConflicts']},ensure_ascii=False))


def review(a):
    assert a.stem.startswith(('r02_c03_','r01_c03_'))
    inp=m.read_json(m.BATCH/f'guides/{a.stem}.input.json')
    raw=m.BATCH/f'native/{a.stem}.png'
    im=Image.open(raw).convert('RGB')
    crops=[]
    for n in inp['neighbors']:
        side=n['direction']; other=Image.open(n['path']).convert('RGB')
        crop=other.crop(n['sourceCrop'])
        x,y=n['destination']; target=im.crop((x,y,x+crop.width,y+crop.height))
        if side in ('north','south'):
            pair=Image.new('RGB',(1254,460));pair.paste(target,(0,0));pair.paste(crop,(0,230))
        else:
            pair=Image.new('RGB',(460,1254));pair.paste(target,(0,0));pair.paste(crop,(230,0))
        crops.append({'side':side,'targetFirst':True,'referenceSecond':True,
                      **m.save_image(m.BATCH/f'qa/c03/{a.stem}/{side}-overlap-100pct.png',pair)})
    print(json.dumps({'stem':a.stem,'raw':m.file_record(raw),'nativeOverlapComparisons':crops},ensure_ascii=False))


def select(a):
    assert a.stem.startswith(('r02_c03_','r01_c03_'))
    raw=m.BATCH/f'native/{a.stem}.png'
    qa={'checkedAtUtc':m.now(),'stem':a.stem,'raw':m.file_record(raw),
        'dimensions':m.dimensions(raw)['nativeSize'],'layoutQuickPass':True,
        'adjacentQuickPass':True,'propagationAllowed':True,'notes':a.notes,'formalAccepted':False}
    rec=m.save_json(m.BATCH/f'qa/c03/{a.stem}/quick-review-v01.json',qa)
    previous=m.read_json(m.BATCH/f'c03-progress-v{a.previous:02d}.json')
    previous.update({'updatedAtUtc':m.now(),'status':'active_native_production','formalAccepted':False})
    previous['selected'].append({'stem':a.stem,'raw':m.file_record(raw),'qa':rec})
    previous['selectedCount']=len(previous['selected'])
    for key in ('nextStem','nextPrepared','nextPrecall','nextImagegenCalled','nextRawExists','reason'):
        previous.pop(key,None)
    print(json.dumps(m.save_json(m.BATCH/f'c03-progress-v{a.version:02d}.json',previous)))


p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
q=sub.add_parser('prepare');q.add_argument('--tile',required=True);q.add_argument('--row',type=int,required=True);q.add_argument('--col',type=int,required=True);q.add_argument('--attempt',type=int,default=1);q.add_argument('--subject',default='Retain every existing local object and its large cropped scale.');q.add_argument('--retry-reason')
q.add_argument('--no-neighbor-contact',action='store_true')
for side in ('north','south','west','east'):q.add_argument('--'+side)
q=sub.add_parser('review');q.add_argument('--stem',required=True)
q=sub.add_parser('select');q.add_argument('--stem',required=True);q.add_argument('--notes',required=True);q.add_argument('--previous',type=int,required=True);q.add_argument('--version',type=int,required=True)
a=p.parse_args(); {'prepare':prepare,'review':review,'select':select}[a.cmd](a)
