# 🛡️ Digital Legacy Platform
### Group 16 | Computer Engineering | Ahmadu Bello University, Zaria

[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)
[![Tech: Django](https://img.shields.io/badge/Backend-Django%204.2-navy.svg)](https://www.djangoproject.com/)
[![Tech: React](https://img.shields.io/badge/Frontend-React%2018-blue.svg)](https://reactjs.org/)

A secure, military-grade digital inheritance platform designed to protect your assets and ensure they reach your loved ones when it matters most.

---

## ✨ Features & Sprints

### 🌑 Premium Navy & Gold UI
*   **Glassmorphism Design:** Modern, translucent interfaces with deep navy tones and gold accents.
*   **Syne & DM Sans Typography:** Curated font pairings for a professional, high-end feel.
*   **Micro-animations:** Smooth transitions and feedback loops built with CSS-in-JS patterns.
*   **Global Notifications:** Centralized, elegant success and error toasts using `react-hot-toast`.
*   **Modular Architecture:** Clean, highly-typed React component hierarchy enforcing strictly enforced `TypeScript` interfaces.
*   **Fully Responsive:** Three-tier breakpoint system — full sidebar (≥1025px), icon-only sidebar (≤1024px), off-canvas drawer with hamburger toggle (≤768px).

### 🔐 Security & Core Functionality
*   **Military-Grade Encryption:** Assets are secured using **AES-256-GCM** with unique data keys.
*   **Dead Man's Switch (DMS):** Automated inactivity tracking with configurable heartbeat intervals.
*   **Digital Vault:** Secure storage for legal documents, photos, and heartfelt legacy messages.
*   **Beneficiary Management:** Controlled heir assignment with verifiable proof-of-identity logic.
*   **Immutable Audit Logs:** Every sensitive action is cryptographically tracked.

---

## 🚀 Fast Track (Docker — Recommended)

The easiest way to run the entire platform (Backend + Frontend + DB + Redis) is using Docker.

### 1. Prerequisites
*   **Docker Desktop** (WSL 2 backend recommended for Windows)
*   **Hardware Tip:** For smooth performance, ensure WSL 2 has at least 4GB RAM allocated in `.wslconfig`.

### 2. Launching the App
```powershell
# 1. Setup environment
cp .env.example .env

# 2. Build and Start everything
docker-compose up --build
```

### 3. Initialize System
Once the containers are healthy:
```powershell
# Run Migrations
docker-compose exec api python manage.py migrate

# Create Admin Account
docker-compose exec api python manage.py createsuperuser
```

*   **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
*   **API Documentation:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

## 📂 Project Architecture

```bash
digital-legacy-web/
├── apps/               # Django Modules (Auth, Vault, DMS, Beneficiaries)
├── core/               # Shared logic (Security, Middleware, Base Classes)
├── frontend/           # React + Vite + Premium Custom CSS
│   ├── src/components/ # UI Components (Vault, VaultItemCard, VaultUploadForm,
│   │                   #   Memories, DMSConfig, Sidebar, Dashboard...)
│   ├── src/store/      # Zustand stores with typed API + toast error handling
│   └── src/index.css   # Navy & Gold Design System + responsive breakpoints
├── config/             # Project settings (Celery, JWT, URL Routing)
└── docker/             # Orchestration & Environment configs
```

---

## 🛠️ Developer Commands

| Task | Command |
| :--- | :--- |
| **Start Services** | `docker-compose up` |
| **Stop & Wipe DB** | `docker-compose down -v` |
| **Backend Tests** | `docker-compose exec api pytest` |
| **Frontend Lint** | `cd frontend && npm run lint` |
| **Build Frontend** | `cd frontend && npm run build` |

---

## 🛡️ Security Guidelines
1. **Zero Trust:** Never commit `.env` or sensitive keys to version control.
2. **Encryption:** Use the `EncryptionService` in `core/` for all sensitive fields.
3. **API Standards:** Always return responses using the standard `{success, data, error}` envelope.

---

## ❓ Troubleshooting

### ❌ Frontend: "Cannot find native binding"
**Fix:** Delete `frontend/node_modules` on your host machine. Docker will manage dependencies internally within its own isolated volume.

### ❌ Database: "Relation [x] does not exist"
**Fix:** Ensure migrations are synced: `docker-compose exec api python manage.py migrate`.

### ❌ Network: Docker "Handshake Timeout"
**Fix:** In Docker Desktop Settings → Docker Engine, ensure your DNS is set to Google's public DNS:
```json
{ "dns": ["8.8.8.8", "8.8.4.4"] }
```

---

*© 2026 Digital Legacy Project — ABU Zaria Computer Engineering*