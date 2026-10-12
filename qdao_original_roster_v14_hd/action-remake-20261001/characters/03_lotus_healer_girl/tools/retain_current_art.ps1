param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$qdaoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$qdaoExpected = [IO.Path]::GetFullPath('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl')
if ($qdaoRoot -ne $qdaoExpected) { throw 'Refusing unexpected character directory.' }
$qdaoSelection = Get-Content -LiteralPath (Join-Path $qdaoRoot 'review/run-E-selection.json') -Raw | ConvertFrom-Json
$qdaoKeep = @{}
foreach ($qdaoFrame in $qdaoSelection.frames) {
    $qdaoSource = [IO.Path]::GetFullPath((Join-Path $qdaoRoot $qdaoFrame.source))
    $qdaoExport = [IO.Path]::GetFullPath((Join-Path $qdaoRoot $qdaoFrame.file))
    if (!(Test-Path -LiteralPath $qdaoSource -PathType Leaf) -or !(Test-Path -LiteralPath $qdaoExport -PathType Leaf)) { throw 'Current source/export missing.' }
    if ((Get-FileHash -LiteralPath $qdaoSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $qdaoFrame.sourceSha256) { throw 'Current source SHA changed.' }
    if ((Get-FileHash -LiteralPath $qdaoExport -Algorithm SHA256).Hash.ToLowerInvariant() -ne $qdaoFrame.sha256) { throw 'Current export SHA changed.' }
    $qdaoKeep[$qdaoSource] = $true
}
$qdaoNative = [IO.Path]::GetFullPath((Join-Path $qdaoRoot 'generation/E'))
$qdaoEntries = @()
foreach ($qdaoImage in Get-ChildItem -LiteralPath $qdaoNative -File -Filter '*.png') {
    $qdaoFull = [IO.Path]::GetFullPath($qdaoImage.FullName)
    if (!$qdaoFull.StartsWith($qdaoNative + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Image escapes character source directory.' }
    $qdaoRecordPath = $qdaoFull + '.generation.json'
    if (!(Test-Path -LiteralPath $qdaoRecordPath -PathType Leaf)) { throw 'Missing provenance.' }
    $qdaoRecord = Get-Content -LiteralPath $qdaoRecordPath -Raw | ConvertFrom-Json
    $qdaoHash = (Get-FileHash -LiteralPath $qdaoFull -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($qdaoHash -ne $qdaoRecord.sha256) { throw 'Provenance SHA mismatch.' }
    $qdaoSelected = $qdaoKeep.ContainsKey($qdaoFull)
    $qdaoEntries += [ordered]@{
        file = 'generation/E/' + $qdaoImage.Name
        sha256 = $qdaoHash
        decision = $(if ($qdaoSelected) {'retain_current_unique_wip'} else {'remove_unselected_retry'})
        reason = $(if ($qdaoSelected) {'Current 16-frame selection depends on this native artwork; still needs local edits.'} else {'A selected current candidate is on disk; this earlier/rejected version is no longer a current pixel dependency.'})
        generationRecord = 'generation/E/' + $qdaoImage.Name + '.generation.json'
    }
}
$qdaoRemoved = @()
$qdaoPriorRemoved = @()
$qdaoPriorEntries = @()
$qdaoHistoryPath = Join-Path $qdaoRoot 'review/retention.json'
if (Test-Path -LiteralPath $qdaoHistoryPath -PathType Leaf) {
    $qdaoPrior = Get-Content -LiteralPath $qdaoHistoryPath -Raw | ConvertFrom-Json
    if ($qdaoPrior.mode -eq 'applied') {
        $qdaoPriorRemoved = @($qdaoPrior.removedPngFiles)
        $qdaoCurrentNames = @($qdaoEntries | ForEach-Object {$_.file})
        $qdaoPriorEntries = @($qdaoPrior.entries | Where-Object {$_.file -notin $qdaoCurrentNames})
    }
}
if ($Apply) {
    foreach ($qdaoEntry in $qdaoEntries) {
        if ($qdaoEntry.decision -eq 'remove_unselected_retry') {
            $qdaoDelete = [IO.Path]::GetFullPath((Join-Path $qdaoRoot $qdaoEntry.file))
            if (!$qdaoDelete.StartsWith($qdaoNative + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Deletion escapes source directory.' }
            Remove-Item -LiteralPath $qdaoDelete
            $qdaoRemoved += $qdaoEntry.file
        }
    }
}
$qdaoReport = [ordered]@{
    checkedAt = [DateTimeOffset]::Now.ToString('o')
    mode = $(if ($Apply) {'applied'} else {'dry_run'})
    authorization = 'Root AGENTS.md retention preference confirmed 2026-09-23; selected unique WIP and candidate exports remain.'
    allowedDirectory = $qdaoRoot
    retainedCurrentNativeCount = @($qdaoEntries | Where-Object {$_.decision -eq 'retain_current_unique_wip'}).Count
    removedPngCount = @($qdaoPriorRemoved + $qdaoRemoved | Select-Object -Unique).Count
    removedThisRunCount = $qdaoRemoved.Count
    removedPngFiles = @($qdaoPriorRemoved + $qdaoRemoved | Select-Object -Unique)
    entries = @($qdaoPriorEntries) + @($qdaoEntries)
    provenancePreserved = 'All prompt/job/receipt/generation/review text and image SHA retained. Historical input references may intentionally point to retired PNG; these are lineage evidence, not active preview dependencies.'
    externalFilesModified = $false
    noRecursiveDelete = $true
}
$qdaoReportPath = $(if ($Apply) {$qdaoHistoryPath} else {Join-Path $qdaoRoot 'review/retention-plan.json'})
$qdaoReport | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $qdaoReportPath -Encoding utf8
$qdaoReport | Select-Object mode,retainedCurrentNativeCount,removedPngCount | ConvertTo-Json

