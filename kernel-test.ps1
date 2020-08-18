$UnusedFiles = @(
    "__pycache__"
    "*.dat"
    "*.env"
    "*.inp"
    "*.ipm"
    "*.lck"
    "*.log"
    "*.com"
    "*.msg"
    "*.prt"
    "*.sim"
    "*.sta"
    "*.rec"
    "*.pyc"
    "*.odb"
)


function Clear-Line {
    Param(
    	[Parameter(Position=1)]
    	[int32]$Count=1
    )

    $CurrentLine  = $Host.UI.RawUI.CursorPosition.Y
    $ConsoleWidth = $Host.UI.RawUI.BufferSize.Width

    $i = 1
    for ($i; $i -le $Count; $i++) {
    	[Console]::SetCursorPosition(0,($CurrentLine - $i))
    	[Console]::Write("{0,-$ConsoleWidth}" -f " ")
    }
    [Console]::SetCursorPosition(0,($CurrentLine - $Count))
}


function Clean-Directory {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$NameList
    )
    $NameList | % { Get-ChildItem -Filter $_ -Recurse -Force | Remove-Item -Force -Recurse }
}


Write-Host "----------------------" -ForegroundColor Cyan
Write-Host "PROSTHETIC FOOT DESIGN" -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan


Write-Output "Running..."
Start-Sleep 1

Push-Location .\src\
$Result = abaqus cae noGUI=sub\kernel.py 2>..\result\error.log
Clear-Line
ConvertFrom-Json $Result
Clean-Directory -NameList $UnusedFiles
Pop-Location
