# Project Issue & Resolution Log

This document tracks technical issues encountered and the fixes applied during the development of **Annapurna-AI**.

| Category | Problem / Error Message | Fix Applied | Files Affected |
|----------|-------------------------|-------------|----------------|
| **Startup** | `ModuleNotFoundError: No module named 'dotenv'` | Added `python-dotenv` to dependencies and loaded it in `main.py`. | `backend/requirements.txt`, `backend/app/main.py` |
| **Startup** | Frontend Syntax Error in `test-backend` page | Fixed malformed check inside JSX/TSX. | `app/test-backend/page.tsx` |
| **Auth** | No user authentication | Integrated **Clerk** (Frontend) and JWT verification (Backend). | `app/layout.tsx`, `backend/app/auth/deps.py` |
| **Auth** | `Module not found: Can't resolve '@clerk/nextjs'` | Ran `npm install` to add the missing package. | `package.json`, `node_modules` |
| **Auth** | `SyntaxWarning: name 'generated_plan_store' is assigned to before global declaration` | Moved `global generated_plan_store` to the top of the function scope. | `backend/app/api/routes.py` |
| **Build** | `Next.js Build Check` failing on missing env vars | Created `.env.local` with placeholder keys to pass build checks. | `.env.local` |
| **Build** | `⚠ The "middleware" file convention is deprecated` | Renamed `middleware.ts` to `proxy.ts` (Next.js 16+ convention). | `proxy.ts` (formerly `middleware.ts`) |
| **Runtime** | `ModuleNotFoundError: No module named 'structlog'` | Ran `pip install` to sync the environment with `requirements.txt`. | `backend/requirements.txt` |
| **Features** | Tracing missing User Context | Updated `LLMService` to accept and log `user_id` to LiteLLM metadata. | `backend/app/services/llm_service.py` |
| **Prod** | Production Server Stability | Switched from `uvicorn` to `gunicorn` with 4 workers. | `backend/requirements.txt`, `PRODUCTION_GUIDE.md` |
| **Prod** | Generic 404/Error Pages | Created custom branded `not-found.tsx` and `error.tsx`. | `app/not-found.tsx`, `app/error.tsx` |
| **Auth** | Backend 500 Error (Missing Config) | Added `CLERK_PEM_PUBLIC_KEY` to `backend/.env` for JWT verification. | `backend/.env` |
| **Ops** | `Failed to generate plan` (Env vars not loaded) | Killed "zombie" backend processes holding port 8000 to force restart with new `.env`. | N/A (Terminal) |

## Summary of Major Changes
1.  **Authentication**: Fully secure end-to-end auth with Clerk.
2.  **Observability**: Structured Logging + User Tracing.
3.  **Stability**: Production-grade Gunicorn server config.
4.  **UX**: Custom Error UI and polished Frontend integration.
