$ErrorActionPreference = 'Stop'
$taskBase = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$expectedBase = 'D:\work\image\qdao_original_roster_v14_hd\action-remake-20261001\characters\17_ghost_script_calligrapher_boy'
if ($taskBase -ne $expectedBase) { throw 'Wrong cleanup workspace' }
# Exact roots evidenced by this character's revision records and edit ancestors.
$externalBases = @(
    'C:\Users\luyua\.codex\generated_images\01a0f77a-fb47-7bd0-8402-cf6df9512a1c',
    'C:\Users\luyua\.codex\generated_images\01a10114-831b-7c12-8a91-0c9cb2d89709',
    'C:\Users\luyua\.codex\generated_images\01a10115-2b8e-7a52-8634-77f1edef65cb',
    'C:\Users\luyua\.codex\generated_images\01a10114-f91d-77b2-8a6b-4a2081aed2a5'
)
$planPath = Join-Path $taskBase 'cleanup-plan.json'
$plan = Get-Content -Raw -LiteralPath $planPath | ConvertFrom-Json
if ($plan.status -ne 'ready_for_cleanup_review' -or $plan.manifestStatus -notin @('passed','ready_with_review_limit') -or $plan.validatedRuntimeFrames -ne 196) { throw 'Final cleanup prerequisites missing' }
function Assert-Hash([string]$file, [string]$hash) {
    if ($hash -cnotmatch '^[0-9a-f]{64}$') { throw 'Invalid recorded SHA256' }
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw "Changed file: $file" }
}
function Assert-RegularFile([string]$file) {
    $actual = Get-Item -LiteralPath $file
    if ($actual -isnot [IO.FileInfo] -or $actual.LinkType -or
        ($actual.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'Evidence and deletion targets must be regular non-symlink files'
    }
}
function Assert-ExternalEvidence($item, [string]$absolute) {
    if ($null -eq $item.records -or @($item.records).Count -eq 0) { throw 'External candidate lacks generation records' }
    $stagingBase = [IO.Path]::GetFullPath((Join-Path $taskBase 'staging'))
    foreach ($recordRef in $item.records) {
        if ($recordRef -isnot [string] -or [string]::IsNullOrWhiteSpace($recordRef)) { throw 'Invalid generation record reference' }
        $recordPath = [IO.Path]::GetFullPath((Join-Path $taskBase $recordRef))
        if (-not [IO.Path]::GetDirectoryName($recordPath).Equals($stagingBase, [StringComparison]::OrdinalIgnoreCase) -or
            -not $recordPath.EndsWith('.png.generation.json', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Generation record must be inside this character staging directory'
        }
        Assert-RegularFile $recordPath
        $record = Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
        $returnedPath = $record.evidence.toolReturnedPath
        if ($returnedPath -isnot [string] -or $returnedPath -notmatch '^[A-Za-z]:[\\/]') { throw 'Tool-returned path is not absolute' }
        $recordedAbsolute = [IO.Path]::GetFullPath($returnedPath)
        if (-not $recordedAbsolute.Equals($absolute, [StringComparison]::OrdinalIgnoreCase) -or
            $record.sha256 -cne $item.sha256) {
            throw 'External candidate does not match its exact tool-returned path and source SHA'
        }
    }
}
Assert-Hash (Join-Path $taskBase 'manifest.json') $plan.manifestSha256
Assert-Hash (Join-Path $taskBase 'preview\delivery.html') $plan.deliveryChecks.htmlSha256
Assert-Hash (Join-Path $taskBase 'preview\delivery-data.json') $plan.deliveryChecks.dataSha256
$candidates = @()
foreach ($item in $plan.localCandidates) {
    $absolute = [IO.Path]::GetFullPath((Join-Path $taskBase $item.file))
    if (-not $absolute.StartsWith($taskBase + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Candidate escapes task' }
    if ($item.file -notmatch '^(staging|review|preview)/' -or [IO.Path]::GetExtension($absolute) -notin @('.png','.jpg','.jpeg','.webp','.gif','.avif','.bmp')) { throw 'Unexpected local candidate' }
    if ($absolute -eq (Join-Path $taskBase 'preview\run-current-960ms.webp')) { throw 'Formal preview is protected' }
    $candidates += [pscustomobject]@{file=$absolute;sha256=$item.sha256;bytes=$item.bytes;scope='local'}
}
foreach ($item in $plan.externalCandidates) {
    if ($item.file -isnot [string] -or $item.file -notmatch '^[A-Za-z]:[\\/]') { throw 'External candidate path is not absolute' }
    $absolute = [IO.Path]::GetFullPath($item.file)
    $matchedRoots = @($externalBases | Where-Object { $absolute.StartsWith($_ + '\', [StringComparison]::OrdinalIgnoreCase) })
    if ($matchedRoots.Count -ne 1 -or [IO.Path]::GetExtension($absolute) -ne '.png') { throw 'External candidate escapes exact recorded thread roots' }
    if ($item.allowedRoot -isnot [string] -or
        -not [IO.Path]::GetFullPath($item.allowedRoot).Equals($matchedRoots[0], [StringComparison]::OrdinalIgnoreCase)) {
        throw 'External candidate root differs from reviewed plan'
    }
    Assert-ExternalEvidence $item $absolute
    $candidates += [pscustomobject]@{file=$absolute;sha256=$item.sha256;bytes=$item.bytes;scope='same_thread_original'}
}
# Resolve and validate every literal target before deleting any file.
foreach ($item in $candidates) {
    Assert-RegularFile $item.file
    Assert-Hash $item.file $item.sha256
}
$deleted = @()
$errors = @()
foreach ($item in $candidates) {
    try {
        Assert-RegularFile $item.file
        Assert-Hash $item.file $item.sha256
        Remove-Item -LiteralPath $item.file
        $deleted += $item
    } catch { $errors += [pscustomobject]@{file=$item.file;error=$_.Exception.Message} }
}
$report = [ordered]@{
    character='17_ghost_script_calligrapher_boy'
    status=$(if ($errors.Count -eq 0) {'completed'} else {'partial_failure'})
    completedAt=[DateTimeOffset]::UtcNow.ToString('o')
    authorization='User AGENTS.md 2026-09-23 retention policy; final runtime and active references verified before removal'
    planSha256=(Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()
    manifestSha256=$plan.manifestSha256
    deletedImages=$deleted.Count
    deletedBytes=($deleted | Measure-Object -Property bytes -Sum).Sum
    preserved='196 runtime PNGs, formal run WebP, all generation/model/quality/source text, old external formal libraries'
    deleted=$deleted
    errors=$errors
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskBase 'cleanup-report.json') -Encoding utf8
[pscustomobject]@{status=$report.status;deletedImages=$deleted.Count;errors=$errors.Count} | ConvertTo-Json -Compress
if ($errors.Count) { exit 2 }
