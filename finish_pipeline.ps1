# finish_pipeline.ps1
# Waits for batch_process.py, then generates HTML reports and pushes to GitHub.

$env:PYTHONIOENCODING = "utf-8"
$projectDir = "d:\GIT\Medical"
Set-Location $projectDir

Write-Host "=== Finish Pipeline: waiting for batch ==="

$summaryFile = Join-Path $projectDir "output_reports\batch_summary.csv"
$waitMin = 0
while (-not (Test-Path $summaryFile)) {
    $count = (Get-ChildItem (Join-Path $projectDir "output_reports") -Filter "*.json" | Measure-Object).Count
    Write-Host ("  [" + (Get-Date -Format 'HH:mm:ss') + "] Waiting... " + $count + " JSON reports so far")
    Start-Sleep -Seconds 60
    $waitMin++
    if ($waitMin -gt 360) {
        Write-Host "  [TIMEOUT] Waited 6 hours - check batch manually"
        exit 1
    }
}

Write-Host ""
Write-Host "=== Batch complete! Generating HTML reports..."
python generate_html_report.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ("[ERROR] generate_html_report.py failed with exit " + $LASTEXITCODE)
    exit 1
}

Write-Host ""
Write-Host "=== HTML reports generated. Committing and pushing to GitHub..."
$gitBin = "C:\Program Files\Git\bin\git.exe"
& $gitBin add "output_reports/" "html_reports/" "src/classification/doc_types.py" "src/decisioning/decision_engine.py" "batch_process.py"
& $gitBin commit -m "Auto: full batch results plus improved classifier and decision engine"
& $gitBin push origin main

Write-Host ""
Write-Host "=== ALL DONE ==="
$count = (Get-ChildItem (Join-Path $projectDir "output_reports") -Filter "*.json" | Measure-Object).Count
Write-Host ("Total JSON reports: " + $count)
Get-Content $summaryFile | Write-Host
