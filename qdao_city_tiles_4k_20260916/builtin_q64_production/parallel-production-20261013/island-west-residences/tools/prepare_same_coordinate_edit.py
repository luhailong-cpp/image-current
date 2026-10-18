"""Append-only exact-coordinate edit request records; no AI call or final pixel edits."""
import sys
sys.dont_write_bytecode=True
import json, argparse, copy
from pathlib import Path
import batch_pipeline as p

a=argparse.ArgumentParser()
a.add_argument('--stem',required=True)
a.add_argument('--template',required=True)
a.add_argument('--target',required=True)
a.add_argument('--prompt-file',required=True)
args=a.parse_args()
tile,row,col,attempt=p.parse_stem(args.stem)
core,box=p.boxes(tile,row,col)
template=p.safe_path(args.template)
d=p.read_json(template)
p.require(d['globalBox']==box and d['coreBox']==core,'Template must be same native coordinate')
target=p.safe_path(args.target)
tg=p.read_json(target.with_name(target.name+'.generation.json'))
p.require(tg['globalBox']==box and tg.get('nativeGeometryEligible') is True,'Actual target must be same-coordinate eligible raw')
prompt=p.safe_path(args.prompt_file).read_text(encoding='utf-8-sig')
p.require(bool(prompt.strip()),'Empty actual prompt')
guide=p.BATCH/'guides'/f'{args.stem}.layout-with-native.png'
guide_rec=p.copy_original(p.safe_path(d['guide']['path']),guide)
guide_rec.update({'role':'Exact target composition guide and fixed native overlaps; layout pixels not final','dimensions':[1254,1254]})
target_rec={**p.file_record(target,'EDIT TARGET: existing same-coordinate original native art; preserve correct content'),**p.dimensions(target),'coordinateEvidence':p.file_record(target.with_name(target.name+'.generation.json'))}
refs=[target_rec,guide_rec]
promptrec=p.save_bytes(p.BATCH/'prompts'/f'{args.stem}.txt',prompt.encode('utf-8'))
refsrec=p.save_json(p.BATCH/'guides'/f'{args.stem}.references.json',{'schemaVersion':1,'stem':args.stem,'inputs':refs,'imageGenReferencedImagePaths':[x['path'] for x in refs]})
_,auth=p.authority()
d=copy.deepcopy(d)
d.update({'schemaVersion':2,'createdAtUtc':p.now(),'stem':args.stem,'versionStem':args.stem,'attempt':f'a{attempt:02d}',
          'inputs':refs,'imageGenReferencedImagePaths':[x['path'] for x in refs],'inputCount':2,
          'referenceMode':'same_coordinate_original_target_plus_geometry_guide','guide':guide_rec,
          'prompt':promptrec,'referencesFile':refsrec,'authority':auth,
          'nativeGenerationPerformed':False,'formalAccepted':False,
          'editTarget':target_rec,'templateInput':p.file_record(template),
          'status':'prepared_only_fresh_allocation_precall_required_before_actual_generation'})
inp=p.save_json(p.BATCH/'guides'/f'{args.stem}.input.json',d)
print(json.dumps({'stem':args.stem,'input':inp,'referenced_image_paths':d['imageGenReferencedImagePaths']},ensure_ascii=False))
