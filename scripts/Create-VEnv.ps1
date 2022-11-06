$BaseDir = $PSScriptRoot
Write-Host "Running from $BaseDir"

$currentFolder = Split-Path $BaseDir -Leaf
if ($currentFolder -eq "scripts") {
    $venvRelativePath = "..\.venv"
    Write-Host "This is the scripts folder. The venv relative path is $venvRelativePath"
}

if (-not $venvRelativePath) {
    throw "You must run this script from the scripts folder, or from the repo root."
}

$joinedVenvPath = Join-Path $BaseDir $venvRelativePath
Write-Host "joinedVenvPath is $joinedVenvPath"
$resolvedVenvPath = Resolve-Path $joinedVenvPath -ErrorAction SilentlyContinue -ErrorVariable _resolveError
if ($resolvedVenvPath) {
    Write-Host "Your virtual environment already exists"
    exit
}

$resolvedVenvPath = $_resolveError[0].TargetObject
Write-Host "Creating a virtual environment at $resolvedVenvPath"

# Create the virtual environment
python -m venv $resolvedVenvPath

# Activate the virtual environment
$activateFilePath = Join-Path $resolvedVenvPath "Scripts\activate.ps1"
& $activateFilePath