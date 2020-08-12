$FolderStructure = @(
    ".\asset\icon.ico"
    ".\data\input.txt"
    ".\data\profile.csv"
    ".\src\ga.py"
    ".\src\sub\inputprocess.py"
    ".\src\sub\kernel.py"
    ".\src\sub\plot.py"
    ".\src\sub\translate.py"
    ".\src\sub\__init__.py"
    ".\src\test\multitaskdemo.py"
    ".\src\test\outread.py"
    ".\src\test\plotstuff.py"
    ".\src\test\recheck.py"
    ".\src\test\virtualkernel.py"
)


$Commands = @{
    "py" = "cde"
    "abaqus" = "cde"
    # "pipenv" = "cde"
}


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


function Test-DirectoryTree {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$Paths
    )
    $Boolean = $true
    foreach ($Path in $Paths) {
        if (!(Test-Path $Path)) {
            $Log += "File doesn't exist: $Path"
            $Boolean = $false
        }
    }
    return @{
        Log = $Log
        Boolean = $Boolean
    }
}

function Test-Command {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [hashtable]$Commands
    )
    $Boolean = $true
    foreach ($Command in $Commands.GetEnumerator()) {
        if ((Get-Command $Command.Key -ErrorAction SilentlyContinue) -eq $null) {
            $Log += "Path doesn't exist: $($Command.Key)`nFor more info: $($Command.Value)"
            $Boolean = $false
        }
    }
    return @{
        Log = $Log
        Boolean = $Boolean
    }
}


function Clean-Directory {
    Param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$NameList
    )
    $NameList | % { Get-ChildItem -Filter $_ -Recurse -Force | Remove-Item -Force -Recurse }
}


$Check = @(
    (Test-DirectoryTree $FolderStructure).Boolean,
    (Test-Command $Commands).Boolean
)

If ($Check -notcontains $false) {
    "Ok"

    # Push-Location .\src\
    # python .\ga.py 2>$null
    # Pop-Location

    Clean-Directory -NameList $UnusedFiles
}
else {
    "Not ok"
}
