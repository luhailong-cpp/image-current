from pathlib import Path
from PIL import Image
import json,hashlib,re
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
versions=[]
for i in range(3,9):
 version=f'fix{i:02d}';D=B/version;p=D/'generated.png'
 params=json.loads((D/'parameters.json').read_text(encoding='utf-8'))
 receipt=json.loads((D/'tool-result.json').read_text(encoding='utf-8'))
 match=re.search(r' as (.+?\.png) by default',receipt['output_hint'])
 host=Path(match.group(1)) if match else None
 with Image.open(p) as im:
  size=list(im.size);mode=im.mode;fmt=im.format;opaque=im.convert('RGBA').getchannel('A').getextrema()==(255,255)
 refs=[{'file':str(Path(x).resolve()),'sha256':sha(x),'pixels':list(Image.open(x).size),'actuallySubmitted':True} for x in params['referenced_image_paths']]
 record={'id':'s04_01_'+version,'tile':'r04_c04','logicalPatch':'s04_01','file':str(p),'sha256':sha(p),'width':size[0],'height':size[1],
         'mode':mode,'format':fmt,'opaque':opaque,'nativeSizeVerified':size==[1254,1254],'copiedUnchangedFromHost':bool(host and sha(host)==sha(p)),
         'hostOutputPath':str(host),'route':'builtin_image_gen','tool':'image_gen.imagegen','generatedAt':None,
         'recordedAt':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None,
         'modelEvidence':'Returned tool keys were image_url and output_hint; no execution model or quality was disclosed.',
         'parameters':str(D/'parameters.json'),'parametersSha256':sha(D/'parameters.json'),'prompt':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),
         'receipt':str(D/'tool-result.json'),'receiptSha256':sha(D/'tool-result.json'),
         'receiptFormat':'Exact output_hint plus returned-key list; encoded image payload omitted and original PNG preserved byte-for-byte.',
         'references':refs,'preparation':str(D/'preparation.json'),'preparationSha256':sha(D/'preparation.json'),
         'worldBoxWithHalo':[12173,15245,13427,16499],'coreWorldBox':[12288,15360,13312,16384],'coreCrop':[115,115,1139,1139],
         'resizedAfterGeneration':False,'finalArtUpscaled':False,'selectionUpdated':False,'sharedProgressUpdated':False,'formalAccepted':False,
         'status':'unaccepted_repair_candidate' if i in [7,8] else 'rejected_repair_revision'}
 dest=D/'generation-evidence.json'
 if dest.exists():raise FileExistsError(dest)
 dest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 versions.append({'version':version,'file':str(p),'sha256':record['sha256'],'pixels':size,'originalHostBytesVerified':record['copiedUnchangedFromHost']})
summary={'tile':'r04_c04','patch':'s04_01','newNativeGenerations':6,'versions':versions,'bestAvailableVersion':'fix08',
         'originalRepairRequested':'Restore native south-boundary continuity with northwest/r05_c04/native/s01_01.png',
         'taskOutcome':'Substantial geometry improvement but visible residual seam defects remain; repair is not complete',
         'passedFormalAcceptance':False,'ingestedBySubagent':False,'sharedProgressModified':False,'selectionModified':False,
         'observedViews':['All six generated full native outputs','Individual native rail-boundary crops for fix03/04/06/07/08; full native hard-boundary strips for fix07/08; fix05 rejected from its full generated image',
                          'fix07/fix08 minimum-error native boundary pairs'],
         'rejectedRevisions':{'fix03':'Imported the southern rail ornamental end panel into the wrong world coordinate',
                              'fix04':'Rail right outside boundary remains about32px too far right',
                              'fix05':'Rail became substantially too narrow instead of matching fixed edge',
                              'fix06':'Right rail boundary retains11-16px offset and the y1024splice remains'},
         'bestAvailable':{'fix07':'Right outside edge is0-3px from actual neighbor in representative overlap rows; left groove and shade still jump',
                          'fix08':'Same improved right outside edge; overlapMAE6.8775 versus original fix02MAE15.6509; left-side improvement but right inset has visible small kink near local y1024 and hard-core seam still shows a shade/groove step'},
         'minimumErrorQA':'Both fix07 and fix08 still show visible jagged source-selection boundaries at native scale; binary seam optimization does not grant continuity acceptance.',
         'practicalLimitation':'Repeated built-in edits did not honor exact preservation of the real230pxanchor despite direct native context, cropped edge references, and explicit edit-mask guides. Do not claim the fixed border was unchanged.',
         'nextStep':'Parent may ingest fix08 as explicitly unaccepted improvement, or retain the current selection; root-controlled coordinated boundary repair remains required before formal acceptance.'}
(B/'repair-handoff.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'nativeGenerations':len(versions),'allOriginalHostBytesVerified':all(v['originalHostBytesVerified'] for v in versions),'summary':str(B/'repair-handoff.json'),'best':str(B/'fix08/generated.png'),'formalAccepted':False},indent=2))
