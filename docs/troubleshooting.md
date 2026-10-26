# SentinelOps AI - Troubleshooting Guide

This guide helps resolve common operational and development environment issues when running SentinelOps AI locally.

---

## 1. Port Conflicts

### Backend (`Port 8000 already in use`)
If another service or zombie uvicorn instance is using port 8000:
- **Windows (PowerShell):**
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
  ```
- **Linux/macOS:**
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```
- **Alternative:** Change port in backend startup:
  ```bash
  uvicorn app.main:app --port 8080
  ```

### Frontend (`Port 5173 already in use`)
Vite will automatically offer to bind to `5174` or you can force a port:
```bash
npm run dev -- --port 3000
```

---

## 2. Windows PowerShell Script Execution Policy

On Windows, executing `npm` or `activate.ps1` may show:
```text
PSSecurityException: File ... cannot be loaded because running scripts is disabled on this system.
```
**Resolution:**
- Always call `.cmd` directly in PowerShell:
  ```powershell
  npm.cmd install
  npm.cmd test
  ```
- Or run Python virtual environment binaries directly without activating:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest
  .\.venv\Scripts\uvicorn.exe app.main:app --reload
  ```

---

## 3. Database Reset & Seeding

If the SQLite database becomes out of sync or you want to restart from scratch:
1. Stop the backend server.
2. Delete `backend/sentinelops.db`.
3. Run the reproducible seed command:
   ```bash
   cd backend
   python -m app.scripts.seed_data
   ```
4. All 5 services, 4 incidents, deployments, and metrics will be cleanly restored with seed 42.

---

## 4. Frontend CORS or Network Connection Errors

If the frontend displays **"Offline / Connecting"**:
1. Confirm the backend is running at `http://127.0.0.1:8000`.
2. Visit `http://127.0.0.1:8000/health` in your browser. It should return status `healthy`.
3. Check `CORS_ORIGINS` in `.env` or `backend/app/core/config.py`. It includes `http://localhost:5173` and `http://127.0.0.1:5173` by default.
