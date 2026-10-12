from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[1]
target=root/"SHA256SUMS.txt"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if "--verify" in sys.argv:
 rows=[line.split("  ",1) for line in target.read_text(encoding="utf-8").splitlines() if line]
 bad=[]
 for digest,relative in rows:
  p=(root/relative).resolve()
  if root not in p.parents or not p.is_file() or sha(p)!=digest:bad.append(relative)
 print(f"SHA entries={len(rows)} mismatches={len(bad)}")
 if bad:print("\n".join(bad));raise SystemExit(2)
else:
 paths=sorted(p for p in root.rglob("*") if p.is_file() and p!=target and "__pycache__" not in p.parts)
 target.write_text("".join(f"{sha(p)}  {p.relative_to(root).as_posix()}\n" for p in paths),encoding="utf-8")
 print(f"Wrote {len(paths)} SHA256 entries")

