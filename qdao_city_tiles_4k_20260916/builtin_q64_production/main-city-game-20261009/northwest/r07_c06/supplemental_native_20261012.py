"""Truthful evidence for native repair frames outside the normal 16-source grid."""
from pathlib import Path
from PIL import Image
import argparse
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v2',HERE.parent/'production_v2.py')
v2=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
p=argparse.ArgumentParser()
p.add_argument('command',choices=['request','ingest'])
p.add_argument('--id',required=True)
p.add_argument('--args-file')
p.add_argument('--guide-derivation')
p.add_argument('--source')
p.add_argument('--receipt')
args=p.parse_args()
if not all(c.isalnum() or c in '_-' for c in args.id):
    raise ValueError('Unsafe supplemental identifier')
request_path=HERE/'receipts'/f'{args.id}.request.json'
prompt_path=HERE/'prompts'/f'{args.id}.txt'
if args.command=='request':
    params=v2.read(args.args_file)
    derivation=v2.read(args.guide_derivation)
    box=derivation['worldBox']
    assert box[2]-box[0]==box[3]-box[1]==1254
    refs=[dict(file=str(Path(s).resolve()),sha256=v2.sha(s),role='Supplemental actual-seam edit target at the recorded shifted world box')
          for s in params['referenced_image_paths']]
    v2.write_bytes(prompt_path,params['prompt'].encode('utf-8'))
    request=dict(schemaVersion=1,id=args.id,tile=HERE.name,recordedAt=v2.now(),parameters=params,
                 references=refs,prompt=str(prompt_path),promptSha256=v2.sha(prompt_path),worldBox=box,
                 guideDerivation=dict(file=args.guide_derivation,sha256=v2.sha(args.guide_derivation)),
                 nativePixels=[1254,1254],normalPatchPlanMembership=False,
                 actualModel=None,actualQuality=None,configurationSnapshot={'available':False},
                 evidenceMeaning='Exact intended builtin tool arguments. Shifted repair frame is an additional source, not a normal grid patch; no completion implied.')
    v2.write_json(request_path,request)
    print(json.dumps(dict(request=str(request_path),sha256=v2.sha(request_path),worldBox=box)))
else:
    request=v2.read(request_path)
    assert v2.sha(prompt_path)==request['promptSha256']
    receipt=v2.read(args.receipt)
    host=Path(args.source).resolve()
    with Image.open(host) as im:
        im.load()
        assert im.size==(1254,1254) and im.format=='PNG'
        assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
    out=HERE/'repair-native'/f'{args.id}.png'
    result=HERE/'receipts'/f'{args.id}.result.json'
    v2.write_bytes(out,host.read_bytes())
    assert v2.sha(out)==v2.sha(host)
    v2.write_json(result,receipt)
    record=dict(schemaVersion=1,id=args.id,tile=HERE.name,file=str(out),sha256=v2.sha(out),generatedAt=v2.now(),
                hostOutputPath=str(host),hostByteIdentical=True,width=1254,height=1254,opaque=True,format='PNG',
                route='builtin',tool='image_gen.imagegen',actualModel=None,actualQuality=None,
                worldBox=request['worldBox'],fullSourceBox=[0,0,1254,1254],normalPatchPlanMembership=False,
                submittedParameters=request['parameters'],references=request['references'],guideDerivation=request['guideDerivation'],
                evidence=dict(request=str(request_path),requestSha256=v2.sha(request_path),prompt=str(prompt_path),
                              promptSha256=v2.sha(prompt_path),receipt=str(result),receiptSha256=v2.sha(result)),
                sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,
                status='supplemental-native-pending-local-and-perimeter-review',formalAccepted=False)
    v2.write_json(out.with_suffix('.png.generation.json'),record)
    print(json.dumps(dict(file=str(out),sha256=v2.sha(out),worldBox=record['worldBox'],hostByteIdentical=True)))
