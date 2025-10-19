# APEX V3 Web Dashboard

3Commas-style trading dashboard for APEX V3

## 🚀 Quick Start

### Local Development

```bash
cd web-dashboard

# Install dependencies
npm install

# Run development server
npm run dev
```

Open http://localhost:3000

### Deploy to Vercel

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
cd web-dashboard
vercel
```

3. **Follow prompts:**
- Link to existing project or create new
- Configure project settings
- Deploy!

### OR Deploy via Git

1. Push to GitHub:
```bash
git add web-dashboard/
git commit -m "Add web dashboard"
git push
```

2. Go to https://vercel.com
3. Click "New Project"
4. Import your GitHub repo
5. Vercel auto-detects Next.js
6. Click "Deploy"

## 📊 Features

- **Dashboard** - Overview of performance, trades, bots
- **Bot Management** - Start/stop/configure trading bots
- **Positions** - View and manage open positions
- **Trade History** - Complete trading history
- **Settings** - Configure API keys, risk settings
- **Real-time Updates** - Live system status
- **Dark Mode** - 3Commas-style dark theme

## 🔧 Configuration

Set environment variables in Vercel dashboard:

- `API_URL` - Backend API URL (default: http://localhost:8000)

## 🎨 Tech Stack

- Next.js 14
- React 18
- TailwindCSS
- TypeScript
- Recharts (for charts)

## 📱 Responsive

Works on:
- Desktop
- Tablet
- Mobile

## 🔒 Security

- API keys stored in environment variables
- No sensitive data in code
- Secure API communication

## 🚀 Production Ready

- Optimized build
- Fast page loads
- SEO friendly
- PWA ready
