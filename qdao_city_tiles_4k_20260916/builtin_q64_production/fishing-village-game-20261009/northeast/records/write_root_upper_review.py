from pathlib import Path
import datetime, hashlib, json

z = Path(__file__).resolve().parents[1]
q = z / 'qa/r06_c12'
def ref(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

observations = {
    'p11': 'Overall geometry continuous. Small abrupt stone-edge/texture change near core x397,y330 at bridge insertion remains a minor observation; no formal acceptance.',
    'p12': 'Fish bodies, partition and paving geometry appear continuous through the inspected core.',
    'p13': 'Joint bridge removes previous central paving mismatch. Fish bodies and internal divider appear continuous.',
    'p14': 'Central paving joints continuous after bridge; warm bright joints still require material-style review.',
    'p21': 'Major geometry continuous; repeated pale lattice texture and local tone differences remain material observations.',
    'p22': 'Center fish body and gold front rim now connect. At core x397 in lower wood section the bridge insertion still changes timber tone/brushwork abruptly.',
    'p23': 'FAIL: visible vertical timber tone/brushwork step at core x627, approximately y600..1024, at bridge right insertion. Central rim repair does not make the whole core seamless.',
    'p24': 'FAIL: visible vertical timber tone/brushwork step near core x129, starting around y440 and extending downward, inherited from anchored edit boundary. Gold paving joints also differ from weak grey-joint target.'
}
cores = []
for patch, detail in observations.items():
    item = ref(q / 'cores' / f'{patch}.native-1to1.png')
    item.update(patch=patch, nativePixels=[1024,1024], inspectedAtPixelScale=1,
                observation=detail, blocksWholeTileAcceptance=patch in ['p22','p23','p24'], formalAccepted=False)
    cores.append(item)
edges = []
for row in [1,2]:
    for col in [1,2,3]:
        key = f'v_p{row}{col}_p{row}{col+1}'
        item = ref(q / f'{key}.native-1to1.png')
        item.update(edge=key, nativePixels=[256,1024], inspectedAtPixelScale=1,
                    coreBoundaryGeometry='No obvious new break exactly at x128',
                    observation=('p24 anchor-to-new-art tone step appears near strip right edge; core boundary alone is insufficient.'
                                 if key=='v_p23_p24' else 'Shared core boundary geometry appears continuous at native scale.'),
                    formalAccepted=False)
        edges.append(item)
out = dict(reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='root',
           candidate=ref(z/'tiles/r06_c12.candidate.png'),coreReviews=cores,verticalBoundaryReviews=edges,
           conclusion='Upper core joins improved, but internal edit-insertion tone/brushwork steps block whole-tile acceptance.',
           complete4k=False,formalAccepted=False)
(q/'upper-core-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cores':len(cores),'verticalEdges':len(edges),'formalAccepted':False}))
