# 💎 Digital Legacy Dashboard
### High-Fidelity React Frontend

This is the premium frontend dashboard for the Digital Legacy Platform, built with **React 18**, **TypeScript**, and **Vite**. It is designed to provide a secure, intuitive, and luxurious user experience for digital estate management.

---

## 🎨 Design System: "Navy & Gold"

The UI implements a custom design system focused on prestige and security.

- **Palette:**
  - `Background`: Deep Navy (`#060912`)
  - `Accent`: Gold (`#d4a853`)
  - `Surfaces`: Translucent Navy with Glassmorphism
- **Typography:**
  - `Headings`: **Syne** (Modern, Geometric)
  - `Body`: **DM Sans** (Clean, Readable)
- **Glassmorphism:** Leverages `backdrop-filter: blur()` for a multi-layered, premium feel.

### 📱 Responsive Strategy
The layout uses a custom breakpoint system implemented in vanilla CSS:
| Breakpoint | Sidebar Mode | Description |
| :--- | :--- | :--- |
| **Desktop (≥ 1025px)** | Expanded | Full 280px sidebar with labels and brand identity. |
| **Tablet (769–1024px)** | Collapsed | Compact 72px icon-only sidebar for maximized workspace. |
| **Mobile (≤ 768px)** | Hidden | Sidebar hidden; accessed via a gold hamburger menu `☰`. |

---

## 🛠️ Technical Architecture

### State Management
We use **Zustand** for lightweight, performant state management.
- **Auth Store:** Handles JWT persistence and user session state.
- **Vault Store:** Manages encrypted asset metadata and upload/download states.
- **DMS Store:** Controls the Dead Man's Switch configuration and heartbeat status.

### Component Structure
- `src/components/Vault`: Handles AES-256-GCM file management.
- `src/components/DMSConfig`: Manages inactivity thresholds and cooling-off periods.
- `src/components/AuditLog`: Displays the immutable security ledger.
- `src/components/Sidebar`: Responsive navigation logic.

---

## 🚀 Development Workflow

### Prerequisites
- Node.js 18+
- npm (v9+)

### Installation
```bash
npm install
```

### Local Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

---

## 🛡️ Best Practices
1. **Strict Typing:** All API responses and store states must be interface-typed.
2. **Modular CSS:** Avoid global style pollution; use the design system tokens defined in `index.css`.
3. **Icons:** Use `lucide-react` for consistent, accessible iconography.
4. **Notifications:** All user feedback must go through the global `react-hot-toast` handler.

---
*Digital Legacy Frontend — ABU Zaria Group 16*
