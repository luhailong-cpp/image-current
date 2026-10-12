# r10_c10 — 4K internal candidate

16 selected native1254² patches have been hard-cropped at [115,115,1139,1139] into r10_c10-candidate-4096.png. Every1024² core matches the selected source exactly. No final pixels were enlarged.

The tile occupies world [36864,36864,40960,40960] in the57344²,14×14 map. Selection is local in selected-patches.json; root zone progress and r10_c09 were not changed.

Current primary QA covers24 native internal seam crops and9 crossings. Internal candidate is ready for final independent changed-source review and external-neighbor review. Formal acceptance remains false. Minor cloth/wood texture variation is recorded as nonblocking observation. qa/internal-primary-review.json is the current report; older first-row and independent interim reports describe their saved earlier source hashes.

generation-index.json lists every successful builtin image and source record. Each has prompt, request, actual tool output_hint receipt, configuration snapshot, references with roles and hashes, global coordinates and measured native size. Config target is recorded separately; submitted and actual model/quality are null because the host does not expose them. The p22-v1 network failure is retained as a receipt.

Geometry repairs use builtin-generated native1254 edits, exact native crops and explicit bounded adoption. Connected-net silhouette adoption preserves unrelated original bench/floor pixels. Additive color fields alter only RGB values at original pixel centers, never blur, shift or resample artwork; all fields and source hashes are saved. Cross-patch color finishing applies the same field to each patch's own image pixels.

layout-only/ contains enlarged input guides only. input-snapshots/ preserves a hash-verified earlier submitted guide. qa/ previews are downsamples only for inspection and are never delivery sources.

Scripts: tile_native_workflow.py in the parent zone prepares/refreshed guides; qa_tile.py assembles and refreshes inspection crops; finalize_tile.py verifies and refreshes this tile's records. Re-running qa_tile.py sets inspection status pending, so inspect changed sources and rerun finalize_tile.py only after reviewing them.
