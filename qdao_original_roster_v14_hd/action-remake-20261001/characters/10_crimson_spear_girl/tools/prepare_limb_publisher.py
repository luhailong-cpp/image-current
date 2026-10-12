from pathlib import Path
R=Path(__file__).resolve().parents[1]
text=(R/'tools/publish_axis_revision.py').read_text(encoding='utf-8')
text=text.replace('run-axis-revision-20261004','full-limb-review-20261004')
start=text.index("required={'run/NE/01'")
end=text.index('prepared={}',start)
text=text[:start]+"""approval=load(W/'approved-slots.json')
required=set(approval['slots'])
assert approval['status']=='visually-approved' and required
assert set(selected)==required,'Selection differs from the independently reviewed approval set'
assert sha(R/'delivery-current.json')==approval['beforeInventorySHA256'],'Runtime changed after visual approval'
"""+text[end:]
text=text.replace("assert slot in rows and slot.startswith('run/')","assert slot in rows")
text=text.replace("frameDurationMs=75","frameDurationMs=rows[slot]['durationMs']")
text=text.replace("contactRevision='20261004-leg-axis'","fullLimbRevision='20261005-anatomy'")
text=text.replace("'battleUnchanged':True","'battleUnchanged':all(not x['slot'].startswith(('hit/','attack/','cast/')) or x['oldSHA']==x['newSHA'] for x in summary)")
text=text.replace("source_frame=int(slot.split('/')[-1]);meta={}","source_frame=int(slot.split('/')[-1]);meta={}")
(R/'tools/publish_limb_revision.py').write_text(text,encoding='utf-8')
print('Prepared guarded full-limb publisher; no runtime files changed')
