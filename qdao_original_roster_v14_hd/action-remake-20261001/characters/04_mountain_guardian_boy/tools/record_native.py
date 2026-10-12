"""Record native image evidence without changing pixels."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def record(stem, status):
    stem = Path(stem).resolve()
    if not stem.is_relative_to(ROOT / "provenance"):
        raise ValueError("Only this character provenance is writable")
    image = stem.with_suffix(".png")
    submission_path = stem.with_suffix(".submission.json")
    receipt_path = stem.with_suffix(".receipt.json")
    submission = json.loads(submission_path.read_text(encoding="utf-8-sig"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    submitted = submission["submittedParameters"]
    references = []
    for idx, name in enumerate(submitted["referenced_image_paths"], 1):
        path = Path(name)
        with Image.open(path) as ref:
            size = list(ref.size)
        references.append({"inputIndex": idx, "path": path.as_posix(), "sha256": sha(path), "dimensions": size, "role": "用途对应完整提示词中的reference序号", "viewed": True, "passedToTool": True})
    with Image.open(image) as native:
        native.load()
        info = {"width": native.width, "height": native.height, "format": native.format, "mode": native.mode, "alphaExtrema": list(native.getchannel("A").getextrema()) if native.mode == "RGBA" else None}
    data = {
        "schemaVersion": 1, "file": image.relative_to(ROOT).as_posix(),
        "sha256": sha(image), **info, "generatedAt": None,
        "generationTimeEvidence": {"startedAt": submission.get("startedAt"), "completedAt": receipt.get("completedAt"), "timezone": "America/New_York", "note": "请求边界时间，非工具披露的准确生成时间"},
        "tool": "image_gen__imagegen", "route": "builtin",
        "configSnapshot": submission["configSnapshot"],
        "submittedParameters": submitted, "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理，工具无model/quality选择器且回执未披露实际版本或质量",
        "references": references, "prompt": {"path": stem.with_suffix(".prompt.txt").relative_to(ROOT).as_posix(), "sha256": sha(stem.with_suffix(".prompt.txt"))},
        "evidence": {"submission": submission_path.relative_to(ROOT).as_posix(), "receipt": receipt_path.relative_to(ROOT).as_posix()},
        "review": {"status": status, "artApproved": False},
        "recordedAt": datetime.now(timezone.utc).isoformat()
    }
    output = stem.with_suffix(".png.generation.json")
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(output), "sha256": data["sha256"], **info}, ensure_ascii=False))
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("stem")
    p.add_argument("--status", default="candidate_pending_visual")
    a = p.parse_args()
    record(a.stem, a.status)
