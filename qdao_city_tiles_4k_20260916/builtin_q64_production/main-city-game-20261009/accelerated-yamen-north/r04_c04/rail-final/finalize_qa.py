from pathlib import Path
import json,hashlib,sys,importlib.util
sys.dont_write_bytecode=True
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;T=O.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p);v={'file':str(p),'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p) as im:v.update(width=im.width,height=im.height,mode=im.mode)
 return v
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(O/'candidate-manifest.json')
manifest['localVisualVerdict']='Formal south rail boundary PASS at worldY16384 with disclosed new stone connector; overall candidate FAIL due adjacent stair top artifact.'
manifest['qaFindings']=[
 {'status':'PASS','scope':'formal south segment1 rail','worldY':16384,'qaFile':str(O/'qa-native/external-south-segment01-native.png'),
  'detail':'Actual 1024x640 view; seam is y320. Both grooves, left gray facet, green recess shadow and outer edge continue without the former horizontal jump. New stone connector above boundary is intentional alternative design.'},
 {'status':'FAIL','scope':'adjacent staircase in 4-patch export','tileBoxApprox':[1120,3970,1140,4005],
  'worldBoxApprox':[13408,16258,13428,16293], 'qaFile':str(O/'qa-native/internal-x1024-bottom-native.png'),
  'detail':'A short white tread fragment remains near the forced derivation rectangle edge; 4-patch version is not recommended for selection.'},
 {'status':'PASS','scope':'internal y3072 rail and col2 stairs','detail':'Actual view of both segment01 and segment02; no new obvious jump. Existing F2 patch pixels were independently verified unchanged.'}
]
for q in manifest['qaImages']:
 n=Path(q['file']).name
 q['visualVerdict']='PASS for local inspected object' if n in ['external-south-segment01-native.png','internal-y3072-segment01-native.png','internal-y3072-segment02-native.png'] else 'FAIL or not overall accepted; see qaFindings'
manifest['status']='review_only_not_overall_pass'
manifest['selectionRecommendation']='Do not select this 4-patch set as passed. Compare the col1-only alternative and read its residual stair finding.'
dump(O/'candidate-manifest.json',manifest)

alt=read(O/'candidate-manifest.json')
alt['exports']=[x for x in alt['exports'] if x['patch'] in ['s03_01','s04_01']]
alt['candidate']=ref(O/'qa-native-col1/candidate-minimum-error.png')
alt['assemblyPaths']=read(O/'qa-native-col1/seam-paths.json')
for src in alt['sources']:
 if src['patch'] in ['s03_02','s04_02']:
  side=read(Path(src['file']+'.generation.json'))
  src.update(side['baseNative'])
Q=O/'qa-native-col1';im=Image.open(Q/'candidate-minimum-error.png').convert('RGB');out=np.array(im)
baseline=np.array(Image.open(O/'qa-native/baseline-minimum-error.png').convert('RGB'))
mask=np.any(out!=baseline,axis=2);ys,xs=np.where(mask)
alt['changedTileBox']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
alt['changedTilePixels']=int(mask.sum())
Image.fromarray((mask*255).astype('uint8')).save(Q/'candidate-change-mask.png')
im.crop((980,3890,1220,4060)).save(Q/'residual-stair-detail-native.png')
for c in [2,3,4]:
 sf=T.parent.parent/f'northwest/r05_c04/native/s01_{c:02d}.png'
 S=np.array(Image.open(sf).convert('RGB'))
 arr=np.concatenate([out[-320:,(c-1)*1024:c*1024],S[115:435,115:1139]],axis=0)
 Image.fromarray(arr).save(Q/f'external-south-segment{c:02d}-native.png')
alt['qaImages']=[{**ref(p),'kind':'unscaled native QA pixels','visualVerdict':'see qaFindings'} for p in sorted(Q.glob('*native.png'))]
alt['qaFindings']=[
 {'status':'PASS','scope':'formal south segment1 rail','worldY':16384,
  'qaFile':str(Q/'external-south-segment01-native.png'),
  'detail':'Actual 1:1 inspection. Formal edge is y320. Old south lower half is untouched. Grooves/facets/shadow continue. New beveled connector is explicitly a design change.'},
 {'status':'FAIL','scope':'adjacent stair geometry in col1-only variant','tileBoxApprox':[1070,3930,1140,4010],
  'worldBoxApprox':[13358,16218,13428,16298],'qaFile':str(Q/'residual-stair-detail-native.png'),
  'detail':'Minimum-error selection removes the floating white fragment of the 4-patch version, but the two adjacent stair blocks have tread tops roughly 35-40px apart. This remains an architectural geometry mismatch near x1088,y3980. Do not claim overall pass.'},
 {'status':'PASS','scope':'internal y3072 segments03 and04','detail':'Both actual native strips viewed; retained stair tone repairs show no new obvious hard color edge.'}
]
alt['localVisualVerdict']='Formal south rail boundary PASS with disclosed connector; whole candidate NOT PASSED due adjacent stair geometry.'
alt['selectionRecommendation']='Root review required. This two-patch option is a cleaner comparison, but neither variant is labeled overall PASS. Existing selected files remain untouched.'
alt['formalAccepted']=False
alt['constraintsVerified']={'rawOutputsByteIdenticalToHost':True,'allExportsOpaque1254PNG':True,'noResizeWarpOrBlur':True,
                            'existingF2NativePixelsUnchanged':True,'oldSouthFileHashUnchanged':True,
                            'selectionOrProgressModified':False}
dump(O/'candidate-col1-manifest.json',alt)
handoff={'candidateForRootReview':str(O/'candidate-col1-manifest.json'),
         'fourPatchRejectedComparison':str(O/'candidate-manifest.json'),
         'generationAndAlphaProvenance':str(O/'derivation-manifest.json'),
         'formalSouthRail':'PASS at native scale, with new connector design',
         'overall':'NOT PASSED: adjacent stair top mismatch remains',
         'nextAction':'Root inspects and chooses. No further generation attempted after true-south and full-assembly QA.',
         'writesConfinedTo':str(O),'exports':alt['exports'],
         'evidence':[ref(Q/'external-south-segment01-native.png'),ref(Q/'residual-stair-detail-native.png')]}
dump(O/'handoff.json',handoff)
print(json.dumps(handoff,ensure_ascii=False))
