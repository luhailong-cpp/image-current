
from production import *
P=T/'repairs'
def prepare(name,source,box):
    for d in ['guides','prompts','native','receipts','output']:(P/d).mkdir(parents=True,exist_ok=True)
    src=Path(source);box=list(map(int,box));assert box[2]-box[0]==N and box[3]-box[1]==N
    with Image.open(src) as im:
        assert im.size==(4096,4096);seed=im.crop(box)
    seedpath=P/'guides'/f'{name}.input.png';seed.save(seedpath)
    coord={'candidateBox':box,'contextWorldBox':[ORIGIN[0]+box[0],ORIGIN[1]+box[1],ORIGIN[0]+box[2],ORIGIN[1]+box[3]],'nativeCoreBox':[H,H,H+C,H+C]}
    refs=[{'file':str(seedpath),'sha256':sha(seedpath),'role':'only editing target, exact native crop of assembled candidate'},
    {'file':CONTRACT['layoutReference'],'sha256':sha(CONTRACT['layoutReference']),'role':'layout context only, do not output'},
    {'file':CONTRACT['detailStyleReference'],'sha256':sha(CONTRACT['detailStyleReference']),'role':'approved materials'},
    {'file':CONTRACT['primaryStyleReference'],'sha256':sha(CONTRACT['primaryStyleReference']),'role':'approved primary Daoist chibi style'}]
    task={'wood':"This first image contains only warm wooden floor planks and two large cropped ivory painted arcs. Remove the small polygonal brightness/darkness mismatch around native x=520..660, y=190..510. Continue the existing fine wood grain and soft color naturally through this region. Do not invent new knots. Everything outside that localized wood-tone mismatch must remain identical, especially the plank seams and ivory paint outlines.",
          'stone':"This first image contains pale natural grey STONE STAIR TREADS. Fix ONLY two tiny step-edge kinks around native x=615..650, y=400..430 and native x=615..650, y=648..668. Make each horizontal stair-edge shadow/highlight pass smoothly across these little joints at the same height. Preserve all other tread edges, every step spacing, color, smooth clean stone surface and lighting. Do not add texture or remove fine painting."}[name]
    prompt="Use case: precise-object-edit. EDIT ONLY IMAGE1, the exact 1254x1254 native crop. This is a tiny local continuity repair, NOT a new scene. "+task+"\nLOCK camera, crop, scale and all object geometry. Preserve the outer115-pixel margin on all four sides exactly; this is overlap for the adjoining game-map pixels. Do not modify other regions. No buildings, people, city, symbols, text or new objects. Images2/3/4 are context/style references only; do not output them. Output the SAME opaque1254x1254 close crop with only the specified tiny defects corrected. No resizing or reframing."
    pp=P/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    req={'id':name,'prompt':prompt,'promptFile':str(pp),'references':refs,'referenced_image_paths':[i['file'] for i in refs],'transparent_background':False,'coordinates':coord,'candidateBox':box,'inputCandidate':str(src),'inputCandidateSha256':sha(src),'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
    write(P/'prompts'/f'{name}.request.json',req)
    write(str(seedpath)+'.derivation.json',{'file':str(seedpath),'sha256':sha(seedpath),'operation':'exact native crop, no resampling','source':str(src),'sourceSha256':sha(src),'candidateBox':box,'size':[N,N]})
    print(json.dumps({'request':str(P/'prompts'/f'{name}.request.json'),'seed':str(seedpath)}))
def ingest(name,source):
    req=json.loads((P/'prompts'/f'{name}.request.json').read_text(encoding='utf-8-sig'));src=Path(source);dest=P/'native'/f'{name}.png'
    assert not dest.exists()
    with Image.open(src) as im:im.load();size=list(im.size);fmt=im.format;mode=im.mode
    assert size==[N,N];shutil.copy2(src,dest)
    ev=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
    rec={'id':name,'file':str(dest),'sha256':sha(dest),'width':N,'height':N,'format':fmt,'mode':mode,'generatedAt':now(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':ev['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host tool does not expose model or quality fields','evidence':{'toolReceipt':str(P/'receipts'/f'{name}.receipt.json')},'prompt':req['promptFile'],'promptSha256':sha(req['promptFile']),'references':req['references'],'coordinates':req['coordinates'],'candidateBox':req['candidateBox'],'inputCandidate':req['inputCandidate'],'inputCandidateSha256':req['inputCandidateSha256'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'formalAccepted':False,'visualStatus':'pending'}
    write(str(dest)+'.generation.json',rec)
    print(json.dumps({'record':str(dest)+'.generation.json','sha256':sha(dest)}))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','ingest']);a.add_argument('--name',required=True);a.add_argument('--source',required=True);a.add_argument('--box',nargs=4,type=int);args=a.parse_args()
    if args.action=='prepare':prepare(args.name,args.source,args.box)
    else:ingest(args.name,args.source)

