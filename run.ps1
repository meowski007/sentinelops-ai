# SentinelOps AI - Developer Helper Script (PowerShell)
param (
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$RootDir = $PSScriptRoot
$PythonBin = "$RootDir\.venv\Scripts\python.exe"
$UvicornBin = "$RootDir\.venv\Scripts\uvicorn.exe"
$RuffBin = "$RootDir\.venv\Scripts\ruff.exe"
$PytestBin = "$RootDir\.venv\Scripts\pytest.exe"

switch ($Command.ToLower()) {
    "seed" {
        Write-Host "Seeding synthetic IT incident dataset..." -ForegroundColor Cyan
        Set-Location "$RootDir\backend"
        & $PythonBin -m app.scripts.seed_data
    }
    "eval" {
        Write-Host "Running RAG Retrieval Quality Benchmark..." -ForegroundColor Cyan
        Set-Location "$RootDir\backend"
        & $PythonBin -m app.scripts.run_eval
    }
    "test-backend" {
        Write-Host "Running Backend Pytest Suite..." -ForegroundColor Cyan
        Set-Location "$RootDir\backend"
        & $PytestBin
    }
    "test-frontend" {
        Write-Host "Running Frontend Vitest Suite..." -ForegroundColor Cyan
        Set-Location "$RootDir\frontend"
        npm.cmd test
    }
    "test" {
        Write-Host "Running All Tests (Backend + Frontend)..." -ForegroundColor Cyan
        Set-Location "$RootDir\backend"
        & $PytestBin
        Set-Location "$RootDir\frontend"
        npm.cmd test
    }
    "lint" {
        Write-Host "Running Ruff Code Quality Check..." -ForegroundColor Cyan
        Set-Location "$RootDir\backend"
        & $RuffBin check .
    }
    "build" {
        Write-Host "Building Production Frontend Bundle..." -ForegroundColor Cyan
        Set-Location "$RootDir\frontend"
        npm.cmd run build
    }
    "backend" {
        Write-Host "Starting FastAPI Backend Server on port 8000..." -ForegroundColor Green
        Set-Location "$RootDir\backend"
        & $UvicornBin app.main:app --reload --port 8000
    }
    "frontend" {
        Write-Host "Starting Vite React Frontend on port 5173..." -ForegroundColor Green
        Set-Location "$RootDir\frontend"
        npm.cmd run dev
    }
    default {
        Write-Host "SentinelOps AI - Available Commands:" -ForegroundColor Yellow
        Write-Host "  .\run.ps1 seed           - Initialize and seed synthetic dataset"
        Write-Host "  .\run.ps1 eval           - Run RAG retrieval benchmark (MRR, Recall@K)"
        Write-Host "  .\run.ps1 test           - Run full test suite (Pytest + Vitest)"
        Write-Host "  .\run.ps1 lint           - Run Ruff linter"
        Write-Host "  .\run.ps1 build          - Build frontend production bundle"
        Write-Host "  .\run.ps1 backend        - Start backend server on http://localhost:8000"
        Write-Host "  .\run.ps1 frontend       - Start frontend dev server on http://localhost:5173"
    }
}
