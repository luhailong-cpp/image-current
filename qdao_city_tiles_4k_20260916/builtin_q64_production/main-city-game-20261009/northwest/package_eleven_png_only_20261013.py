from pathlib import Path
import json,hashlib,zipfile
Z=Path(__file__).resolve().parent;FULL=Z/'verified-eleven-tiles-20261012/2f0946e391eb1655';D=Z/'verified-eleven-png-only-20261013';D.mkdir();
def sha(f):
 with Path(f).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
package=json.loads((FULL/'package.json').read_text());summary=json.loads((FULL/'delivery-summary.json').read_text());tiles=summary['tiles'];assert len(tiles)==11;files=[]
for t in tiles:
 assert sha(t['file'])==t['sha256'];files.append({'originalFile':t['file'],'zipEntry':t['tile']+'-4096.png','sha256':t['sha256']})
manifest={'tileCount':11,'tilePixels':[4096,4096],'files':list(files),'completeEvidencePackage':{'file':package['file'],'sha256':package['sha256']},'ownedTargetTiles':60,'internallyPassedTiles':11,'fullSourceCandidates':12,'missingSourceTiles':48,'missingNativePatches':768,'completeSourceTilePendingRepair':'r07_c06','wholeZoneComplete':False,'formalAccepted':False,'productionBytesUnmodified':True}
mf=D/'delivery-summary.json';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert json.loads(mf.read_text())==manifest
files.append({'originalFile':str(mf),'zipEntry':mf.name,'sha256':sha(mf)});out=D/'northwest-eleven-4k-pngs.zip'
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_STORED) as archive:
 for f in files:archive.write(f['originalFile'],f['zipEntry'])
with zipfile.ZipFile(out) as archive:
 assert archive.testzip() is None
 for f in files:
  with archive.open(f['zipEntry']) as h:assert hashlib.file_digest(h,'sha256').hexdigest()==f['sha256']==sha(f['originalFile'])
 assert json.loads(archive.read('delivery-summary.json'))==manifest
proof={'archive':str(out),'sha256':sha(out),'sizeBytes':out.stat().st_size,'verifiedEntries':len(files),'zipCRCVerified':True,'allEntrySHA256Verified':True,'allProductionPNGsByteIdentical':True,'wholeZoneComplete':False};(D/'verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
