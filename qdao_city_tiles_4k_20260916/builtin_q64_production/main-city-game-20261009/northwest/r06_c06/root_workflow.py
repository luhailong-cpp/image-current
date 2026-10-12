from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
ap=argparse.ArgumentParser()
ap.add_argument("action",choices=["ingest","prepare"])
ap.add_argument("--id")
ap.add_argument("--reason",default="Native image inspected; full seam and junction QA pending.")
ap.add_argument("--patch")
ap.add_argument("--version",default="")
ap.add_argument("--edges",default="all")
a=ap.parse_args()
tile="r06_c06"
d=p.ZONE/tile
if a.action=="ingest":
    receipt=d/"receipts"/(a.id+".host-result.json")
    r=p.read(receipt)
    import re
    source=re.search(r"as ([^\r\n]+?\.png) by default",r["output_hint"]).group(1)
    output=p.ingest(tile,a.id,source,receipt)
    p.record_selection(tile,a.id[:6],a.id,a.reason)
    print(json.dumps(output))
else:
    output=p.prepare(tile,a.patch,a.version,a.edges)
    print(json.dumps({k:output[k] for k in ("guide","nativeAnchors","missingNeighborSlots")}))

