# 📊 TPS19 APEX - Vercel Dashboard

Real-time monitoring dashboard for the TPS19 APEX Trading Organism.

## 🚀 Features

- **Real-Time Monitoring**: Live WebSocket updates every 2 seconds
- **Organism Health**: Visual health metrics and consciousness monitoring
- **Live Trading**: Active positions with real-time P&L tracking
- **Performance Charts**: Historical performance visualization
- **Strategy Comparison**: Side-by-side strategy performance
- **AI Intelligence**: ML model confidence and brain activity
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Professional trading interface

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Running TPS19 APEX Organism (for live data)
- API Server running on port 5000 (included)

## 🛠️ Installation

### 1. Install Dashboard Dependencies

```bash
cd dashboard
npm install
```

### 2. Install API Server Dependencies

```bash
pip install flask flask-cors flask-socketio
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your settings
```

## 🏃 Running Locally

### Terminal 1: Start API Server

```bash
python3 api_server.py
```

This starts the Flask API server on `http://localhost:5000`

### Terminal 2: Start Dashboard

```bash
cd dashboard
npm run dev
```

Dashboard will be available at `http://localhost:3000`

### Terminal 3: Run Organism (Optional)

```bash
python3 tps19_apex.py
```

## 📦 Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Main dashboard page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── OrganismHealth.tsx  # Health visualization
│   │   ├── LiveTrading.tsx     # Trading positions
│   │   ├── PerformanceCharts.tsx
│   │   ├── StrategyComparison.tsx
│   │   ├── AIIntelligence.tsx
│   │   └── SystemStatus.tsx
│   └── hooks/
│       └── useOrganismData.ts  # Data fetching hook
├── public/
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── vercel.json                 # Vercel configuration

api_server.py                   # Flask API server
```

## 🚀 Deploying to Vercel

### 1. Deploy API Server

First, deploy the API server (can use Railway, Render, or any Python hosting):

```bash
# Option 1: Railway
railway up

# Option 2: Render
# Push to GitHub and connect via Render dashboard

# Option 3: Your own server
python3 api_server.py
```

### 2. Deploy Dashboard to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd dashboard
vercel

# Or push to GitHub and connect via Vercel dashboard
```

### 3. Configure Environment Variables

In Vercel dashboard, add:

- `NEXT_PUBLIC_API_URL`: Your Vercel app URL
- `NEXT_PUBLIC_WS_URL`: Your API server URL
- `ORGANISM_API_URL`: Your API server URL

### 4. Update vercel.json

Edit `dashboard/vercel.json` and replace `your-organism-api.com` with your actual API URL.

## 🔧 Configuration

### API Endpoints

The API server exposes:

- `GET /api/vitals` - Complete organism status
- `GET /api/health` - Health metrics
- `GET /api/trading` - Trading positions
- `GET /api/performance` - Performance metrics
- `GET /api/strategies` - Strategy comparison
- `WebSocket /` - Real-time updates

### WebSocket Events

- `connect` - Client connection established
- `organism_update` - Real-time data update (every 2s)
- `request_update` - Manually request data update

### Mock Data

If the API server can't connect to the organism, it falls back to mock data for demonstration.

## 📊 Components Overview

### OrganismHealth
- Health score visualization (0-100)
- Consciousness level
- Metabolic rate
- Immune system status
- Real-time status badge

### LiveTrading
- Daily & total P&L
- Active positions list
- Entry/current prices
- Real-time P&L updates
- Position details

### PerformanceCharts
- Equity curve
- Win rate over time
- Drawdown chart
- Strategy performance

### StrategyComparison
- Strategy win rates
- P&L by strategy
- Trade count
- Performance ranking

### AIIntelligence
- ML model confidence
- Brain activity signals
- Model weight distribution
- Decision metrics

### SystemStatus
- Connection status
- Uptime
- System metrics
- Quick actions

## 🎨 Customization

### Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  primary: {
    500: '#0ea5e9',  // Main brand color
    // ... other shades
  },
}
```

### Update Frequency

Edit `api_server.py`:

```python
def background_updates():
    while True:
        time.sleep(2)  # Change update frequency
        # ...
```

### Theme

Toggle between dark/light mode in `src/app/layout.tsx`:

```tsx
<html lang="en" className="dark">  {/* Remove "dark" for light mode */}
```

## 🔒 Security

### Production Checklist:

- [ ] Add authentication to API endpoints
- [ ] Enable CORS only for your domain
- [ ] Use HTTPS for all connections
- [ ] Add rate limiting
- [ ] Sanitize all inputs
- [ ] Use environment variables for secrets
- [ ] Enable WebSocket authentication

### Example: Add API Key

```python
# api_server.py
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/vitals')
@require_api_key
def get_vitals():
    # ...
```

## 🐛 Troubleshooting

### Dashboard shows "Disconnected"

1. Check API server is running: `curl http://localhost:5000/api/health`
2. Check WebSocket URL in `.env.local`
3. Check browser console for errors

### No data showing

1. Verify organism is running
2. Check API server logs
3. Try refreshing the page
4. Check `/api/vitals` endpoint directly

### Build errors

```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

## 📚 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Real-time**: Socket.IO
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **API**: Flask + Flask-SocketIO

## 🤝 Contributing

This dashboard is part of the TPS19 APEX Organism project. Follow the CURSOR MASTER KEY PROCEDURE for all enhancements.

## 📄 License

Part of TPS19 APEX Organism - Proprietary

---

**Built with ❤️ for the TPS19 APEX Organism**

For questions or issues, see the main project documentation.
