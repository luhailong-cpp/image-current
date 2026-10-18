from pathlib import Path
import hashlib,json
Z=Path(__file__).resolve().parent.parent
source=Z/'production_workflow.py'
code=source.read_text(encoding='utf-8')
begin=code.index('        target = evidence_path(references[-1]["path"], local=True)',code.index('def assemble('))
end=code.index('        pixels.append(',begin)
old=code[begin:end]
assert old.count('prep["anchors"]')==4
newhead='''        guide_references, guide_prep = references, prep
        native_edit_evidence = None
        correction = prep.get("nativeCorrectionOf")
        if correction:
            # The input is a prior actual native, not a layout-derived image.
            # Verify its complete recorded generation lineage, then independently
            # replay the original anchored guide instead of inventing a derivative.
            original_target = evidence_path(references[-1]["path"], local=True)
            base_version = correction.get("version")
            require(isinstance(base_version, str) and base_version.startswith(patch + "_v")
                    and base_version != version, "Invalid native edit parent")
            require(original_target == evidence_path(correction.get("path"), local=True)
                    and references[-1]["sha256"] == correction.get("sha256"), "Native edit parent target differs")
            base_native = t / "native" / (base_version + ".png")
            require(base_native.resolve() == original_target, "Native edit parent location differs")
            checked(base_native, correction["sha256"])
            base_record_path = Path(str(base_native) + ".generation.json")
            base_record_sha = checked(base_record_path)
            base_record = read(base_record_path)
            require(base_record.get("sha256") == correction["sha256"]
                    and base_record.get("tile") == tile and base_record.get("logicalPatch") == patch
                    and base_record.get("coordinates") == coordinate(tile, patch)
                    and base_record.get("tool") == "image_gen.imagegen" and base_record.get("route") == "builtin"
                    and base_record.get("actualModel") is None and base_record.get("actualQuality") is None
                    and base_record.get("resizedAfterGeneration") is False
                    and base_record.get("finalArtUpscaled") is False, "Native edit parent generation evidence differs")
            base_evidence = base_record.get("evidence", {})
            base_prep_path = t / "records" / (base_version + ".preparation.json")
            checked(base_prep_path, base_evidence.get("preparationSha256"))
            base_prep = validate_preparation(t, base_version)
            require(not base_prep.get("nativeCorrectionOf"), "Nested native edit not implemented; inspect lineage")
            require(base_prep.get("anchors") == prep["anchors"]
                    and base_prep.get("references", [])[:3] == references[:3]
                    and base_record.get("references") == base_prep.get("references"), "Native edit inherited continuity lineage differs")
            for field in ("request", "prompt"):
                checked(base_prep[field], base_prep[field + "Sha256"])
            base_receipt_path = evidence_path(base_evidence.get("receipt"), local=True)
            checked(base_receipt_path, base_evidence.get("receiptSha256"))
            base_receipt = read(base_receipt_path)
            require(status_ok(base_receipt.get("status"))
                    and base_receipt.get("actualModel") is None
                    and not base_receipt.get("resizedAfterGeneration")
                    and not base_receipt.get("finalArtUpscaled")
                    and base_evidence.get("originalSha256") == correction["sha256"], "Native edit parent receipt is not successful native generation")
            for key in ("sourceSha256", "outputSha256", "sha256"):
                require(not base_receipt.get(key) or base_receipt[key] == correction["sha256"], "Native edit parent receipt hash differs")
            base_original = evidence_path(base_evidence.get("originalOutputPath"))
            if base_original.is_file():
                checked(base_original, correction["sha256"])
            with Image.open(base_native) as parent_image:
                require(parent_image.size == (NATIVE, NATIVE) and parent_image.format == "PNG"
                        and parent_image.mode in ("RGB", "RGBA"), "Native edit parent dimensions differ")
                require(parent_image.mode != "RGBA" or parent_image.getextrema()[3] == (255, 255), "Native edit parent not opaque")
            guide_references, guide_prep = base_prep["references"], base_prep
            native_edit_evidence = {"target": str(base_native), "sha256": correction["sha256"],
                "parentGenerationRecord": str(base_record_path), "parentGenerationRecordSha256": base_record_sha,
                "parentPreparation": str(base_prep_path), "targetIsActualNative": True,
                "originalAnchoredGuideReplayedBelow": True, "nativeInputIsNotClaimedAsDerivedGuide": True}
'''
old=old.replace('references[-1]', 'guide_references[-1]').replace('prep["anchors"]','guide_prep["anchors"]')
code=code[:begin]+newhead+old+code[end:]
needle='"anchorGuideReplayVerified": True, "originalFilePresentAndVerified": original_present'
assert code.count(needle)==1
code=code.replace(needle,'"anchorGuideReplayVerified": True, "anchorGuideReplayScope": "native edit parent original guide" if correction else "submitted target", "nativeEditInputVerification": native_edit_evidence, "originalFilePresentAndVerified": original_present')
dest=Z/'production_workflow_native_edit_v1.py'
compile(code,str(dest),'exec')
with dest.open('x',encoding='utf-8') as f:f.write(code)
print(json.dumps({'assembler':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'originalAssemblerUnmodified':str(source),'originalSha256':hashlib.sha256(source.read_bytes()).hexdigest()}))
