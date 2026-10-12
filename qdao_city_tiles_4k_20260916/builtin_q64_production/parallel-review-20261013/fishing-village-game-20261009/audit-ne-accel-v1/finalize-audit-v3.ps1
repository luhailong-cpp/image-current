$ErrorActionPreference='Stop'
$out='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-review-20261013\fishing-village-game-20261009\audit-ne-accel-v1'
$report=Get-Content -LiteralPath (Join-Path $out 'audit-report-v2.json') -Raw|ConvertFrom-Json
$checks=@()
$unique=@{}
foreach($item in @($report.inputs)+@($report.selectionRecords)+@($report.qaEvidence)+@($report.selectedNatives)+@($report.explicitVerifiedCandidates)+@($report.privateCompleteCandidate)+@($report.assemblyGeometry.sixTileRegion)){
 if($unique.ContainsKey($item.path)){continue}
 $unique[$item.path]=$true
 $actual=(Get-FileHash -LiteralPath $item.path -Algorithm SHA256).Hash.ToLowerInvariant()
 $checks+=[ordered]@{path=$item.path;expectedSha256=$item.sha256;actualSha256=$actual;unchanged=($actual -eq $item.sha256)}
}
$changed=@($checks|Where-Object{$_.unchanged -eq $false})
$rootPath='D:\work\image\AGENTS.md'
$rootFile=Get-Item -LiteralPath $rootPath
$agentsRecord=[ordered]@{path=$rootPath;sha256=(Get-FileHash -LiteralPath $rootPath -Algorithm SHA256).Hash.ToLowerInvariant();lastWriteTimeUtc=$rootFile.LastWriteTimeUtc.ToString('o');readCompletely=$true}
$report.knownIssues[0].status='Requires native AI repair by original production owner; latest free-route policy allows existing builtin2.0 fallback when2.5 unavailable. This audit window does not generate.'
$report.supersedes='audit-report-v2.json: incorporates latest AGENTS policy and ending SHA recheck; all earlier snapshots retained'
$report|Add-Member -NotePropertyName latestRootInstructions -NotePropertyValue $agentsRecord
$report|Add-Member -NotePropertyName endingSourceHashCheck -NotePropertyValue ([ordered]@{checkedAtUtc=[datetime]::UtcNow.ToString('o');checkedDistinctFiles=$checks.Count;allPinnedSourcesUnchanged=($changed.Count -eq 0);changedFiles=$changed;checks=$checks})
$report|Add-Member -NotePropertyName latestModelPolicy -NotePropertyValue ([ordered]@{source='AGENTS.md2026-10-13 clarification read from disk after parent notification';freeExisting25Preferred=$true;existingBuiltin20FallbackAllowed=$true;additionalPaidRouteAuthorized=$false;actualModelUnreturnedRemainsUnknown=$true;auditGenerationAllowed=$false;oldWaitingForVerified25LanguageSuperseded=$true})
$report|Add-Member -NotePropertyName snapshotStatus -NotePropertyValue $(if($changed.Count){'partially_stale_do_not_inherit_changed_source_reviews'}else{'pinned_source_hashes_unchanged_at_ending_check'})
$report|ConvertTo-Json -Depth 15|Set-Content -LiteralPath (Join-Path $out 'audit-report-v3.json') -Encoding utf8
[ordered]@{report=(Join-Path $out 'audit-report-v3.json');endingCheckedAtUtc=$report.endingSourceHashCheck.checkedAtUtc;checkedFiles=$checks.Count;unchanged=($changed.Count -eq 0);changedFiles=$changed;reportSha256=(Get-FileHash -LiteralPath (Join-Path $out 'audit-report-v3.json') -Algorithm SHA256).Hash.ToLowerInvariant()}|ConvertTo-Json -Depth 6
