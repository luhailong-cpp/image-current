from pathlib import Path
import json,sys,hashlib
HERE=Path(__file__).resolve().parent;ZONE=HERE.parents[2]
case=sys.argv[1];note=sys.argv[2]
rec=json.loads((HERE/'records'/f'{case}.input.json').read_text(encoding='utf-8'))
contract=json.loads((ZONE.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
refs=[rec['context'],contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
prompt=f'''Use case: precise-object-edit. Edit image 1, an exact1254x1254 existing native-pixel game-map crop. Image2 is approved complete city geography, image3 is close-view materials/daylight, image4 is Daoist Q illustration style only; preserve image1 framing and objects.
{note}
Use the existing polished rounded painted style, colors and illumination. Repaint only the local discontinuity into coherent native detail. Keep every object contour, tile rib, red beam, gold ridge, plaster edge and branch not directly involved in the defect exactly in place. Preserve original pixels near all four outer image edges and outside the repair neighborhood. No zoom, crop, scaling, perspective changes, sharpen filter, blur, feathered fog, depth of field, added decoration, text, watermark, frame, grid or transparency. Return1254x1254 opaque with the same framing.'''
req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':['exact existing-pixel repair target','approved full-layout context','approved material/daylight detail','primary Daoist Mail style']}
path=HERE/'prompts'/f'{case}.request.json';assert not path.exists()
path.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(HERE/'prompts'/f'{case}.prompt.txt').write_text(prompt,encoding='utf-8')
rec['references']=[{'file':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'role':r} for p,r in zip(refs,req['referenceRoles'])]
(HERE/'records'/f'{case}.input.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(path)
