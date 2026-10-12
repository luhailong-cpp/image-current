from pathlib import Path
from PIL import Image
import hashlib, json
import numpy as np

p = Path(__file__).parent
file = p/'seam02-raw-v1.png'
sha = lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
im = Image.open(file)
guide = Image.open(p/'seam02-center-guide.png')
assert im.size == guide.size == (1254,1254)
ar,gr = np.array(im.convert('RGB')).astype(float), np.array(guide.convert('RGB')).astype(float)
im.crop((620,427,970,827)).save(p/'seam02-v1-tassel-native.png')
im.crop((0,507,1254,747)).save(p/'seam02-v1-wall-native.png')
topbottom = Image.new('RGB',(1254,800))
topbottom.paste(im.crop((0,0,1254,400)),(0,0))
topbottom.paste(im.crop((0,854,1254,1254)),(0,400))
topbottom.save(p/'seam02-v1-outer-bands-native.png')
stats = {'centerBoundaryMeanAbsRGBBefore':float(np.abs(gr[626]-gr[627]).mean()),'centerBoundaryMeanAbsRGBAfter':float(np.abs(ar[626]-ar[627]).mean()),'outerTopMeanAbsRGBvsGuide':float(np.abs(ar[:400]-gr[:400]).mean()),'outerBottomMeanAbsRGBvsGuide':float(np.abs(ar[880:]-gr[880:]).mean())}
evidence = {'file':str(file),'sha256':sha(file),'size':list(im.size),'mode':im.mode,'format':im.format,'worldBox':[12173,13709,13427,14963],'nativeOutput':True,'resizedAfterGeneration':False,'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'unknownReason':'Built-in receipt discloses output and save-path hint, no actual model or quality fields.','hostOutputPath':'C:/Users/luyua/.codex/generated_images/01a125b1-411b-73b1-95c9-a9dcad714b5a/exec-1d8c861e-8e05-4d79-9b6a-0311d1de4a91.png','reference':{'file':str(p/'seam02-center-guide.png'),'sha256':sha(p/'seam02-center-guide.png'),'provenance':str(p/'guide-provenance.json')},'submittedParameters':str(p/'seam02-v1-parameters.json'),'prompt':str(p/'seam02-v1-prompt.txt'),'receipt':str(p/'seam02-v1-tool-result.json'),'receiptSha256':sha(p/'seam02-v1-tool-result.json'),'pngMetadata':im.info,'diagnostics':stats,'status':'center_repair_candidate_pending_outer_join_QA','formalAccepted':False}
(p/'seam02-v1-native-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(evidence,ensure_ascii=False))
