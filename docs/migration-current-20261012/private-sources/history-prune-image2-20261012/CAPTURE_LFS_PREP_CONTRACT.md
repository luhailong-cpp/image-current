# Private frozen capture preparation

This is an independently reviewed preparation copy of the sealed
`.git/migration-latest-20261011/capture_frozen_delta.py`. The sealed source SHA256
is `16fad0d59d96e0eeda95a4e3395d4a62ee5b504d90f1e804898cbeef64b64039`.
The original capture contract still applies to preservation, ignored-file review,
15 producers, original protected pictures, no deletion, private index, two full
source reads, zero catchup and absence of publication.

The private copy changes `WORK` to `.git/history-prune-image2-20261012`. It accepts
the real audited manifest shapes and explicit portable aliases. It creates only
a content tree from baseline F. It performs no commit, branch, upload, remote
update, historical deletion or history rewrite. Old tile-history retention rules
belong to the separate history converter, after full current content is captured.

## Portable source aliases

`portable_source_aliases` is an explicit list. Every row must contain exactly:

- `original_path`: the absolute old host provenance path outside the repository.
- `workspace_copy`: safe, relative, slash-separated path inside the repository.
- `sha256`: exact lowercase 64-character digest of original/copy bytes.
- `size`: exact integer byte size.

The validator never opens, hashes or resolves outside original bytes. A source
reference outside the repository is accepted only if its exact normalized
absolute original path has one alias and the source digest equals the alias
digest. Duplicate or ambiguous original mappings, incorrect size/digest,
traversal, missing copies, junctions or symlinks in alias-copy paths fail.

All alias copies are independently hash-checked, pinned through capture and
required to appear in final content membership. An ignored copy needs an explicit
ignored include; an excluded required copy fails.

When aliases exist, `portable_source_aliases_manifest` must pin an actual JSON
file outside `.git` containing an `aliases` list exactly equal to the evidence
list. This complete mapping is pinned and required in the captured tree. A `.git`
only mapping, missing manifest, stale digest or different mapping fails.

The prepared private mapping must be reviewed and copied without replacement to
`docs/CAPTURE_PORTABLE_SOURCE_ALIASES_20261012.json`. Its expected SHA256 is recorded
in `freeze-evidence-draft.json`. The copy does not modify any source artwork.

## Nested manifests

The existing `manifest` string plus `currentManifestSha256`/`manifestSha256`
semantics remain unchanged: the explicitly current digest takes precedence over a
retained historical digest. A `manifest` dictionary must have a string `path`.
The outer current digest verifies that path. Any inner `path`/`sha256` pair is
also checked recursively, so an inconsistent embedded digest fails.

An embedded checkpoint may be a filesystem metadata snapshot without `sha256`.
Such a snapshot must name the exact current checkpoint, assert `exists=true`,
and match its byte size when `bytes` is present. It cannot count as a hashed
checkpoint identity. The independently pinned row must still supply a hash, or
a legacy embedded checkpoint must supply its full hash. Any embedded hash must
be well formed and agree with the current gate; conflicting paths/hashes fail.

## Approval and execution

The draft remains `approved=false`, `all_writers_frozen=false`, and
`other_writers_reviewed=false`. Root review must verify the actual producer/source
receipts, remaining writers, reviewed script/test hashes, stable ignored inventory
and committed mapping file before creating approved evidence. A false draft is
refused before production capture. The new script must remain in this private
directory.

Offline validation uses invented small repositories and nonexistent external
original paths. The original 18 checks and 22 added checks passed; no real capture,
network operation or production Git write occurred during those tests.

Only after independent root approval:

```powershell
& 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  .git\history-prune-image2-20261012\capture_frozen_delta_lfs_prep.py capture `
  --freeze-evidence <absolute-approved-evidence-path> --freeze-sha256 <reviewed-SHA256>
```

Capture success does not mean LFS migration, publication or remote completeness.
