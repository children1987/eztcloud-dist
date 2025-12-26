# ISW Backend Dependency Installation Script (Windows PowerShell)
# Usage: 
#   Method 1: powershell -ExecutionPolicy Bypass -File .\install_deps.ps1
#   Method 2: .\install_deps.bat (Recommended, automatically handles execution policy)

# Set execution policy for current session only
$ErrorActionPreference = "Stop"
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force -ErrorAction SilentlyContinue
} catch {
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force -ErrorAction SilentlyContinue
}

Write-Host "Starting ISW Backend dependency installation..." -ForegroundColor Green
Write-Host "Using Douban PyPI mirror for faster download..." -ForegroundColor Cyan

# Set Douban mirror for uv
$env:UV_INDEX_URL = "https://pypi.doubanio.com/simple/"

# Check if virtual environment exists
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment with Python 3.11..." -ForegroundColor Yellow
    # Try to use Python 3.11 specifically
    uv venv --python 3.11
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment with Python 3.11, trying default Python..." -ForegroundColor Yellow
        uv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create virtual environment!" -ForegroundColor Red
            Write-Host "Please ensure Python 3.11 is installed and available in PATH." -ForegroundColor Red
            exit 1
        }
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Create temporary requirements file (excluding django-celery-beat)
Write-Host "Creating temporary requirements file (excluding django-celery-beat)..." -ForegroundColor Yellow
$tempFile = "requirements-temp.txt"
Get-Content requirements.txt | Where-Object { $_ -notmatch "^django-celery-beat" -and $_ -notmatch "^#.*django-celery-beat" } | Set-Content $tempFile -Encoding UTF8

# Install other dependencies
Write-Host "Installing other dependencies..." -ForegroundColor Yellow
uv pip install -r $tempFile --index-url https://pypi.doubanio.com/simple/
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    exit 1
}

# Install django-celery-beat (using --no-binary)
Write-Host "Installing django-celery-beat (from source)..." -ForegroundColor Yellow
uv pip install --no-binary django-celery-beat django-celery-beat==2.5.0 --index-url https://pypi.doubanio.com/simple/

# If uv method fails, try using pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "uv installation failed, trying pip..." -ForegroundColor Yellow
    pip install django-celery-beat==2.5.0 -i https://pypi.doubanio.com/simple/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install django-celery-beat! Please install manually." -ForegroundColor Red
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        exit 1
    }
}

# Clean up temporary file
Remove-Item $tempFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Dependency installation completed!" -ForegroundColor Green
Write-Host "Virtual environment is activated. You can now use the project." -ForegroundColor Green
Write-Host "Example: python manage.py migrate" -ForegroundColor Cyan
