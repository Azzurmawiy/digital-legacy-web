# 🛡️ Digital Legacy Platform
### Group 16 | Computer Engineering | Ahmadu Bello University, Zaria

[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)
[![Tech: Django](https://img.shields.io/badge/Backend-Django%206.0-navy.svg)](https://www.djangoproject.com/)
[![Tech: React](https://img.shields.io/badge/Frontend-React%2018-blue.svg)](https://reactjs.org/)
[![Tech: Docker](https://img.shields.io/badge/Container-Docker-lightblue.svg)](https://www.docker.com/)

**Digital Legacy** is a secure, military-grade digital inheritance platform designed to protect your assets and ensure they reach your loved ones when it matters most. It combines cutting-edge encryption with an automated "Dead Man's Switch" to bridge the gap between security and accessibility.

---

## 🌟 Key Features

### 🌑 Premium Navy & Gold UI
*   **Dynamic Dashboard:** Real-time stats on vault assets, storage usage, and heir status.
*   **Glassmorphism Design:** Modern, high-fidelity interface with translucent deep navy tones and gold accents.
*   **Fully Responsive:** Optimized for everything from mobile devices to large desktop monitors.

### 🔐 Security & Safety Protocols
*   **Automated Safety Switch (DMS):** System auto-activates upon registration. Heartbeat signals reset inactivity timers to prevent accidental release.
*   **Military-Grade Encryption:** Sensitive assets are secured using **AES-256-GCM** with unique encryption keys.
*   **Real-Time Notifications:** SMTP-enabled alerting system (Gmail/AWS SES ready) for heartbeat reminders and system warnings.
*   **Verified Heir Management:** Secure beneficiary assignment with identity verification logic.

### 📂 Digital Vault
*   **Asset Management:** Secure storage for legal documents, passwords, and sensitive credentials.
*   **Memories:** A dedicated space for photos and heartfelt legacy messages.
*   **Storage Tracking:** Automated tracking of file sizes and storage limits.

---

## 🚀 Quick Start (Docker)

The easiest way to run the entire stack (Backend + Frontend + DB + Redis) is using Docker.

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env with your specific keys
```

### 2. Launch Services
```bash
docker-compose up --build -d
```

### 3. Initialize Database
```bash
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py createsuperuser
```

*   **Frontend:** [http://localhost:5173](http://localhost:5173)
*   **API Docs:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

## 📂 Architecture

```bash
digital-legacy-web/
├── apps/               # Core Modules (Auth, Vault, DMS, Beneficiaries, Notifications)
├── core/               # Shared Security & Middleware
├── frontend/           # React + Vite (Custom Design System)
├── config/             # Django & Celery Configuration
└── scripts/            # Maintenance & Utility Scripts
```

---

## ☁️ Deployment
This project is optimized for deployment on **AWS (EC2 Free Tier)**. Detailed instructions for setting up your production server, including SSL and Swap memory configuration, can be found in [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md).

---

*© 2026 Digital Legacy Project — ABU Zaria Computer Engineering*