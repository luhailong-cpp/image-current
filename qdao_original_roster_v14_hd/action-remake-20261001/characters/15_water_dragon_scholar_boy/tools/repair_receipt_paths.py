"""Resolve incorrectly suffixed receipt references to the existing actual tool receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    manifest=read(ROOT/'manifest.json'); changes=[]
    for r in manifest['frames']:
        gp=ROOT/r['derivedFrom']['generationRecord'];g=read(gp)
        old=g.get('evidence',{}).get('toolResult','')
        if not old.endswith('.tool.json') or (ROOT/old).is_file():continue
        new=old[:-len('.tool.json')]+'.json';receipt=ROOT/new
        assert receipt.is_file(),new
        read(receipt)
        assert g['sha256']==r['derivedFrom']['sha256']==sha(ROOT/r['source'])
        dp=ROOT/r['derivedRecord'];d=read(dp)
        assert d['originalGenerationRecord']==g
        prior=sha(gp);g['evidence']['toolResult']=new;write(gp,g)
        d['originalGenerationRecord']=g;d['derivedFrom']['generationRecordSha256']=sha(gp);write(dp,d)
        changes.append({'slot':r['slot'],'generationRecord':gp.relative_to(ROOT).as_posix(),'previousReceiptPath':old,'actualReceiptPath':new,'actualReceiptSha256':sha(receipt),'previousGenerationRecordSha256':prior,'generationRecordSha256':sha(gp),'sourceSha256Unchanged':g['sha256']})
    write(ROOT/'provenance/receipt-path-repairs-20261004.json',{'at':datetime.now(timezone.utc).isoformat(),'operation':'only repair missing .tool.json path to existing actual .json receipt; original generation time, tool, route, pixels, prompt, references and returned model/quality unchanged','changes':changes})
    print(f'Repaired {len(changes)} receipt paths.')
if __name__=='__main__':main()
