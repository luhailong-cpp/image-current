"""Native material-only edits; selected sources retain coordinate and provenance checks."""
from production import *
R=T/'refinement'
def prepare_refine(r,c):
    n=pid(r,c);original=T/'native'/f'{n}.png'
    for d in ['native','guides','prompts','receipts']:(R/d).mkdir(parents=True,exist_ok=True)
    seed=Image.open(original).convert('RGB');neighbors=[]
    for rr,cc,side in [(r,c-1,'left'),(r-1,c,'top')]:
        neighbor=R/'native'/f'{pid(rr,cc)}.png'
        if neighbor.exists():
            other=Image.open(neighbor)
            seed.paste(other.crop((C,0,N,N)) if side=='left' else other.crop((0,C,N,N)),(0,0))
            neighbors.append({'file':str(neighbor),'sha256':sha(neighbor),'role':f'already-cleaned {side} neighbor; exact 230px shared strip'})
    seedpath=R/'guides'/f'{n}.native-edit-seed.png';seed.save(seedpath)
    refs=[{'file':str(seedpath),'sha256':sha(seedpath),'role':'native edit target; all geometry already final, only reduce stone texture density'},
          {'file':CONTRACT['layoutReference'],'sha256':sha(CONTRACT['layoutReference']),'role':'whole-city geometry reference only'},
          {'file':CONTRACT['detailStyleReference'],'sha256':sha(CONTRACT['detailStyleReference']),'role':'mandatory clean natural grey stone material target'},
          {'file':CONTRACT['primaryStyleReference'],'sha256':sha(CONTRACT['primaryStyleReference']),'role':'primary refined Daoist chibi painting style'}]
    prompt=f'''Use case: precise-object-edit. Edit ONLY image1, a finished 1254x1254 native cropped map patch {n}. This is a MATERIAL CLEANUP, not scene generation. Keep the exact camera, crop, object silhouettes, every stair tread/riser boundary, bevel, wall joint, post outline, wood grain, metal fitting, shadows and lighting. Do not move or resize any object. Images2/3/4 are approved context/style references; image3 sets the CLEAN stone surface target.\nONLY CHANGE: replace the dense cellular/flaky/stippled stone pattern and obvious marbled vein network on all pale/grey STONE surfaces with calm smooth hand-painted natural grey limestone. Stone must have broad subtle tonal planes and very sparse faint brush variation, like the quiet clean steps around the temple in image3. Remove the tiny overlapping flake shapes, scalloped dots, pebbled/speckled pattern, crack networks and sparkly crystalline texture. It must NOT look like terrazzo, marble, fish scales, rough granite, foam, or sponge. Preserve crisp edges and dimensional shading; do not blur the whole image. Keep original stone lightness and grey-beige tint, no global recoloring.\nKeep every non-stone pixel (wood, red lacquer, gold, foliage) unchanged. Do not add objects, ornament, grout lines, cracks, wear, dirt, people, text, labels, border, watermark or grid. Do not zoom or recenter. Produce the same opaque 1254x1254 native crop.\n'''
    if neighbors:prompt+='The already-cleaned native LEFT/TOP overlap strips in image1 are fixed continuity anchors. Match their smooth stone finish and preserve their geometry; no visible boundary at the strip edge.\n'
    (R/'prompts'/f'{n}.prompt.txt').write_text(prompt,encoding='utf-8')
    req={'prompt':prompt,'referenced_image_paths':[q['file'] for q in refs],'transparent_background':False,'references':refs,'neighborSources':neighbors,'coordinates':info(r,c),'editSource':{'file':str(original),'sha256':sha(original),'generationRecord':str(original)+'.generation.json'},'submittedParameters':{'model':None,'quality':None}}
    write(R/'prompts'/f'{n}.request.json',req)
    write(str(seedpath)+'.derivation.json',{'operation':'native copy, replace only overlaps from selected refined neighbors, no resampling','file':str(seedpath),'sha256':sha(seedpath),'derivedFrom':[req['editSource']]+neighbors})
    print(json.dumps({'request':str(R/'prompts'/f'{n}.request.json'),'seed':str(seedpath)}))
def ingest_refine(r,c,source):
    n=pid(r,c);src=Path(source);dest=R/'native'/f'{n}.png'
    assert not dest.exists();shutil.copy2(src,dest)
    with Image.open(dest) as im:im.load();size=list(im.size);fmt=im.format;mode=im.mode
    assert size==[N,N]
    req=json.loads((R/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
    evidence=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
    rec={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'generatedAtEvidence':'Recorded shortly after tool return; tool generation timestamp undisclosed','width':size[0],'height':size[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':evidence['configurationSnapshot'],'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实型号和质量元数据','evidence':{'toolReceipt':str(R/'receipts'/f'{n}.receipt.json')},'prompt':str(R/'prompts'/f'{n}.prompt.txt'),'promptSha256':sha(R/'prompts'/f'{n}.prompt.txt'),'references':req['references'],'neighborSources':req['neighborSources'],'coordinates':req['coordinates'],'editedFrom':req['editSource'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'formalAccepted':False,'sizeMatchesPlan':True,'editIntent':'stone material density cleanup with geometry locked','visualStatus':'pending_QA'}
    write(str(dest)+'.generation.json',rec)
    selectionpath=R/'selection.json';selection=json.loads(selectionpath.read_text(encoding='utf-8-sig')) if selectionpath.exists() else {}
    selection[n]=str(dest.relative_to(T)).replace('\\','/')+'.generation.json';write(selectionpath,selection)
    p=json.loads((ROOT/'progress.json').read_text(encoding='utf-8-sig'));p.update({'status':'native_stone_refinement_in_progress','updatedAtUtc':now(),'generatedNativeCount':len(list(T.rglob('*.generation.json'))),'refinedNativeCount':len(selection),'nextStep':f'Inspect refined {n}; continue cleaned neighboring native patches and reassemble candidate.'});write(ROOT/'progress.json',p)
    print(json.dumps({'native':str(dest),'size':size,'sha256':sha(dest),'selectedRefinedCount':len(selection)}))
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','ingest']);a.add_argument('--row',type=int,required=True);a.add_argument('--col',type=int,required=True);a.add_argument('--source');args=a.parse_args()
    if args.action=='prepare':prepare_refine(args.row,args.col)
    else:ingest_refine(args.row,args.col,args.source)
