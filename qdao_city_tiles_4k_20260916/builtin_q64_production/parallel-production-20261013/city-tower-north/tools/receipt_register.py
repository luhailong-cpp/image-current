"""Register a completed built-in image event without exposing its base64 payload.

Reads the specified session log, preserves the complete event except item.result,
and delegates native registration to the unchanged native_batch.py. All writes
are immutable and confined to this batch. Source images and logs are read-only.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import native_batch as native

DEFAULT_LOG = Path(
    "C:/Users/luyua/.codex/sessions/2026/10/13/"
    "rollout-2026-10-13T00-35-43-01a1338b-807e-7e72-9d6d-adc2ca02b507.jsonl"
)
BATCH = Path(__file__).resolve().parent.parent


def batch_input(value):
    path = Path(value)
    if not path.is_absolute():
        path = BATCH / path
    path = path.resolve()
    native.require(path.is_relative_to(BATCH), "Request/prompt must be inside this batch")
    native.require(path.is_file(), f"Missing batch input: {path}")
    return path


def receipt_target(name):
    root = (BATCH / "receipts").resolve()
    native.require(root.is_relative_to(BATCH), "Receipts directory escaped batch")
    path = (root / name).resolve()
    native.require(path.is_relative_to(root), "Receipt output escaped receipts directory")
    native.require(not path.exists(), f"Refusing overwrite: {path}")
    return path


def write_json_exclusive(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    native.require(path.resolve().is_relative_to(BATCH), "Write parent redirected outside batch")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def completed_event(log_path, event_id):
    match = None
    with log_path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, 1):
            # Filter bytes before parsing large unrelated records. Never print raw lines.
            if event_id.encode("ascii") not in raw_line or b"item_completed" not in raw_line:
                continue
            try:
                event = json.loads(raw_line)
            except (ValueError, UnicodeDecodeError):
                raise ValueError(f"Malformed matching session JSON at line {line_number}") from None
            payload = event.get("payload", {})
            item = payload.get("item", {})
            if not (event.get("type") == "event_msg"
                    and payload.get("type") == "item_completed"
                    and item.get("kind") == "image_gen.generation"
                    and item.get("id") == event_id):
                continue
            native.require(match is None, "Ambiguous duplicate completed event ID")
            match = (event, line_number, hashlib.sha256(raw_line).hexdigest())
    native.require(match is not None, "No matching image_gen.generation item_completed event")
    event, line_number, line_sha = match
    payload = event["payload"]
    item = payload["item"]
    native.require(item.get("status") == "completed", "Image event status is not completed")
    native.require(item.get("failure") in (None, "", {}, []), "Image event reports a failure")
    native.require("failure" in item, "Image event has no explicit failure field")
    native.require(event.get("ordinal") is not None and event.get("timestamp"),
                   "Image event lacks ordinal/timestamp")
    native.require(payload.get("thread_id") and payload.get("turn_id"),
                   "Image event lacks thread/turn identity")
    result = item.get("result")
    native.require(isinstance(result, str) and result, "Completed event has no base64 result")
    if result.startswith("data:"):
        native.require(result.startswith("data:image/png;base64,"), "Unsupported image data URL")
        encoded = result.partition(",")[2]
    else:
        encoded = result
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("Completed result is not valid base64") from None
    native.require(image_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Result bytes are not PNG")
    saved = item.get("savedPath")
    native.require(isinstance(saved, str) and saved, "Completed event has no savedPath")
    source = Path(saved)
    native.require(source.is_absolute(), "Event savedPath must be absolute")
    source = source.resolve()
    native.require(source.is_file(), "Event savedPath does not exist; refusing inferred recovery")
    digest = hashlib.sha256(image_bytes).hexdigest()
    native.require(source.read_bytes() == image_bytes,
                   "Saved PNG bytes do not exactly match decoded event result")
    evidence = {
        "eventId": event_id,
        "sessionLog": str(log_path),
        "sessionLineNumber": line_number,
        "sessionRawLineSha256": line_sha,
        "originalOrdinal": event["ordinal"],
        "originalTimestamp": event["timestamp"],
        "originalThreadId": payload["thread_id"],
        "originalTurnId": payload["turn_id"],
        "savedPath": str(source),
        "decodedResultSha256": digest,
        "decodedResultBytes": len(image_bytes),
        "encodedResultChars": len(result),
        "encodedResultUtf8Sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "savedPngMatchesDecodedResult": True,
        "removedField": "originalEvent.payload.item.result",
        "actualModel": None,
        "actualModelEvidence": "未返回；不从请求偏好推断实际型号",
    }
    # Keep every other field, including full revisedPrompt, exactly as parsed.
    del item["result"]
    return source, {"schemaVersion": 1, "capturedAtUtc": native.now(),
                    "provenance": evidence, "originalEvent": event}, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-id", required=True, help="Exact exec-... completed image event ID")
    parser.add_argument("--request", required=True, help="Saved request JSON, absolute or relative to batch")
    parser.add_argument("--prompt", required=True, help="Exact saved prompt, absolute or relative to batch")
    parser.add_argument("--version", required=True, help="New immutable native registration version")
    parser.add_argument("--session-log", default=str(DEFAULT_LOG),
                        help="Session JSONL containing the completed image event (supports child agents)")
    args = parser.parse_args()
    native.require(re.fullmatch(r"exec-[A-Za-z0-9-]{1,100}", args.event_id), "Unsafe event ID")
    native.verify_contracts()
    request_path, prompt_path = batch_input(args.request), batch_input(args.prompt)
    request = native.read_json(request_path)
    tile, patch = request["tile"], request["patch"]
    native.coords(tile, patch)
    scope = native.Scope()
    output = scope.path(args.version, tile, "native", f"{patch}.png")
    native.require(not output.exists() and not Path(str(output) + ".generation.json").exists(),
                   "Native or generation record already exists")
    references = request["referenced_image_paths"]
    native.require(isinstance(references, list) and references, "Request has no attached references")
    refs = [{"file": str(native.resolve_input(value, request_path.parent)),
             "role": f"Actual attached reference {i} from saved submitted request"}
            for i, value in enumerate(references, 1)]
    log_path = Path(args.session_log).resolve()
    source, receipt, expected_sha = completed_event(log_path, args.event_id)
    native.load_opaque(source, (native.NATIVE, native.NATIVE))
    stem = f"{tile}-{patch}-{args.event_id}"
    receipt_path = receipt_target(Path(args.version) / (stem + ".receipt.json"))
    spec_path = receipt_target(Path(args.version) / (stem + ".register-spec.json"))
    spec = {"tile": tile, "patch": patch, "sourceOutputPath": str(source),
            "prompt": str(prompt_path), "receipt": str(receipt_path),
            "request": str(request_path), "references": refs}
    # Exact prompt/reference agreement is checked by the existing registration tool.
    write_json_exclusive(receipt_path, receipt)
    write_json_exclusive(spec_path, spec)
    native.require(native.sha(source) == expected_sha, "Saved PNG changed before registration")
    registered = native.register(spec_path, scope, args.version)
    native.require(registered["sha256"] == expected_sha, "Registered PNG differs from completed event")
    print(json.dumps({**registered, "eventId": args.event_id, "receipt": str(receipt_path),
                      "registrationSpec": str(spec_path), "eventResultByteIdentity": True},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        print(f"Refused: {error}", file=sys.stderr)
        raise SystemExit(2)
