# 💎 Digital Legacy Dashboard
### Premium React Frontend

This is the frontend dashboard for the Digital Legacy Platform, built with **React 18**, **TypeScript**, and **Vite**.

## 🎨 Design System
The UI uses a custom **Navy & Gold** design system implemented in vanilla CSS.
- **Base Tones:** Deep Navy (`#060912`)
- **Primary Accents:** Gold (`#d4a853`)
- **Typography:** Syne (Headings) & DM Sans (Body)
- **Glassmorphism:** Subtle blurs and borders for a premium feel.
- **Global Notifications:** Elegant success/error toasts integrated via `react-hot-toast`.
- **Fully Responsive Layout:**
  | Breakpoint | Sidebar Behaviour |
  |---|---|
  | ≥ 1025px | Full 280px sidebar with all labels |
  | 769–1024px | Collapsed 72px icon-only sidebar |
  | ≤ 768px | Hidden; hamburger `☰` opens a slide-in drawer |

## 🚀 Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Build
```bash
# Production build
npm run build
```

## 🛠️ Structure
- `/src/components`: UI modules
  - `Vault.tsx`, `VaultItemCard.tsx`, `VaultUploadForm.tsx` — vault with extracted sub-components
  - `Sidebar.tsx` — responsive collapsible navigation
  - `Dashboard.tsx`, `Memories.tsx`, `Beneficiaries.tsx`, `DMSConfig.tsx`, `AuditLog.tsx`
  - `Login.tsx`, `Register.tsx` — authentication flows
- `/src/store`: Zustand state with typed API + `react-hot-toast` error handling
- `/src/index.css`: Global styles, design tokens, and responsive breakpoints
- `vite.config.ts`: Configured with polling and HMR for Docker compatibility

## 🛡️ Best Practices
1. **Type Safety:** Always use TypeScript interfaces for store data and API responses.
2. **Components:** Keep components modular and avoid inline styles where global classes exist.
3. **Icons:** Use `lucide-react` for consistent iconography.

---
*Digital Legacy Frontend — Group 16*
