$ErrorActionPreference = 'Stop'

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $workspaceRoot 'database-data.js'
$database = $null
$jsonText = $null

Get-ChildItem -LiteralPath $workspaceRoot -Filter '*.json' -File | ForEach-Object {
    if ($database) {
        return
    }

    try {
        $candidateText = [System.IO.File]::ReadAllText(
            $_.FullName,
            [System.Text.Encoding]::UTF8
        )
        $candidate = $candidateText | ConvertFrom-Json

        if ($candidate.database_name -and $candidate.prompts -and $candidate.prompts.Count -gt 0) {
            $database = $candidate
            $jsonText = $candidateText
        }
    } catch {
        # Ignore unrelated or malformed JSON files.
    }
}

if (-not $database) {
    Write-Error 'No valid AI video prompt database JSON was found.'
    exit 1
}

$javascript = "window.AI_VIDEO_PROMPT_DB = $jsonText;"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($outputPath, $javascript, $utf8NoBom)

Write-Output ("Synced {0} prompts." -f $database.prompts.Count)
