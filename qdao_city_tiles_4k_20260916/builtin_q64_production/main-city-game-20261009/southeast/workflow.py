"""Local provenance, native-overlap guide preparation and unscaled map QA."""
from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime,shutil

B=Path(__file__).resolve().parent
T=B/'r13_c13'
C=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CO=json.loads((T/'coordinates.json').read_text(encoding='utf-8'))
CONFIG=json.loads((B/'model-verification.json').read_text(encoding='utf-8'))['configSnapshot']
REFS=[C['layoutReference'],C['detailStyleReference'],C['primaryStyleReference']]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def coord(i):return next(x for x in CO['patches'] if x['id']==i[:6])
def native(i):return T/'native'/f'{i}.png'
def active(i):
    mapping=read(T/'active-native-map.json') if (T/'active-native-map.json').exists() else {}
    return native(mapping.get(i,i))
def rec(i,suffix):return T/'records'/f'{i}.{suffix}'
def update(next_id,status='generating_adjacent_native_patches'):
    p=read(B/'progress.json');n=len(list((T/'native').glob('*.generation.json')))
    p.update(updatedAt=now(),status=status,generatedNativeCount=n,currentPatch=next_id,nextStep=f'Generate r13_c13 {next_id} with existing native overlaps; review structure, then continue remaining patches and seam QA.',nativeSourceDirectory=str(T/'native'))
    write(B/'progress.json',p)

def ingest(i,source):
    dst=native(i)
    if dst.exists():raise ValueError('Refusing to replace existing native')
    source=Path(source);im=Image.open(source);im.load()
    if im.format!='PNG' or im.size!=(1254,1254):raise ValueError(f'Unexpected actual native size {im.size}; must replan without scaling')
    shutil.copy2(source,dst)
    request=read(rec(i,'request.json'))
    refs=[]
    saved_refs=read(rec(i,'reference-evidence.json')) if rec(i,'reference-evidence.json').exists() else []
    for j,p in enumerate(request['referenced_image_paths']):
        role=saved_refs[j]['role'] if saved_refs else ['layout reference','detail material style','primary approved style'][REFS.index(p)] if p in REFS else 'edit target: current crop' if j==0 or j==len(request['referenced_image_paths'])-1 else 'supporting layout or native reference'
        refs.append({'path':p,'sha256':sha(p),'role':role,'dimensions':list(Image.open(p).size)})
    record={'id':i,'file':str(dst),'sha256':sha(dst),'generatedAt':now(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':request['referenced_image_paths']},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'宿主管理，工具未披露型号或质量选择器；无可核实实际版本元数据。','evidence':{'receipt':str(rec(i,'receipt.json')),'request':str(rec(i,'request.json')),'originalOutputPath':str(source),'originalSha256':sha(source)},'prompt':str(rec(i,'prompt.txt')),'promptSha256':sha(rec(i,'prompt.txt')),'references':refs,'coordinates':coord(i),'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'native_in_progress_pending_seam_review'}
    write(str(dst)+'.generation.json',record)
    mapping=read(T/'active-native-map.json') if (T/'active-native-map.json').exists() else {}
    mapping[i[:6]]=i
    write(T/'active-native-map.json',mapping)
    ids=[p['id'] for p in CO['patches']];nxt=next((p for p in ids if not native(p).exists()),'all_generated_internal_review')
    update(nxt)
    print(json.dumps({'id':i,'file':str(dst),'size':im.size,'sha256':sha(dst),'next':nxt}))

def prepare(i):
    co=coord(i);r=co['row'];c=co['column']
    im=Image.open(T/'layout-only'/f'{i[:6]}-layout-only.png').convert('RGB')
    anchors=[];neighbors=[]
    if c>1:
        left=f'p{r:02d}_{c-1:02d}';p=active(left)
        if not p.exists():raise ValueError('left native missing')
        im.paste(Image.open(p).crop((1024,0,1254,1254)),(0,0));neighbors.append(str(p));anchors.append({'neighbor':left,'sourceCrop':[1024,0,1254,1254],'target':[0,0,230,1254]})
    if r>1:
        top=f'p{r-1:02d}_{c:02d}';p=active(top)
        if not p.exists():raise ValueError('top native missing')
        im.paste(Image.open(p).crop((0,1024,1254,1254)),(0,0));neighbors.append(str(p));anchors.append({'neighbor':top,'sourceCrop':[0,1024,1254,1254],'target':[0,0,1254,230]})
    guide=T/'layout-only'/f'{i}-native-anchor-guide.png';im.save(guide)
    write(str(guide)+'.derived.json',{'role':'generation guide only, not deliverable pixels','operation':'paste unscaled native neighbor overlap strips on nearest layout-only crop','layoutSource':str(T/'layout-only'/f'{i[:6]}-layout-only.png'),'layoutSourceSha256':sha(T/'layout-only'/f'{i[:6]}-layout-only.png'),'anchors':anchors,'sha256':sha(guide),'nativeNeighborHashes':[{ 'path':p,'sha256':sha(p)} for p in neighbors]})
    anchor_text=' '.join(('Keep the left 230-pixel strip pixel-aligned and unchanged; continue its wood/stone geometry into the newly rendered area.' if c>1 else '', 'Keep the top 230-pixel strip pixel-aligned and unchanged; continue its shapes downward.' if r>1 else ''))
    prompt=f'''Use case: stylized-concept / precise-object-edit.
Asset type: native square map context patch {i} of r13_c13. Requested 1254x1254 opaque square, real new painted detail. This is a small continuous crop, not a standalone scene.
Inputs 1/2/3 are reference only: approved whole-city v9 layout / temple material close-up / primary Xianjian mail illustration style. Input 4, THE LAST IMAGE, is the ONLY EDIT TARGET: a pixelated crop containing sharp native edge strips. Keep its exact current framing. Repaint its blocky area with crisp new native detail while preserving the sharp edge strips. Do not use a reference image as the edit target.
Coordinates: artwork context box {co['contextBox']}; core box {co['coreBox']}. THE LAST IMAGE defines the exact current framing and silhouette. Do not zoom out, rotate, pan, recenter an object, or invent complete objects or buildings. Follow ONLY objects and locations already visible in the last image and specified in CRITICAL LOCAL CROP below. Objects continue past the image edges. Large flat grey areas must remain flat grey stone surfaces.
CONTINUITY: {anchor_text} Keep all silhouettes and grout lines meeting those anchor strips at the exact same positions, width, direction, value and scale. Only replace the blocky layout region with native artwork. Match the anchors' detail density, avoid creating extra seams, small tiles or repeat ornaments. Where a large pale paving slab appears, preserve it as a large slab.
Style: clean bright rounded Taoist chibi game illustration. Natural grey/blue-grey stone surfaces; material finish from temple and mail references, no UI or characters. Clear hand-painted forms, gentle daylight shadows, restrained clean grout and broad quiet shading; no gritty realism, plastic glare, noise or blur. The references supply rendering style only; do not bring their objects into this crop.
Constraints: exact layout and camera; no whole city, rooftops, new architecture, people, tree islands, planters, boats, borders, text labels, watermarks or diagram lines. Render one image filling the canvas. Do not repeat the previous entire patch; this is its spatially adjacent continuation.'''
    rec(i,'prompt.txt').write_text(prompt,encoding='utf-8')
    extra={'p02_01':'The ONLY furniture visible is the tiny cropped wooden foot at the extreme top-right within the top strip. ALL the rest is natural grey pavement with a small scatter of red scraps at the lower-right edge. Absolutely no chair or table legs in the center, no seat, no red chest. Preserve the top strip and extend the floor downward.','p01_02':'A cropped wooden chair fragment enters from the top and left and stops above the lower quarter, with a diagonal wooden brace tapering down toward center. The whole bottom quarter and the right edge are grey floor. No full central vertical chair post from the previous crop. Follow the LAST image composition.'}.get(i[:6],'')
    local_file=T/'local-content.json'
    if local_file.exists():extra=read(local_file).get(i[:6],extra)
    prompt += '\nCRITICAL LOCAL CROP: '+extra
    rec(i,'prompt.txt').write_text(prompt,encoding='utf-8')
    args={'prompt':prompt,'referenced_image_paths':[*REFS,str(guide)],'transparent_background':False}
    write(rec(i,'reference-evidence.json'),[{'path':p,'sha256':sha(p),'role':role} for p,role in zip(args['referenced_image_paths'],['layout reference','detail material style','primary approved style','edit target: layout-only current crop with native overlap anchors'])])
    write(rec(i,'request.json'),args);update(i)
    print(json.dumps({'id':i,'guide':str(guide),'request':str(rec(i,'request.json')),'anchors':anchors}))

if __name__=='__main__':
    if sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='prepare':prepare(sys.argv[2])
