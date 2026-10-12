"""Export exact pixel QA crops; never modify production images or acceptance."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ZONE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("assembly", ZONE / "assemble.py")
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)
OUT = ZONE / "qa" / "south-join-20261010"
OUT.mkdir(exist_ok=True)

def emit(image, name, source_box, sources):
    path = OUT / name
    image.save(path)
    return {"file": str(path), "sha256": assembly.sha(path), "pixels": list(image.size),
            "sourceWorldBox": source_box, "sources": sources, "resized": False}

evidence = {"createdAtUtc": datetime.now(timezone.utc).isoformat(),
            "operation": "strict verified native core crops and integer placement; no resampling",
            "formalAcceptedCount": 0, "sources": [], "artifacts": [], "overlapMetrics": []}
upper_tile, upper_plan = assembly.load_plan("r05_c13")
lower_tile, lower_plan = assembly.load_plan("r06_c13")
upper_sources, upper_evidence, _, upper_invalid = assembly.inspect_sources(upper_tile, upper_plan)
lower_sources, lower_evidence, _, lower_invalid = assembly.inspect_sources(lower_tile, lower_plan)
assert not upper_invalid and not lower_invalid
all_evidence = {("r05_c13", e["id"]): e for e in upper_evidence}
all_evidence.update({("r06_c13", e["id"]): e for e in lower_evidence})
for col in range(1, 5):
    a, b = upper_sources[f"p4{col}"], lower_sources[f"p1{col}"]
    refs = [all_evidence[("r05_c13", f"p4{col}")], all_evidence[("r06_c13", f"p1{col}")]]
    evidence["sources"].extend(refs)
    join = Image.new("RGB", (1024, 768))
    join.paste(a.crop((115, 755, 1139, 1139)), (0, 0))
    join.paste(b.crop((115, 115, 1139, 499)), (0, 384))
    x = 49152 + (col - 1) * 1024
    evidence["artifacts"].append(emit(join, f"c{col}-external-join-100pct.png",
                                            [x, 20096, x + 1024, 20864], refs))
    evidence["artifacts"].append(emit(a.crop((115, 115, 1139, 1139)),
                                            f"upper-p4{col}-core-100pct.png",
                                            [x, 19456, x+1024, 20480], [refs[0]]))
    evidence["artifacts"].append(emit(b.crop((115, 115, 1139, 1139)),
                                            f"lower-p1{col}-core-100pct.png",
                                            [x, 20480, x+1024, 21504], [refs[1]]))
    evidence["overlapMetrics"].append({"column": col, **assembly.difference_metrics(
        a.crop((0, 1024, 1254, 1254)), b.crop((0, 0, 1254, 230)))})

# All first-row internal joins are also native pixels, spanning full core height.
for col in range(1, 4):
    a, b = lower_sources[f"p1{col}"], lower_sources[f"p1{col+1}"]
    join = Image.new("RGB", (384, 1024))
    join.paste(a.crop((947, 115, 1139, 1139)), (0, 0))
    join.paste(b.crop((115, 115, 307, 1139)), (192, 0))
    x = 49152 + col*1024
    refs = [all_evidence[("r06_c13", f"p1{col}")], all_evidence[("r06_c13", f"p1{col+1}")]]
    evidence["artifacts"].append(emit(join, f"lower-internal-c{col}-100pct.png",
                                            [x-192, 20480, x+192, 21504], refs))
    evidence["overlapMetrics"].append({"pair": [f"p1{col}", f"p1{col+1}"],
        **assembly.difference_metrics(a.crop((1024, 0, 1254, 1254)), b.crop((0, 0, 230, 1254)))})

path = OUT / "pixel-evidence.json"
path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(path), "crops": len(evidence["artifacts"]),
                  "overlapMetrics": evidence["overlapMetrics"]}, ensure_ascii=False, indent=2))
