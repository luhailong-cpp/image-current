"""Record r09_c13 actual review and source audit; does not promote the candidate."""
from pathlib import Path
from workflow import ROOT,read,write,sha,now,progress
from PIL import Image
tid='r09_c13'
index=read(ROOT/'qa'/f'{tid}.review-index.json')
failed={'r09_c13-p22-p32':'Upper beam gold top face stops at horizontal cut; thick post right edge/width differs roughly 30 pixels.','r09_c13-p32-p42':'Thick post edges shift about 10-25 pixels at horizontal cut; grain/tone also changes.'}
for item in index['seams']:
 item['status']='needs_native_repair' if item['id'] in failed else 'self_review_candidate_pass'
 item['note']=failed.get(item['id'],'Observed at native size: contours cross the core cut without a conspicuous split. This is a local candidate check, not full-zone approval.')
 rec=read(Path(item['record']));rec['status']=item['status'];rec['visualReview']={'reviewedAt':now(),'reviewer':'tile_right production agent','scope':'actual core cut; halo outside core is context only','note':item['note']};write(Path(item['record']),rec)
index.update({'reviewedAt':now(),'reviewer':'tile_right','internalCandidatePassCount':22,'internalNeedsRepairCount':2,'leftExternalCandidatePassCount':4,'junctions':[{'id':f'{r}{c}','status':'needs_native_repair' if (r,c) in [(2,2),(3,2)] else 'self_review_candidate_pass'} for r in range(1,4) for c in range(1,4)],'candidateStatus':'full_native_coverage_needs_two_structural_seam_repairs','formalAccepted':False,'unverifiedExternalEdges':['top','right','bottom'],'repairAttempts':{'p32_v02':'Rejected for selection: post movement partially improved but still does not match p42 exactly.','p22_v02':'Rejected for selection: post was narrowed in wrong direction and lower beam still differs.'}})
write(ROOT/'qa'/f'{tid}.review-index.json',index)
dispositions={'p21_v01':'Rejected: upper crossbeam stepped at x240. Replaced by p21v02.','p41_v01':'Rejected: added tassels and pendants. Replaced by p41v02.','p13_v01':'Rejected: invented paving. Replaced by p13v02.','p33_v01':'Rejected: added stone pillar and finial.','p33_v02':'Rejected: misidentified rear timber upright as tree stem. Replaced by p33v03.','p32_v02':'Not selected: structural edge repair incomplete.','p22_v02':'Rejected: attempted seam repair worsened post alignment.'}
selection=read(ROOT/f'selected-native-{tid}.json')
selection.update({'internalEdgesAccepted':False,'externalEdgesAccepted':False,'formalAccepted':False,'review':str(ROOT/'qa'/f'{tid}.review-index.json'),'remainingIssues':list(failed.values()),'candidateStatus':'full_native_coverage_needs_two_structural_seam_repairs'})
write(ROOT/f'selected-native-{tid}.json',selection)
selected={Path(x['file']).name for x in selection['entries']}
audit=[]
for p in sorted((ROOT/'native').glob(f'{tid}_*.png')):
 recp=Path(str(p)+'.generation.json');rec=read(recp);req=read(ROOT/'prompts'/f'{p.stem}.request.json');receipt=read(ROOT/rec['evidence']['toolReceipt'])
 prompt=Path(rec['prompt']).read_text(encoding='utf-8')
 checks={'native1254':Image.open(p).size==(1254,1254),'hash':sha(p)==rec['sha256'],'sourceOutputHash':sha(Path(rec['sourceOutputPath']))==rec['sourceOutputSha256']==sha(p),'promptHash':sha(Path(rec['prompt']))==rec['promptSha256'],'referenceHashes':all(sha(Path(x['file']))==x['sha256'] for x in rec['references']),'actualModelQualityUnknown':rec['actualModel'] is None and rec['actualQuality'] is None,'receiptPromptExact':receipt['submittedArguments']['prompt']==prompt,'receiptPromptSameIgnoringTerminalNewline':receipt['submittedArguments']['prompt'].rstrip()==prompt.rstrip(),'receiptReferencesExact':receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]}
 rec['status']='selected_in_candidate_not_formally_accepted' if p.name in selected else 'not_selected'
 rec['disposition']=dispositions.get(p.stem.replace(tid+'_',''),'Selected native core contributes to full candidate; tile still needs two structural seam repairs.')
 write(recp,rec)
 audit.append({'file':str(p),'sha256':sha(p),'record':str(recp),'checks':checks,'status':rec['status'],'disposition':rec['disposition']})
write(ROOT/'qa'/f'{tid}.source-audit.json',{'generatedAt':now(),'generatedAttemptCount':len(audit),'selectedNativeCount':16,'candidateSha256':selection['candidateSha256'],'records':audit,'allPixelAndReferenceChecksPass':all(all(v for k,v in a['checks'].items() if k!='receiptPromptExact') for a in audit),'limitation':'p21v01 submitted prompt omitted terminal newline from saved prompt; exact actual submitted prompt remains in receipt. No model/quality selectors disclosed.'})
recp=Path(selection['candidate']+'.generation.json');rec=read(recp);rec['status']='candidate_needs_two_structural_seam_repairs';rec['review']=str(ROOT/'qa'/f'{tid}.review-index.json');write(recp,rec)
progress(status='candidate_needs_two_structural_seam_repairs',currentPatch=None,generatedNativeCount=len(audit),usableNativeCount=16,complete4kCount=1,formalAcceptedCount=0,nextStep='Full candidate and QA delivered to root; two post/beam seams remain unresolved after local native repairs; no new tiles started',lastError=None)
print({'generated':len(audit),'selected':16,'candidate':selection['candidate'],'sha256':selection['candidateSha256'],'internalPass':22,'internalNeedsRepair':2,'leftExternalPass':4,'formal':0})

