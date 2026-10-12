from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def jsave(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assembly=read(D/'output/assembly.json');evidence=read(D/'qa/issue-evidence.json')
original=np.array(Image.open(assembly['inputs']['originalContext']['path']).convert('RGB'))[115:4211,115:4211]
candidate=np.array(Image.open(assembly['outputs']['core']['path']).convert('RGB'))
issues=[
 {'id':'G01','severity':'P1','corePoint':[930,2795],'coreBox':[920,2780,950,2815],'category':'dangling-diagonal-joint','description':'Diagonal recessed joint starts abruptly in the middle of an uninterrupted slab. It has no connection to a slab boundary.','evidenceKey':'G01-dangling-y2795'},
 {'id':'G02','severity':'P1','corePoint':[1113,3158],'coreBox':[1100,3140,1130,3175],'category':'dangling-diagonal-joint','description':'Southwest branch of a cross junction terminates abruptly on the slab surface.','evidenceKey':'G02-G03-dangling-y3158-y3290'},
 {'id':'G03','severity':'P1','corePoint':[1100,3290],'coreBox':[1080,3265,1120,3310],'category':'dangling-diagonal-joint','description':'A separate northeast-running diagonal terminates in the slab. Its endpoint does not connect to the branch above; the two visible segments do not form a continuous joint.','evidenceKey':'G02-G03-dangling-y3158-y3290'},
 {'id':'G04','severity':'P1','corePoint':[975,3642],'coreBox':[950,3615,995,3670],'category':'disconnected-offset-joint','description':'Long diagonal has a visible gap and lateral step between its two pieces. Groove and bright bevel both fail to connect.','evidenceKey':'G04-notch-y3642'},
 {'id':'G05','severity':'P2','corePoint':[1065,4000],'coreBox':[1040,3980,1090,4020],'category':'small-joint-offset','description':'Lower diagonal exhibits a smaller abrupt position/width step with a doubled/notched bevel.','evidenceKey':'G05-notch-y4000'},
 {'id':'G06','severity':'P1','corePoint':[2118,2165],'coreBox':[2100,2150,2140,2180],'category':'dangling-horizontal-joint','description':'Horizontal grout starts in the slab to the left of the vertical T junction, leaving an unsupported free endpoint.','evidenceKey':'G06-horizontal-dangling'},
 {'id':'G07','severity':'P2','corePoint':[930,2350],'coreBox':[915,2330,950,2370],'category':'diagonal-joint-step','description':'Diagonal grout at the left overlap has a visible short doubled segment / lateral step.','evidenceKey':'G07-notch-y2350'}
]
for i in issues:
 b=i['coreBox'];i['contextPoint']=[i['corePoint'][0]+115,i['corePoint'][1]+115];i['worldPoint']=[i['corePoint'][0]+16384,i['corePoint'][1]+40960]
 i['contextBox']=[b[0]+115,b[1]+115,b[2]+115,b[3]+115]
 i['worldBox']=[b[0]+16384,b[1]+40960,b[2]+16384,b[3]+40960]
 i['evidence']=evidence[i.pop('evidenceKey')]
 i['presentBeforeThisComposite']=bool(np.array_equal(original[b[1]:b[3],b[0]:b[2]],candidate[b[1]:b[3],b[0]:b[2]]));assert i['presentBeforeThisComposite']
 i['blocksInternalGeometryPass']=True
tone={'id':'T01','severity':'P2','category':'stone-tone-discontinuity','coreBox':[2950,1030,3150,1490],'description':'A milder slanted warm/cool transition remains on second-row stair risers near x3072. It is a material continuity issue rather than a disconnected grout line.','evidence':evidence['T01-second-row-color-x3072'],'geometryIssue':False}
review={'status':'FAIL-INTERNAL-GEOMETRY','internalPassed':False,'formalAccepted':False,'generatedComplete4KCandidate':True,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'coordinateConvention':'All core coordinates use the 4096x4096 output, zero-based origin top left. Context = core + (115,115); world = core + (16384,40960). Bounding boxes are left/top inclusive, right/bottom exclusive.','outputs':assembly['outputs'],'summary':'Approved upper-row color/north-boundary repairs and the isolated p04_02 T-junction repair were integrated successfully. The full tile remains unacceptable internally because seven other grout geometry defects remain in the middle/lower area. No new generation occurred during this integration/QA phase.','geometryIssues':issues,'materialIssues':[tone],'geometryIssueCount':len(issues),'remainingMaterialIssueCount':1,'coverage':{'fullCoreOverviewViewed':True,'upperEight1024CellsViewedByIntegrator':True,'lowerEight1024CellsViewedByIndependentReviewer':True,'targetedNativeResolutionIssueCropsViewedByIntegrator':True,'threeHorizontalAndThreeVerticalSeamStripsSaved':True,'northNeighborBoundaryFourNativeWidthCropsViewed':True,'crossZoneOrOtherNeighborBordersReviewed':False},'passedLocalChecks':[{'name':'First-row north/leaf/color repairs','result':'Preserved and north r10-to-r11 boundary visually continuous across all four 1024-wide segments.'},{'name':'Second-row x2048 tone repair','result':'Applied correctly; original red fragments and grout geometry retained.'},{'name':'p04_02 incomplete diagonal repair','result':'T-junction continuous after full assembly; patch exact at context [1334,3582,1864,4037].'},{'name':'Source isolation','result':'All seven listed geometry failures are pixel-identical to the original full candidate at their issue boxes; they were not introduced by the applied repairs.'}],'preservedInvariants':{'contextOutsideTwoSpecifiedRegionsExact':True,'contextRows2048to2278Exact':True,'p04_02FourOuter230BandsOriginal':True,'noResizing':True,'noColorAdjustmentInMechanicalAssembly':True,'noNativeSelectionProgressWrites':True,'r10OriginalSha256':'f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'},'newImageGenerationCalls':0,'furtherGenerationAuthorizedForThisPhase':False,'independentReviewer':'/root/sw_boundary_qa/lower_geometry_review','nextAction':'Retain as a repair candidate. Do not mark internal geometry passed or formal acceptance. Subsequent work must correct listed free endpoints and offsets before renewed full review.'}
for inp in assembly['inputs'].values():assert sha(inp['path'])==inp['sha256']
assert sha(SW/'r10_c05/repairs/output/r10_c05.repaired.candidate.png')==review['preservedInvariants']['r10OriginalSha256']
jsave(D/'qa/full-visual-review.json',review)
result={'status':'complete-candidate-composite-but-internal-QA-failed','formalAccepted':False,'internalPassed':False,'outputs':assembly['outputs'],'assembly':str(D/'output/assembly.json'),'assemblySha256':sha(D/'output/assembly.json'),'visualReview':str(D/'qa/full-visual-review.json'),'visualReviewSha256':sha(D/'qa/full-visual-review.json'),'geometryIssueCount':7,'materialIssueCount':1,'newImageGenerationCalls':0,'sourceFilesUnmodified':True}
jsave(D/'production-result.json',result)
print(json.dumps(result,indent=2))

