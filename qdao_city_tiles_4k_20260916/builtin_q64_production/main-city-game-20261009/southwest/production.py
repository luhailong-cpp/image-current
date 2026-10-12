"""Southwest native-art provenance and mechanical guides. No generation API."""
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
TILE='r10_c05'
T=ROOT/TILE
ORIGIN=(16384,36864)
N=1254
C=1024
H=115
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pid(r,c):return f'p{r:02d}_{c:02d}'
def info(r,c):
    x=ORIGIN[0]+(c-1)*C;y=ORIGIN[1]+(r-1)*C
    return {'id':pid(r,c),'row':r,'column':c,'coreWorldBox':[x,y,x+C,y+C],'contextWorldBox':[x-H,y-H,x+C+H,y+C+H],'nativeCoreBox':[H,H,H+C,H+C]}
def progress(nextstep):
    records=list(T.rglob('*.generation.json'))
    write(ROOT/'progress.json',{'zone':'southwest','updatedAtUtc':now(),'status':'native_generation_in_progress','tileRows':[9,16],'tileColumns':[1,8],'firstTile':TILE,'generatedNativeCount':len(records),'usableNativeCount':len(list((T/'native').glob('*.generation.json'))),'complete4kCandidateCount':int((T/'output'/f'{TILE}.candidate.png').exists()),'formalAcceptedCount':0,'activeTile':TILE,'nextStep':nextstep,'clientMappingValidated':False,'capacity5000Validated':False})
def init():
    for d in ['guides','native','prompts','receipts','qa','output']:(T/d).mkdir(parents=True,exist_ok=True)
    image=Image.open(CONTRACT['layoutReference']).convert('RGB')
    entries=[]
    for r in range(1,5):
        for c in range(1,5):
            rec=info(r,c); box=[v*image.width/65536 for v in rec['contextWorldBox']]
            guide=T/'guides'/f'{pid(r,c)}.layout-only.png'
            image.transform((N,N),Image.Transform.EXTENT,box,Image.Resampling.NEAREST).save(guide)
            rec.update({'guide':str(guide),'guideSha256':sha(guide),'layoutSourceBox':box,'guideOnly':True,'gameArt':False,'derivedFrom':[{'file':CONTRACT['layoutReference'],'sha256':sha(CONTRACT['layoutReference'])}],'operation':'layout-only nearest-neighbor sampling from overview, never final art'})
            write(str(guide)+'.derivation.json',rec);entries.append(rec)
    write(T/'coordinates.json',{'tile':TILE,'tileCoreWorldBox':[16384,36864,20480,40960],'tileContextWorldBox':[16269,36749,20595,41075],'nativePixels':N,'corePixels':C,'haloPixels':H,'adjacentOverlapPixels':2*H,'halfOpenCoordinates':True,'patches':entries})
    write(ROOT/'batch-evidence.json',{'verifiedOn':'2026-10-09','configurationSnapshot':json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'officialSourcesChecked':['https://openai.com/index/introducing-chatgpt-images-2-5/','https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'],'finding':'Official pages confirm Images 2.5 availability and Sunburst max quality. No newer formal model found. Shared config unchanged; batch uses existing snapshot. Built-in has no model/quality parameters.','actualModel':None,'actualQuality':None,'contractSha256':sha(ROOT.parent/'production-contract.json')})
    progress('Generate p01_01 native artwork from its layout-only guide and three required references.')
def prepare(r,c):
    name=pid(r,c);rec=info(r,c)
    guide=T/'guides'/f'{name}.layout-only.png'
    seed=Image.open(guide).convert('RGB');neighbors=[]
    if c>1:
        prev=T/'native'/f'{pid(r,c-1)}.png'
        if prev.exists():
            seed.paste(Image.open(prev).crop((C,0,N,N)),(0,0));neighbors.append({'file':str(prev),'sha256':sha(prev),'role':'left neighbor; rightmost 230 pixels transferred exactly into target leftmost 230 pixels'})
    if r>1:
        prev=T/'native'/f'{pid(r-1,c)}.png'
        if prev.exists():
            seed.paste(Image.open(prev).crop((0,C,N,N)),(0,0));neighbors.append({'file':str(prev),'sha256':sha(prev),'role':'upper neighbor; bottommost 230 pixels transferred exactly into target topmost 230 pixels'})
    seedpath=T/'guides'/f'{name}.continuity-seed.png';seed.save(seedpath)
    refs=[{'file':str(seedpath),'role':'edit target: layout-only guide plus native overlap strips; redraw low-detail interior in native detail','sha256':sha(seedpath)},{'file':CONTRACT['layoutReference'],'role':'approved v9 entire-city geometry reference only','sha256':sha(CONTRACT['layoutReference'])},{'file':CONTRACT['detailStyleReference'],'role':'current temple close view material and daylight style','sha256':sha(CONTRACT['detailStyleReference'])},{'file':CONTRACT['primaryStyleReference'],'role':'approved primary Daoist chibi hand-painted style, no UI copied','sha256':sha(CONTRACT['primaryStyleReference'])}]
    prompt=f'''Use case: precise-object-edit. Asset type: one native game-map detail patch for 五行奇谈, southwest arena area. Output one opaque square PNG, requested native canvas 1254x1254.\nEDIT IMAGE 1 ONLY. It is an exact spatial crop guide for patch {name} inside tile r10_c05. Do not zoom out or recenter. Target world context is {rec['contextWorldBox']}, pixel ratio 1 output pixel = 1 world-art pixel, planned central 1024x1024 core at [115,115,1139,1139]. All images depict the same approved city at different reference scales.\nImage 2 is complete v9 layout, GEOMETRY ONLY; do not render a whole city. Image 3 is current approved close-view materials and daylight. Image 4 is primary style reference: match its refined rounded Daoist chibi hand-painted forms, clean contours, soft material volume and polish; do not copy its UI, text, people, moon, or scene.\nRepaint the coarse image-1 guide into crisp new native detail at EXACTLY the same framing and projected geometry. This is a tiny close fragment of the arena wooden deck / red rail / pale stone approach, not a complete standalone arena. Keep all clipped objects clipped at the same edges. Preserve natural grey stone and clean warm wood; warm red rail with restrained gold; subtle wood board grain, precise board seams, soft bevels, rounded sturdy forms, clean daylight. No dirty scratches or noise. No extra buildings, props, people, labels, borders, watermarks, grid lines, whole-city overview, extra text or new emblems. Match the few curved gold/cream arena emblem strokes ONLY where present in the guide; never invent a complete character or emblem. Any red paper scraps only if visible at this crop. Do not bring distant towers into this small patch. Keep trees by existing buildings or walls if present, never add street pots.\n'''
    if neighbors:
        prompt+='CONTINUITY: The sharp native strips in Image 1 come from already generated adjacent artwork. Preserve their exact scale, lighting, board-line locations and shape intersections, and continue each line into the newly painted area. '
        if c>1:prompt+='The leftmost 230-pixel strip is fixed context from the left neighbor. '
        if r>1:prompt+='The topmost 230-pixel strip is fixed context from the upper neighbor. '
        prompt+='Do not repaint these fixed strips into a different arrangement; do not stretch them; no visible divider at their inner edge.\n'
    prompt+='Native visual detail is required; the coarse guide is not final art. Maintain the established overhead oblique map camera. Output just this single cropped fragment.\n'
    promptpath=T/'prompts'/f'{name}.prompt.txt';promptpath.write_text(prompt,encoding='utf-8')
    write(T/'prompts'/f'{name}.request.json',{'prompt':prompt,'referenced_image_paths':[q['file'] for q in refs],'transparent_background':False,'references':refs,'neighborSources':neighbors,'coordinates':rec,'requestedNativePixels':[N,N],'submittedParameters':{'model':None,'quality':None}})
    write(str(seedpath)+'.derivation.json',{'file':str(seedpath),'sha256':sha(seedpath),'operation':'copy native neighbor overlap strips onto layout-only guide without resampling; NOT final art','guide':str(guide),'guideSha256':sha(guide),'neighbors':neighbors})
    progress(f'Generate {name} using saved request, then save and inspect actual native output.')
    print(json.dumps({'request':str(T/'prompts'/f'{name}.request.json'),'seed':str(seedpath)},ensure_ascii=False))
def ingest(r,c,source):
    name=pid(r,c);src=Path(source);dest=T/'native'/f'{name}.png'
    if dest.exists():raise RuntimeError('Do not overwrite native output')
    with Image.open(src) as im: im.load();width,height=im.size;fmt=im.format;mode=im.mode;metadata={k:str(v)[:4000] for k,v in im.info.items()}
    shutil.copy2(src,dest)
    req=json.loads((T/'prompts'/f'{name}.request.json').read_text(encoding='utf-8-sig'))
    evidence=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
    record={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'width':width,'height':height,'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':evidence['configurationSnapshot'],'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实型号和质量元数据','evidence':{'toolReceipt':str(T/'receipts'/f'{name}.receipt.json'),'pngMetadata':metadata},'prompt':str(T/'prompts'/f'{name}.prompt.txt'),'promptSha256':sha(T/'prompts'/f'{name}.prompt.txt'),'references':req['references'],'neighborSources':req['neighborSources'],'coordinates':req['coordinates'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'formalAccepted':False,'sizeMatchesPlan':[width,height]==[N,N]}
    write(str(dest)+'.generation.json',record)
    progress(f'Inspect {name}; continue to next adjacent patch only after checking geometry and size.')
    print(json.dumps({'native':str(dest),'size':[width,height],'sha256':sha(dest),'sizeMatchesPlan':record['sizeMatchesPlan']}))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['init','prepare','ingest']);a.add_argument('--row',type=int,default=1);a.add_argument('--col',type=int,default=1);a.add_argument('--source');args=a.parse_args()
    if args.action=='init':init()
    elif args.action=='prepare':prepare(args.row,args.col)
    else:ingest(args.row,args.col,args.source)
