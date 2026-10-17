$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# Force UTF-8 for the Windows console
chcp 65001 > $null

[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$OutputEncoding = [Console]::OutputEncoding

# Log directory
$logDirectory = "evaluation\runs"
$logFile = "$logDirectory\latest_run.log"

New-Item `
    -ItemType Directory `
    -Path $logDirectory `
    -Force |
    Out-Null

# Start every run with a clean UTF-8 log file
"" | Out-File `
    -FilePath $logFile `
    -Encoding utf8

# Run application and write every line explicitly as UTF-8
python -X utf8 -m uvicorn app.main:app --reload 2>&1 |
    ForEach-Object {

        # Show in terminal
        Write-Host $_

        # Write to log as UTF-8
        $_ | Out-File `
            -FilePath $logFile `
            -Append `
            -Encoding utf8
    }