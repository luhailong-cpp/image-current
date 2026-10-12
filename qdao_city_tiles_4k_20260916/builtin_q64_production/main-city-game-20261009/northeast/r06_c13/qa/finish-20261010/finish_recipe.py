from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
spec=read(HERE/'records/roof-intermediate-replay.json');p=read(HERE/'p23-flower-proposal.json');v=p['integerTileOperations'][0]
assert p['pixelProof']['maskOutsideUnchanged'] and p['pixelProof']['maskBinary']
spec['operations'].append({'id':'p23-flower-corner-v1','source':v['source'],'sha256':v['sourceSha256'],'sourceCrop':v['crop'],'destinationTileXY':v['dest'],'mask':v['mask'],'maskSha256':v['maskSha256'],'maskCrop':v['maskCrop'],'generationRecord':str(HERE/'records/p23-flower-corner-v1.generation.json'),'proposalRecord':str(HERE/'p23-flower-proposal.json')})
spec['output']=str(TILE/'candidates/r06_c13.candidate.png');spec.pop('outputSha256',None);spec.pop('createdAt',None)
spec['status']='complete-4k-candidate-internal-visual-review-passed-with-P3-notes-not-formal-accepted'
spec['p43Decision']={'action':'retain-original-native','reason':'Parent and independent reviewer examined complete building context: supported protruding porch eave, with continuous beams/shadows; not a native seam defect. Rejected repair v1-v6 are not integrated.','reviewRecord':str(TILE/'qa/root-p43-repair/review-status.json')}
spec['visualReview']=str(HERE/'records/final-visual-review.json')
out=HERE/'records/candidate-replay.json';assert not out.exists();out.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)
