"""Archive native candidate and export only explicitly reviewed W attack repairs."""
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT = Path(__file__).resolve().parent
index = int(sys.argv[1])
assert 1 <= index <= 6
suffix = sys.argv[2] if len(sys.argv) > 2 else ""
stem = f"{index:02}.guardfix-20261008{suffix}"
jobpath = ROOT / "records" / "attack-W" / f"{stem}.job.json"
job = json.loads(jobpath.read_text(encoding="utf-8"))
source = Path(job["source"])
job["generatedAt"] = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat()
jobpath.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
candidate = jobpath.with_name(f"{stem}.generation.json")
subprocess.run([sys.executable, str(ROOT / "record_native_candidate.py"), str(jobpath), str(candidate)], check=True)
if "--candidate-only" in sys.argv:
    record = json.loads(candidate.read_text(encoding="utf-8"))
    record["disposition"] = "not selected after static comparison; current final export retained"
    candidate.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidateOnly": str(candidate)}))
    sys.exit(0)
subprocess.run([sys.executable, str(ROOT / "export_frame.py"), str(jobpath)], check=True)
record = json.loads(candidate.read_text(encoding="utf-8"))
record["disposition"] = "selected after static native visual inspection; final export inspected separately"
record["exportedTo"] = f"runtime/attack/W/{index:02}.png"
record["currentRecord"] = f"records/attack-W/{index:02}.generation.json"
candidate.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
