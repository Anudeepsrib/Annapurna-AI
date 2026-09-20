# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python -m alembic upgrade head; if (`$LASTEXITCODE -eq 0) { .\venv\Scripts\python -m uvicorn app.main:app --reload }"

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host "Both servers starting..." -ForegroundColor Cyan
