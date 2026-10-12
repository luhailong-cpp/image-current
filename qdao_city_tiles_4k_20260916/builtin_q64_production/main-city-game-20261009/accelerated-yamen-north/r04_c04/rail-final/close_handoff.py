from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def dump(f,v):f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
M=O/'candidate-final-manifest.json';m=read(M)
m['status']='ready_for_root_review_with_minor_upper_tone_caveat'
m['localVisualVerdict']='Formal south rail/grooves/shadow PASS; adjacent stair lip PASS after stage4 restoration. New stone connector is a disclosed design change. A faint rectangular tone transition remains on the upper right rail facet near tile [905,2957,953,2990]; root should inspect before whole-tile acceptance.'
m['formalAccepted']=False
m['qaFindings']=[
 {'status':'PASS','scope':'formal south rail','qaFile':str(O/'qa-native-final/external-south-segment01-native.png'),'worldBoundaryY':16384,'imageBoundaryY':320,'note':'Actual native view in stairs-restored QA; latest candidate unchanged in this southern region.'},
 {'status':'PASS','scope':'adjacent stair lip','qaFile':str(O/'qa-native-final/stair-detail-native.png'),'note':'Original aligned stage4 stair pixels restore continuous front lip. No extra generation.'},
 {'status':'MINOR_REVIEW','scope':'upper right stone rail facet','tileBoxApprox':[905,2957,953,2990],'worldBoxApprox':[13193,15245,13241,15278],'qaFile':str(O/'qa-native-final/upper-join-detail-native.png'),'before':str(O/'qa-native-final/upper-join-before-native.png'),'note':'A faint horizontal rectangular tone transition is still visible in the right facet at the start of the upper overlap. No geometry gap; do not claim unqualified whole-tile pass.'}
]
for q in m['qaImages']:
 n=Path(q['file']).name
 if n in ['upper-join-detail-native.png','internal-y3072-segment01-native.png','rail-full-join-native.png']:q['visualVerdict']='actual view: see upper tone caveat'
 else:q['visualVerdict']='Previously actual-viewed unchanged southern/stair content, or comparison available; root review'
dump(M,m)
for x in m['exports']:
 f=Path(x['record']);v=read(f);v['localVisualVerdict']=m['localVisualVerdict'];dump(f,v)
h={'status':m['status'],'candidateManifest':str(M),'derivationManifest':m['derivationManifest'],
   'exports':m['exports'],'localVerdict':m['localVisualVerdict'],'designChange':m['designChange'],
   'formalAccepted':False,'selectionOrProgressModified':False,
   'nativeQA':str(O/'qa-native-final/external-south-segment01-native.png'),
   'stairQA':str(O/'qa-native-final/stair-detail-native.png'),
   'upperToneQA':str(O/'qa-native-final/upper-join-detail-native.png')}
dump(O/'handoff.json',h)
print(str(O/'handoff.json'))
