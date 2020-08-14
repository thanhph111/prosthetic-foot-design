$FolderStructure = @(
    ".\asset\icon.ico"
    ".\data\input.json"
    ".\data\profile.csv"
    ".\src\ga.py"
    ".\src\sub\inputprocess.py"
    ".\src\sub\kernel.py"
    ".\src\sub\plot.py"
    ".\src\sub\translate.py"
    ".\src\sub\__init__.py"
    # ".\src\test\multitaskdemo.py"
    # ".\src\test\outread.py"
    # ".\src\test\plotstuff.py"
    # ".\src\test\recheck.py"
    # ".\src\test\virtualkernel.py"
)


$Commands = @{
    "py" = @{
        "Info" = "Install at python.com or add python.exe to PATH"
        "GetVersionCommand" = "((python -V) -split ' ')[-1]"
        "RequiredVersion" = "3.2"
    }
    "abaqus" = @{
        "Info" = "Install Abaqus or add abaqus.bat to PATH"
        "GetVersionCommand" = "((abaqus information=version)[1] -split ' ')[-1]"
        "RequiredVersion" = "0"
    }
    "pip" = @{
        "Info" = "Install pip or add pip to PATH"
        "GetVersionCommand" = "((pip --version) -split ' ')[1]"
        "RequiredVersion" = "0"
    }
}


$Packages = @(
    "cycler"
    "kiwisolver"
    "matplotlib"
    "numpy"
    "Pillow"
    "pyparsing"
    "python-dateutil"
    "six"
)


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


function Test-DirectoryTree {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$Paths
    )
    $Boolean = $true
    foreach ($Path in $Paths) {
        if (!(Test-Path $Path)) {
            $Boolean = $false
            Write-Warning "File doesn't exist: '$Path'
            `rCheck again.`n`n"
        }
    }
    return $Boolean
}

function Test-Command {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [hashtable]$Commands
    )
    foreach ($Command in $Commands.GetEnumerator()) {
        if ((Get-Command $Command.Key -ErrorAction SilentlyContinue) -eq $null) {
            $Boolean += @{ $Command.Key = $false}
            Write-Warning "Path doesn't exist: '$($Command.Key)'.
            `r$($Command.Value.Info).`n`n"
        }
        else {
            if ((Invoke-Expression $Command.Value.GetVersionCommand) -lt $Command.Value.RequiredVersion) {
                $Boolean += @{ $Command.Key = $false}
                Write-Warning "'$($Command.Key)' required at least version. $($Command.Value.RequiredVersion).`n`n"
            }
            else {
                $Boolean += @{ $Command.Key = $true}
            }
        }
    }

    if ($Boolean.pip) {
        if (($Boolean.Values -notcontains $false) -and (Test-Package -Packages $Packages)) {
            return $true
        }
    }
    return $false
}


function Test-Package {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$Packages
    )
    $Boolean = $true
    $InstallPackages = pip freeze | % { ($_ -split "==")[0] }
    foreach ($Package in $Packages) {
        if ($InstallPackages -notcontains $Package) {
            $Boolean = $false
            Write-Warning "Package '$Package' missing.
            `rPlease install using pip or get into virtual environment.`n`n"
        }
    }
    return $Boolean
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

Write-Output "Checking neccessary files and softwares..."
Start-Sleep 1
Clear-Line

$Check = @(
    Test-DirectoryTree $FolderStructure
    Test-Command $Commands
)

If ($Check -notcontains $false) {
    Write-Output "Everything looks fine. Start running..."
    Start-Sleep 1
    Clear-Line

    Push-Location .\src\
    python .\ga.py 2>..\result\error.log
    Clean-Directory -NameList $UnusedFiles
    Pop-Location
}
