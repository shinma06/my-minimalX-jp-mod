$ErrorActionPreference = 'Stop'
$harnessRuntime = $env:HARNESS_PYTHON
if (-not $harnessRuntime) {
    $harnessRuntime = git config --get harness.python
}
if ($harnessRuntime) {
    & $harnessRuntime @args
    exit $LASTEXITCODE
}
foreach ($harnessCandidate in @('python3', 'python', 'py')) {
    $harnessCommand = Get-Command $harnessCandidate -ErrorAction SilentlyContinue
    if (-not $harnessCommand) { continue }
    $harnessPrefix = @()
    if ($harnessCandidate -eq 'py') { $harnessPrefix = @('-3') }
    & $harnessCommand.Source @harnessPrefix -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $harnessCommand.Source @harnessPrefix @args
        exit $LASTEXITCODE
    }
}
throw 'Python 3.11+ required. Run bootstrap.py with Python or set HARNESS_PYTHON.'
