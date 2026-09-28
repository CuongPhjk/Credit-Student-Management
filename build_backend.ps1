param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

function Test-PythonWithPip([string]$Candidate) {
    if ([string]::IsNullOrWhiteSpace($Candidate)) {
        return $false
    }
    if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
        return $false
    }
    & $Candidate -c "import pip" 2>$null
    return $LASTEXITCODE -eq 0
}

if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $Candidates = @(
        (Join-Path $ProjectRoot ".venv\Scripts\python.exe")
    )
    $PythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($PythonCommand) {
        $Candidates += $PythonCommand.Source
    }
    foreach ($Candidate in $Candidates) {
        if (Test-PythonWithPip $Candidate) {
            $PythonPath = $Candidate
            break
        }
    }
}

if (-not (Test-PythonWithPip $PythonPath)) {
    throw @"
Không tìm thấy Python có pip. Hãy cài Python 3.10+ từ python.org,
chọn 'Add Python to PATH', rồi chạy lại:
  .\build_backend.ps1
Hoặc truyền đường dẫn cụ thể:
  .\build_backend.ps1 -PythonPath 'C:\duong-dan\python.exe'
"@
}

Write-Host "Python: $PythonPath" -ForegroundColor Cyan
& $PythonPath -m pip install -r requirements.txt cmake
if ($LASTEXITCODE -ne 0) {
    throw "Không thể cài requirements hoặc CMake."
}

$ScriptsDirectory = & $PythonPath -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$CMakePath = Join-Path $ScriptsDirectory "cmake.exe"
if (-not (Test-Path -LiteralPath $CMakePath)) {
    $CMakeCommand = Get-Command cmake.exe -ErrorAction SilentlyContinue
    if (-not $CMakeCommand) {
        throw "Đã cài CMake nhưng không tìm thấy cmake.exe."
    }
    $CMakePath = $CMakeCommand.Source
}

$ConfigureArguments = @(
    "-S", $ProjectRoot,
    "-B", (Join-Path $ProjectRoot "build\cmake"),
    "-DPython_EXECUTABLE=$PythonPath"
)

$MakeCommand = Get-Command mingw32-make.exe -ErrorAction SilentlyContinue
$CompilerCommand = Get-Command g++.exe -ErrorAction SilentlyContinue
if ($MakeCommand -and $CompilerCommand) {
    $ConfigureArguments += @(
        "-G", "MinGW Makefiles",
        "-DCMAKE_CXX_COMPILER=$($CompilerCommand.Source)",
        "-DCMAKE_MAKE_PROGRAM=$($MakeCommand.Source)"
    )
}

Write-Host "Đang cấu hình project..." -ForegroundColor Cyan
& $CMakePath @ConfigureArguments
if ($LASTEXITCODE -ne 0) {
    throw "CMake configure thất bại."
}

Write-Host "Đang build backend..." -ForegroundColor Cyan
& $CMakePath --build (Join-Path $ProjectRoot "build\cmake") --config Release
if ($LASTEXITCODE -ne 0) {
    throw "Build backend thất bại."
}

$Extension = Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "bridge") `
    -Filter "_credit_backend*.pyd" | Select-Object -First 1
if (-not $Extension) {
    throw "Build xong nhưng không tìm thấy extension trong thư mục bridge."
}

Write-Host "Build thành công: $($Extension.FullName)" -ForegroundColor Green
Write-Host "Chạy ứng dụng bằng: & '$PythonPath' app.py" -ForegroundColor Green
