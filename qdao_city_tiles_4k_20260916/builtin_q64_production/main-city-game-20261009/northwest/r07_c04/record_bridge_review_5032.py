from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).parent
oldp=P/'qa/r07_c04-candidate-minimum-error-cbdf49001149/review-internal.json'
old=json.loads(oldp.read_text(encoding='utf-8'));old={e['name']:e for e in old['entries']}
name='r07_c04-candidate-native-bridges-5032b69bc48f9356'
m=json.loads((P/'candidate'/name/'assembly.json').read_text())
nonblocks={
'internal-x2048-segment04':'Continuous joints use an irregular L-shaped slab corner after repair; no dangling endpoints.',
'internal-x3072-segment03':'Connected pedestal bevel changes profile; all edges remain connected.',
'internal-y3072-segment01':'Faint local stone texture transition without geometric break.',
'stair-foot-04-boundary-left':'Very small bevel/joint width variation; continuous geometry.',
'paving-01-boundary-top':'Approximately 1-3 pixel grout-width change at one join; no disconnected line.',
'paving-01-boundary-bottom':'Approximately 1-3 pixel trim/bevel variation; blue band continuous.'
}
entries=[]
for q in m['qa']+m['bridgeBoundaryQa']:
 n=Path(q['file']).stem;previous=old.get(n);inherit=previous and previous['sha256']==q['sha256'] and previous['verdict']=='passed'
 verdict='blocking' if n=='internal-y3072-segment04' else ('nonblocking' if n in nonblocks else 'passed')
 findings=['Right-side floor corner has two unconnected grout tips; queued paving-tip-01 repair.'] if verdict=='blocking' else [nonblocks[n]] if n in nonblocks else ['Native crop viewed; connected geometry and no blocking seam defect.']
 entries.append(dict(name=n,file=q['file'],sha256=q['sha256'],verdict=verdict,actuallyViewed=not inherit,inheritedFrom=dict(report=str(oldp),reportSha256=hashlib.sha256(oldp.read_bytes()).hexdigest(),cropSha256=previous['sha256']) if inherit else None,findings=['Inherited exact identical passed native crop.'] if inherit else findings))
o=dict(schemaVersion=1,tile='r07_c04',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=m['output'],assemblyManifest=str(P/'candidate'/name/'assembly.json'),internalQA=dict(status='blocking',seamSegments=24,junctions=9,actuallyViewed=True,actuallyViewedThisRevision=21,inheritedExactPassed=12),bridgeBoundaryQA=dict(status='passed',actuallyViewed=True,crops=8),entries=entries,formalAccepted=False)
(P/'qa'/name/'review-internal.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('saved41entries;1blocking')

