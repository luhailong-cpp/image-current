from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).parent
q=p/'qa/r07_c04-candidate-minimum-error-cbdf49001149'
blocks={
'internal-x1024-segment03':'Multiple stair nosings and risers are jagged across s03_01 / s03_02.',
'internal-x1024-segment04':'Multiple stair nosings and risers are jagged across s04_01 / s04_02.',
'internal-x2048-segment03':'Stair nosing has a jagged partial riser at bottom near row4 boundary.',
'internal-x2048-segment04':'Upper end contains false partial riser offset against pavement.',
'internal-x3072-segment03':'Two disconnected floor grout stubs near lower end.',
'internal-x3072-segment04':'Floor grout stub and blue border offset across seam.',
'internal-y2048-segment01':'Far right stair transition contains diagonal clipped wedge.',
'internal-y3072-segment01':'Far right stair boundary jagged.',
'internal-y3072-segment02':'Large diagonal mismatched stair wedge.',
'internal-y3072-segment03':'Upper left false vertical partial stair stripe.',
'internal-y3072-segment04':'Two disconnected floor grout ends at left side.',
'junction-x1024-y3072':'Stair riser and nosing kink and are torn by cut path.',
'junction-x2048-y3072':'Large false vertical step edge and jagged tread plane.',
'junction-x3072-y3072':'Two stone floor lines stop without meeting another joint.'
}
entries=[]
for f in sorted(q.glob('*.png')):
 if not (f.stem.startswith('internal-') or f.stem.startswith('junction-')): continue
 entries.append(dict(name=f.stem,file=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),verdict='blocking' if f.stem in blocks else 'passed',actuallyViewed=True,inheritedFrom=None,findings=[blocks[f.stem]] if f.stem in blocks else ['Native crop viewed; no blocking seam geometry observed.']))
candidate=p/'candidate/r07_c04-candidate-minimum-error-cbdf49001149.png'
o=dict(schema='native-visual-qa-v1',tile='r07_c04',candidateFile=str(candidate.resolve()),candidateSha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),internalQA=dict(status='blocking',actuallyViewed=True,seamSegments=24,junctions=9),externalQA=dict(status='pending',actuallyViewed=False),entries=entries,formalAccepted=False)
assert len(entries)==33
(q/'review-internal.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':len(entries),'blocking':sum(e['verdict']=='blocking' for e in entries),'report':str(q/'review-internal.json')}))

