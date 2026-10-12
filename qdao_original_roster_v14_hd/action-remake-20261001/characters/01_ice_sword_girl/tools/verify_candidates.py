from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'candidate/manifest.json').read_text(encoding='utf-8'))
selection=json.loads((R/'review/run-E-selection.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for f in manifest['files']:
    p=R/f['path'];im=Image.open(p);im.load();a=im.getchannel('A');rec=json.loads((R/f['generationRecord']).read_text(encoding='utf-8'))
    source=R/rec['derivedFrom']['file'];nativeRec=json.loads((R/rec['derivedFrom']['generationRecord']).read_text(encoding='utf-8'))
    edges=[(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)]
    rows.append({'frame':f['frame'],'path':f['path'],'size':list(im.size),'mode':im.mode,'alpha':list(a.getextrema()),'shaMatches':sha(p)==f['sha256']==rec['sha256'],'sourceShaMatches':sha(source)==rec['derivedFrom']['sha256']==nativeRec['sha256'],'nativeSize':nativeRec['nativeFrameSize'],'actualModel':nativeRec['actualModel'],'actualQuality':nativeRec['actualQuality'],'evidencePresent':bool(nativeRec.get('evidence')),'edgeAlphaMax':max(a.crop(b).getextrema()[1] for b in edges),'pixelSha256':hashlib.sha256(im.tobytes()).hexdigest()})
report={'selectedCount':len(rows),'distinctPixelCount':len(set(x['pixelSha256'] for x in rows)),'technicalFormatPass':len(rows)==16 and all(x['size']==[1024,1024] and x['mode']=='RGBA' and x['alpha']==[0,255] and x['shaMatches'] and x['sourceShaMatches'] and x['evidencePresent'] for x in rows),'timingTotalMs':sum(selection['timing']['frameDurationsMs']),'rightToLeftContactMs':sum(selection['timing']['frameDurationsMs'][:7]),'leftToRightContactMs':sum(selection['timing']['frameDurationsMs'][7:]),'frames':rows,'artAcceptance':False,'formalApprovedCount':0,'clientRuntimeVerified':False}
(R/'review/technical-candidates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'}))
assert report['technicalFormatPass'] and report['distinctPixelCount']==16 and report['timingTotalMs']==1200
assert selection['timing']['frameDurationsMs']==[75]*16
assert report['rightToLeftContactMs']==525 and report['leftToRightContactMs']==675
