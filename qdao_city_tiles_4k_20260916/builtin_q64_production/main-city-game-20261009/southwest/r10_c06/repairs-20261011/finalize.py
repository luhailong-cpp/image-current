from pathlib import Path
from PIL import Image
import numpy as np,json,sys,shutil
sys.path.insert(0,str(Path(__file__).parent))
import repair
R=repair.R;T=repair.T;qa=R/'qa';qa.mkdir(exist_ok=True)
selected=R/'green-relief-v01/r10_c06.candidate.png'
out=R/'output';out.mkdir(exist_ok=True)
dest=out/'r10_c06.repaired.candidate.png';shutil.copyfile(selected,dest)
basecontext=T/'pipeline/output/5c4d9d81c6fcc1ca/r10_c06.candidate.context.png'
ctx=Image.open(basecontext).convert('RGB');assert ctx.size==(4326,4326)
im=Image.open(dest).convert('RGB');ctx.paste(im,(115,115))
context=out/'r10_c06.repaired.candidate.context.png';ctx.save(context,optimize=True)
for name,box in [('repair-joint-upper-left',(1950,2440,2380,2870)),('repair-joint-lower-left',(1950,3500,2380,3900)),('repair-joint-right',(3100,2760,3400,3830)),('panel-perimeter',(2680,3150,4096,4096))]:
 im.crop(box).save(qa/(name+'.png'))
for val in (1024,2048,3072):
 im.crop((0,val-115,4096,val+115)).save(qa/('horizontal-y'+str(val)+'.png'))
 im.crop((val-115,0,val+115,4096)).save(qa/('vertical-x'+str(val)+'.png'))
a=np.array(im);b=np.array(Image.open(repair.BASE).convert('RGB'))
border=np.zeros((4096,4096),bool);border[:115]=True;border[-115:]=True;border[:,:115]=True;border[:,-115:]=True
origsummary=T/'qa/production-summary.json'
hist=T/'qa/production-summary.before-local-repairs-20261011.json'
if not hist.exists():shutil.copyfile(origsummary,hist)
summary=repair.read(hist)
summary.update({'reviewedAtUtc':repair.now(),'toolReturnedImages':22,'selectedNativeCount':16,'selectedLocalRepairCount':2,'rejectedNativeCount':4,'failedCalls':0,'output':str(dest),'outputSha256':repair.sha(dest),'contextOutput':str(context),'contextOutputSha256':repair.sha(context),'localRepairInspectionPassed':True,'visualQaPassed':False,'formalAccepted':False,'externalSeamsReviewed':False,
'inspection':['Whole repaired candidate','Exact seam crop around y3072 covering repaired stone plane','Green panel at native detail scale','Four repair perimeter crops'],
'resolvedIssues':[{'location':'core y~3072, x~2100-3100','finding':'Native image edit removed scalloped grey tone transition and discontinuous diagonal shadow.'},{'location':'p04_03/p04_04 green panel','finding':'Native image edit removed invented round floral relief; retained original flat green inset and pale stone framing.'}],
'issues':[{'severity':'P2','location':'p04_03 south boundary','finding':'Original guide red/brown object fragment is still replaced by pale stone in current candidate. Needs coordinated r10_c06/r11_c06 boundary repair; not attempted here to preserve boundary.'},{'severity':'P2','location':'p04_02 bottom/halo red sliver','finding':'Blurred red arc straddles south boundary. Needs coordinated neighbor repair.'},{'severity':'P3','location':'p02_04,p03_01,p03_02','finding':'Inherited dense cellular stone and repetitive gold texture; untouched by current localized fixes.'}],
'formalAcceptanceNote':'Complete candidate with two visually checked local repairs. Tile-wide layout QA remains not passed due to south-boundary omissions. External seam review remains parent-owned.',
'localRepairs':[str(R/n/'generation.json') for n in ('stone-seam-v01','green-relief-v01')],
'assemblyRecords':[str(R/n/'assembly.json') for n in ('stone-seam-v01','green-relief-v01')],
'outerEdgesUnchanged':True,'outer115pxBandChangedPixels':int(np.any(a!=b,axis=2)[border].sum()),'sourceResampling':False,'maximumFeatherRadiusPixels':2})
repair.write(origsummary,summary)
report={'status':'two_local_repairs_complete_candidate_ready_for_parent_review','candidate':str(dest),'sha256':repair.sha(dest),'context':str(context),'contextSha256':repair.sha(context),'nativeSize':[1254,1254],'candidateSize':[4096,4096],'newSuccessfulBuiltinCalls':2,'newRejectedCalls':0,'newFailedCalls':0,'selectedLocalRepairs':2,'allFourOutermostEdgesUnchanged':True,'outer115pxBandChangedPixels':summary['outer115pxBandChangedPixels'],'formalAccepted':False,'entireTileVisualQaPassed':False,'localRepairInspectionPassed':True,'remainingIssues':summary['issues'],'summary':str(origsummary),'atUtc':repair.now()}
repair.write(R/'handoff.json',report);print(json.dumps(report,ensure_ascii=False))

