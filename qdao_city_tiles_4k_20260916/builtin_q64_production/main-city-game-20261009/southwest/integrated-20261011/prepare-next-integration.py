from pathlib import Path
import json,sys
B=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
D=B/"integrated-20261011"
old=(D/"integrate.py").read_text()
old=old.replace("for key in ('base','nativeSource','premixed','pasteMask','proposal'):", "for key in ('base','premixed','pasteMask','proposal'):")
old=old.replace("  patch=image(m['premixed']['file'])", "  if 'nativeSource' in m:checked(m['nativeSource']['file'],m['nativeSource']['sha256'])\n  for item in m.get('sourceRegions',[]):checked(item['source']['file'],item['source']['sha256'])\n  patch=image(m['premixed']['file'])")
target=D/"integrate-v5.py";assert not target.exists();target.write_text(old,encoding="utf-8")
a=json.loads((D/"v4/assembly.json").read_text())
tiles={t:{"candidate":e["candidate"]["file"],"sha256":e["candidate"]["sha256"],"context":e["context"]["file"],"contextSha256":e["context"]["sha256"]} for t,e in a["outputs"].items()}
cfg={"version":"v5","tiles":tiles,"overlays":[{"kind":"local-premixed","id":"G01-object-plane","manifest":str(B/"r11_c06/repairs-restored-20261011/G01-object-plane.proposal.json")},{"kind":"color","id":"stair-first-bevel","manifest":str(B/"pipeline-tools/stair-short-bevels-local/proposal.json")}],"remainingIssues":["north_vertical short bevel at worldy40734 remains pending.","south_vertical material consistency pending.","Broad dense woven stone material remains pending throughout affected existing candidates.","r10_c06 guide object fragment and red sliver pending.","r11_c06 G02/G06 paving geometry still requires review.","64 tile native coverage incomplete; formal acceptance0.","Remaining cross-region neighbors not yet available."],"intentionalRebases":{}}
atomic_json(D/"integration-inputs-v5.json",cfg)
print(str(target))
