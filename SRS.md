# Software Requirements Specification (SRS)
## Digital Legacy Platform

**Prepared By:** Group 16
**Department:** Computer Engineering
**Institution:** Ahmadu Bello University, Zaria
**Date:** May 2026

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to outline the Software Requirements Specification (SRS) for the **Digital Legacy Platform**. It defines the functional and non-functional requirements, system architecture, and overall behavior of the application to serve as a guide for development, testing, and deployment.

### 1.2 Scope
The Digital Legacy Platform is a secure, military-grade digital inheritance web application. It is designed to allow users to securely store vital digital assets (legal documents, personal photos, encrypted messages) and establish a "Dead Man's Switch" (DMS) protocol. In the event of the user's prolonged inactivity or passing, the system automatically triggers a release protocol, transferring decryption keys and access rights to pre-authorized beneficiaries (heirs).

### 1.3 Intended Audience
This document is intended for:
- Developers and Software Engineers working on the platform.
- Project Supervisors and Evaluators at ABU Zaria.
- UI/UX Designers ensuring interface requirements are met.
- Quality Assurance (QA) testers verifying functionality.

---

## 2. Overall Description

### 2.1 Product Perspective
The system operates as a self-contained, containerized web application utilizing a client-server architecture:
- **Frontend:** A responsive Single Page Application (SPA) built with React 18, Vite, and TypeScript.
- **Backend:** A RESTful API built with Django 4.2 and Django REST Framework.
- **Database:** PostgreSQL for persistent relational data.
- **Task Queue & Cache:** Redis and Celery for managing background tasks such as the Dead Man's Switch heartbeat checks and notification dispatches.

### 2.2 Product Functions
1. **User Authentication & Authorization:** Secure registration, login, and session management using JWT.
2. **Encrypted Digital Vault:** Upload, retrieval, and deletion of digital assets (documents, images, messages). All assets are encrypted at rest using AES-256-GCM.
3. **Dead Man's Switch (DMS) Configuration:** Setting inactivity thresholds (e.g., 90 days) and a cooling-off period (e.g., 7 days) before asset release.
4. **Beneficiary (Heir) Management:** Adding and removing authorized individuals who will inherit the assets.
5. **Heartbeat System:** A mechanism for the user to signal they are active, resetting the DMS countdown.
6. **Audit Logging:** An immutable ledger tracking all sensitive system events, vault accesses, and configuration changes.

### 2.3 User Classes and Characteristics
- **Vault Owner (Primary User):** Creates the vault, uploads assets, configures the DMS, assigns heirs, and periodically sends heartbeats.
- **Beneficiary / Heir:** Receives notifications upon the triggering of the DMS and is granted secure, read-only access to the inherited assets after identity verification.
- **System Administrator:** Oversees platform health, infrastructure, and top-level monitoring (without access to decrypted user assets).

### 2.4 Operating Environment
- **Server Environment:** Docker-orchestrated environment running Linux.
- **Client Environment:** Modern web browsers (Chrome, Firefox, Safari, Edge) on desktop, tablet, and mobile devices.

---

## 3. System Features & Functional Requirements

### 3.1 User Authentication
- **REQ-AUTH-01:** The system shall allow users to register with a valid email and a strong master password (minimum 12 characters).
- **REQ-AUTH-02:** Passwords must be hashed using a strong cryptographic algorithm (e.g., Argon2 or PBKDF2) before storage.
- **REQ-AUTH-03:** The system shall provide secure JWT-based session management.

### 3.2 Digital Vault Management
- **REQ-VLT-01:** The system shall allow the Vault Owner to upload files of categorized types (Legal Document, Photograph, Video, Note).
- **REQ-VLT-02:** All files and text notes MUST be encrypted client-side or immediately upon reaching the server using AES-256-GCM before being stored on disk.
- **REQ-VLT-03:** The system shall display the vault capacity and asset list to the Owner.
- **REQ-VLT-04:** The Owner shall be able to delete ("Purge") assets, which must permanently destroy the ciphertext and associated keys.

### 3.3 Beneficiary (Heir) Management
- **REQ-BEN-01:** The Owner shall be able to add beneficiaries by providing their legal name, relationship, and secure email address.
- **REQ-BEN-02:** The system shall restrict beneficiaries from accessing the vault until the DMS release protocol has successfully completed the cooling-off phase.
- **REQ-BEN-03:** The Owner shall be able to revoke a beneficiary's access at any time before the DMS is triggered.

### 3.4 Dead Man's Switch (DMS) & Heartbeat
- **REQ-DMS-01:** The system shall provide a configurable inactivity threshold (e.g., 30 to 365 days).
- **REQ-DMS-02:** The system shall provide a configurable cooling-off period (e.g., 3 to 30 days).
- **REQ-DMS-03:** The Owner must be able to securely register a "Heartbeat" (proof of life) via the dashboard to reset the inactivity timer.
- **REQ-DMS-04:** A background scheduler (Celery Beat) shall check the last heartbeat timestamp daily.
- **REQ-DMS-05:** If the inactivity threshold is breached, the system enters the warning/cooling-off state and sends alert emails to the Owner.
- **REQ-DMS-06:** If the cooling-off period expires without a heartbeat intervention, the system executes the release protocol, notifying heirs and granting them decryption keys.

### 3.5 Security & Audit Logging
- **REQ-AUD-01:** The system shall log all significant events (logins, vault uploads, DMS config changes, heartbeat registrations).
- **REQ-AUD-02:** Logs shall be immutable and visible to the Owner via the Security Logs dashboard.

---

## 4. Non-Functional Requirements

### 4.1 Performance & Scalability
- The web interface shall load within 2 seconds under normal network conditions.
- The background task queue must efficiently handle daily checks without blocking API requests.
- File uploads should support chunking or asynchronous processing for files larger than 10MB.

### 4.2 Security & Privacy
- **Zero Trust:** The application architecture must ensure that the platform operators cannot arbitrarily decrypt user assets.
- Data in transit must be protected via HTTPS/TLS 1.2+.
- The application must protect against common OWASP vulnerabilities (e.g., CSRF, XSS, SQL Injection).

### 4.3 Usability & UI/UX
- **Responsive Design:** The UI must function flawlessly across desktop (≥1025px), tablet (769–1024px), and mobile (≤768px) devices using a CSS Flexbox/Grid breakpoint system.
- **Aesthetic Guidelines:** The platform must strictly adhere to the "Navy & Gold" Premium Design System, utilizing glassmorphism, precise typography (Syne & DM Sans), and micro-animations to convey a premium, trustworthy feel.
- **Feedback:** The system must provide immediate, elegant visual feedback for all user actions (success/error states) using global toast notifications.

### 4.4 Reliability & Availability
- The system shall rely on Docker Compose to guarantee consistent behavior across development and production environments.
- The database should be configured to support regular automated backups.

---

## 5. Appendices

### 5.1 Technology Stack
- **Frontend:** React 18, TypeScript, Vite, Zustand, react-hot-toast, Lucide React.
- **Backend:** Python, Django 4.2, Django REST Framework, Celery.
- **Infrastructure:** Docker, Docker Compose, PostgreSQL 15, Redis 7.

### 5.2 Glossary
- **DMS (Dead Man's Switch):** An automated protocol that executes a sequence of actions if the owner fails to interact with the system within a specified timeframe.
- **Heartbeat:** An active signal sent by the user to the system confirming they are alive and retaining control of the vault.
- **AES-256-GCM:** Advanced Encryption Standard with a 256-bit key in Galois/Counter Mode; provides both data confidentiality and authenticity.
- **Glassmorphism:** A UI design style emphasizing background blur, translucency, and subtle borders.
