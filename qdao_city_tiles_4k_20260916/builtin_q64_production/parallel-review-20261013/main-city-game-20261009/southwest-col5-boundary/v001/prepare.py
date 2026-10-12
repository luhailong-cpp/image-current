from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,hashlib

BASE=Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production')
ZONE=BASE/'main-city-game-20261009/southwest'
OUT=Path(__file__).resolve().parent
CENSUS=BASE/'parallel-review-20261013/main-city-game-20261009/southwest-census/v01/current-tiles.json'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

selected={t['tile']:t for t in read(CENSUS) if t['tile'] in ['r10_c05','r11_c05','r12_c05','r13_c05']}
catalog=read(ZONE/'current-candidates.json')['tiles']
inputs=[]
for tid,t in selected.items():
    p=Path(t['currentCandidate']);h=sha(p)
    with Image.open(p) as im: pixels=list(im.size);mode=im.mode
    assert h==t['currentCandidateSha256'] and pixels==[4096,4096]
    assert catalog[tid]['candidate']['file']==str(p) and catalog[tid]['candidate']['sha256']==h
    inputs.append({'tile':tid,'file':str(p),'sha256':h,'pixels':pixels,'mode':mode,
                   'coreWorldBox':t['coreWorldBox'],'assembly':t['nativeManifest'],'assemblySha256':sha(t['nativeManifest']),
                   'selectedNativeSlotCount':t['selectedNativePatchCount'],'nativeDimensions':[1254,1254],
                   'inputContract':'4x4 native1254 sources, core1024, halo115, adjacentOverlap230; existing output4096; current adopted assembly source, no new resizing or quilting'})

upper=Image.open(selected['r11_c05']['currentCandidate']).convert('RGB')
lower=Image.open(selected['r12_c05']['currentCandidate']).convert('RGB')
crops=[]
def crop_pair(name,x0,x1,half_height,kind):
    ub=[x0,4096-half_height,x1,4096];lb=[x0,0,x1,half_height]
    image=Image.new('RGB',(x1-x0,half_height*2))
    image.paste(upper.crop(ub),(0,0));image.paste(lower.crop(lb),(0,half_height))
    p=OUT/f'{name}.png';image.save(p)
    rec={'id':name,'file':str(p),'sha256':sha(p),'pixels':list(image.size),'kind':kind,
         'worldBox':[16384+x0,45056-half_height,16384+x1,45056+half_height],
         'sourceA':{'tile':'r11_c05','file':selected['r11_c05']['currentCandidate'],'sha256':selected['r11_c05']['currentCandidateSha256'],'cropBox':ub},
         'sourceB':{'tile':'r12_c05','file':selected['r12_c05']['currentCandidate'],'sha256':selected['r12_c05']['currentCandidateSha256'],'cropBox':lb},
         'joinYPixel':half_height,'sourceResampling':False,'blend':False,'colorAdjustment':False,'blur':False,
         'operation':'exact native adjacent core crops pasted vertically, no labels on art',
         'actualViewedAtNativePixels':False,'status':'pending_actual_native_visual_review'}
    assert ImageChops.difference(image.crop((0,0,x1-x0,half_height)),upper.crop(ub)).getbbox() is None
    assert ImageChops.difference(image.crop((0,half_height,x1-x0,half_height*2)),lower.crop(lb)).getbbox() is None
    crops.append(rec)
for n in range(4):crop_pair(f'r11_c05--r12_c05-segment{n+1}',n*1024,(n+1)*1024,160,'full_boundary_segment')
for x in [1024,2048,3072]:crop_pair(f'r11_c05--r12_c05-intersection-x{x}',x-256,x+256,256,'four_native_patch_intersection_at_tile_boundary')
upper.close();lower.close()

v5p=ZONE/'integrated-20261011/v5/qa-review.json';v5=read(v5p)
pass_pair=[]
for tid in ['r10_c05','r11_c05']:
    prior=next(t for t in v5['tileChecks'] if t['tile']==tid)['candidate']
    assert prior['file']==selected[tid]['currentCandidate'] and prior['sha256']==selected[tid]['currentCandidateSha256']
    pass_pair.append({'tile':tid,'sameCurrentInput':True,'sha256':prior['sha256']})
passed_edge=next(x for x in v5['sharedEdges'] if x['id']=='west_horizontal')
assert passed_edge['status']=='pass_seam_continuity'

qp=ZONE/'pipeline-tools/col5-local-audit-20261013-v01/lane-repair-queue.json';q=read(qp)
fail_issues=[x for x in q['issues'] if x['id'] in ['C5-R13-G01','C5-R13-E01','C5-R13-M01']]
u=Image.open(selected['r12_c05']['currentCandidate']).convert('RGB');l=Image.open(selected['r13_c05']['currentCandidate']).convert('RGB')
reused_fail=[]
for n in range(4):
    x0=n*1024;image=Image.new('RGB',(1024,256));image.paste(u.crop((x0,3968,x0+1024,4096)),(0,0));image.paste(l.crop((x0,0,x0+1024,128)),(0,128))
    existing=ZONE/f'pipeline-tools/col5-local-audit-20261013-v01/chain/r12_c05--r13_c05-{n+1}.png'
    with Image.open(existing) as old:exact=ImageChops.difference(image,old.convert('RGB')).getbbox() is None
    assert exact
    reused_fail.append({'file':str(existing),'sha256':sha(existing),'pixels':[1024,256],'pixelExactToCurrentPair':exact,
                        'worldBox':[16384+x0,49024,16384+x0+1024,49280]})
u.close();l.close()
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Four adjacent Southwest col5 current adopted tiles. New native visual review only r11/r12 boundary; other two edges reuse unchanged-source evidence.',
          'inputs':inputs,'censusSnapshot':{'file':str(CENSUS),'sha256':sha(CENSUS)},
          'currentCatalogSnapshot':{'file':str(ZONE/'current-candidates.json'),'sha256':sha(ZONE/'current-candidates.json')},
          'nativeAssemblyContract':{'tilePixels':[4096,4096],'nativePixels':[1254,1254],'subgrid':[4,4],'corePixels':1024,'haloPixels':115,'adjacentOverlapPixels':230,
                                   'coordinateConvention':'half-open artwork pixel grid; not client world units','noFinalUpscale':True},
          'newReviewCrops':crops,
          'reusedEdges':[{'tiles':['r10_c05','r11_c05'],'status':'pass_seam_continuity','materialStatus':'global_material_pending',
                          'report':str(v5p),'reportSha256':sha(v5p),'currentInputsMatch':pass_pair,'priorFinding':passed_edge},
                         {'tiles':['r12_c05','r13_c05'],'status':'fail_geometry_and_material','report':str(qp),'reportSha256':sha(qp),
                          'nativeEvidence':reused_fail,'recordedIssues':[{'id':i['id'],'kind':i['kind'],'concreteFinding':i['concreteFinding']} for i in fail_issues]}],
          'stale':False,'newImageGenerationCalls':0,'productionFilesModified':False,'deliverableMergedImageCreated':False,
          'noDeliverableMergeReason':'Existing r12/r13 geometry/material failure in chain; native evidence crops only.'}
write('manifest.json',manifest)
print(json.dumps({'outputDirectory':str(OUT),'newCrops':len(crops),'inputHashesMatch':True,'r10To11ReusedPass':True,'r12To13FourExistingCropsPixelExact':True}))
