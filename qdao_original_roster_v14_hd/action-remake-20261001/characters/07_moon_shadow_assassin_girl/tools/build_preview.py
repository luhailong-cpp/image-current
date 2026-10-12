"""Build a file:// compatible preview from real manifest entries only."""
from __future__ import annotations

import json
import sys
from manifest_tools import ROOT, load_manifest, frames_of, local_path


def main() -> int:
    try:
        manifest = load_manifest()
        if manifest.get('timing', {}).get('runCycleMs') != 960 or manifest.get('timing', {}).get('runFrameMs') != 60 or any(
            f.get('durationMs') != 60 for f in frames_of(manifest) if f.get('action') == 'run'
        ):
            raise ValueError('当前跑步交付必须是960ms一圈、16帧均匀60ms；拒绝重建旧节奏。')
        real_frames, skipped = [], []
        for frame in frames_of(manifest):
            path = frame.get("path", frame.get("file"))
            if path and local_path(path).is_file() and not frame.get("isPlaceholder"):
                real_frames.append({**frame, "path": local_path(path).relative_to(ROOT).as_posix()})
            else:
                skipped.append(frame.get("id", path))
        payload = {**manifest, "frames": real_frames, "previewSkipped": skipped}
        template = (ROOT / "tools" / "preview-template.html").read_text(encoding="utf-8")
        # Prevent JSON strings from closing the application/json script element.
        data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        output = ROOT / "preview" / "index.html"
        output.parent.mkdir(exist_ok=True)
        output.write_text(template.replace("__MANIFEST_DATA__", data), encoding="utf-8")
        print(f"{output}\n已加入 {len(real_frames)} 个真实文件；排除 {len(skipped)} 个缺失/占位条目。")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"预览未生成：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
