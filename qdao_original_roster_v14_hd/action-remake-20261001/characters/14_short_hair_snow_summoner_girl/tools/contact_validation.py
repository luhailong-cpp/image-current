"""Validate current SHA-bound human visual evidence, without inferring contact from pixels."""
from pathlib import Path
import hashlib,json

def validate_contact(root, direction, require_preview=True):
    root=Path(root)
    spatial_path=root/'audit/spatial-contact-requirement.json'
    if spatial_path.exists():
        spatial=json.loads(spatial_path.read_text(encoding='utf-8-sig'))
        assert [s['frames'] for s in spatial['segments']]==[[2*i+1,2*i+2] for i in range(8)], 'Unexpected latest spatial requirement'
        timing=json.loads((root/'run-timing.json').read_text(encoding='utf-8'))
        assert spatial['frameDurationMs']==timing['frameDurationMs'] and spatial['cycleMs']==timing['defaultCycleMs']
    path=root/'audit'/f'contact-{direction}-review.json'
    review=json.loads(path.read_text(encoding='utf-8-sig'))
    assert review['direction']==direction, path
    expected='passed_offline_four_spatial_pairs' if require_preview else 'static_pending_root_preview'
    assert review['status']==expected, (path,review['status'])
    rows=review['frames']
    assert len(rows)==16 and len({r['file'] for r in rows})==16, path
    hashes={}
    for row in rows:
        file=Path(row['file'])
        assert file.as_posix() in {f'run/{direction}/{n:02d}.png' for n in range(1,17)}, file
        actual=hashlib.sha256((root/file).read_bytes()).hexdigest()
        assert actual==row['sha256'], ('Contact evidence changed',file)
        hashes[int(file.stem)]=actual
    contacts=review['contacts']
    assert len(contacts)==2 and len({c['supportLeg'] for c in contacts})==2, path
    for index,contact in enumerate(contacts):
        frames=contact['frames']
        assert frames==list(range(index*8+1,index*8+9)), contact
        assert all(1<=n<=16 for n in frames), contact
        assert all(b==a%16+1 for a,b in zip(frames,frames[1:])), contact
        assert len({hashes[n] for n in frames})==len(frames), contact
        assert contact.get('observations'), contact
    pairs=review['positionPairs']
    assert len(pairs)==8, path
    for index,pair in enumerate(pairs):
        assert pair['frames']==[index*2+1,index*2+2], pair
        assert pair['position']==f'P{index%4+1}', pair
        assert pair['supportLeg']==contacts[index//4]['supportLeg'], pair
        assert pair.get('observations'), pair
    if require_preview:
        assert review.get('rootPreview'), ('Missing actual root preview evidence',path)
    return review
