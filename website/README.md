# Live Transcript — Website

Official marketing website for the **Live Transcript** Windows desktop application.

Built with **Next.js 15**, **TypeScript**, **Tailwind CSS**, and **Lucide Icons**.  
Deployable to **Vercel** in one click.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run the dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ⚙️ Configure the Download URL

Before deploying, edit [`src/config/download.ts`](./src/config/download.ts) and replace the placeholder:

```ts
DOWNLOAD_URL: "PLACEHOLDER_DOWNLOAD_URL",
```

with the actual public URL to the Windows executable or installer, e.g.:

```ts
DOWNLOAD_URL: "https://github.com/YOUR_USERNAME/live-transcript/releases/download/v0.1.0/LiveTranscript_Installer.exe",
```

---

## 🏗️ Production Build

```bash
npm run build   # build
npm run start   # preview the production build locally
npm run lint    # check for lint errors
```

---

## 🌐 Deploy to Vercel

### Option A — Vercel CLI

```bash
npm i -g vercel
vercel
```

Follow the prompts. Vercel auto-detects Next.js.

### Option B — GitHub + Vercel Dashboard

1. Push the `website/` folder to a GitHub repository.
2. Go to [vercel.com](https://vercel.com) → **New Project** → import the repo.
3. Set the **Root Directory** to `website` (if this folder is a subdirectory of a larger repo).
4. Click **Deploy**.

Vercel will rebuild and redeploy automatically on every push to `main`.

---

## 📁 Project Structure

```
website/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout + metadata
│   │   ├── page.tsx         # Main page (composes all sections)
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── Hero.tsx
│   │   ├── Features.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── Screenshots.tsx
│   │   ├── SystemRequirements.tsx
│   │   ├── Download.tsx
│   │   ├── FAQ.tsx
│   │   └── Footer.tsx
│   └── config/
│       └── download.ts      # ← Edit this to set the download URL
├── vercel.json
└── next.config.ts
```
