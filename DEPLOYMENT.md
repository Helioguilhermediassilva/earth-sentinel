# Earth Sentinel - Deployment Guide

**Author:** Hélio Guilherme Dias Silva

## Live Demo

The Earth Sentinel platform is currently deployed and accessible at:

- **Frontend Dashboard:** https://ejzxynwc.manus.space
- **Backend APIs:** https://e5h6i7c0w3x7.manus.space

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- 4GB RAM minimum
- 10GB disk space

### Backend Setup
```bash
cd earth_sentinel_backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd earth_sentinel_frontend
pnpm install
pnpm run dev --host
```

## Production Deployment

### Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm run build

EXPOSE 5173
CMD ["pnpm", "run", "preview", "--host"]
```

### Cloud Deployment

#### Heroku
```bash
# Backend
heroku create earth-sentinel-backend
git subtree push --prefix earth_sentinel_backend heroku main

# Frontend
heroku create earth-sentinel-frontend
git subtree push --prefix earth_sentinel_frontend heroku main
```

#### Vercel (Frontend)
```bash
cd earth_sentinel_frontend
vercel --prod
```

#### Railway
```bash
railway login
railway new earth-sentinel
railway up
```

## Environment Variables

### Backend (.env)
```bash
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=https://your-backend-url.com/api
VITE_APP_TITLE=Earth Sentinel
```

## API Endpoints

### Core APIs
- `GET /api/health` - Health check
- `POST /api/risk/assess` - Risk assessment
- `POST /api/contracts/create` - Create smart contract
- `POST /api/payments/aadhaar-bridge` - Process payment
- `POST /api/dispatch/request` - Request resource dispatch

### Data Layer
- `GET /api/xroad/iot-sensors` - IoT sensor data
- `GET /api/xroad/satellite-imagery` - Satellite imagery
- `GET /api/xroad/weather-data` - Weather data

### Federated Learning
- `POST /api/risk/federated/simulate-training` - Simulate FL training
- `GET /api/risk/federated/status` - Model status

## Testing

### Automated Tests
```bash
python test_system.py
```

### Manual Testing
1. Access frontend at deployed URL
2. Click "Trigger Event" to simulate emergency
3. Navigate through all dashboard tabs
4. Verify real-time data updates

## Monitoring

### Health Checks
- Backend: `GET /api/health`
- Frontend: Check if dashboard loads

### Metrics
- Response times
- Error rates
- Resource utilization
- User activity

## Security

### Authentication
- API key authentication for external integrations
- JWT tokens for user sessions
- Role-based access control

### Data Protection
- Encryption at rest and in transit
- PII anonymization
- GDPR compliance features

## Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check Python version
python3 --version

# Verify dependencies
pip list

# Check port availability
netstat -an | grep 5000
```

#### Frontend Build Errors
```bash
# Clear cache
pnpm store prune

# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Database Errors
```bash
# Reset database
rm src/database/app.db
python src/main.py
```

## Support

For technical support:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Earth Sentinel** - Advanced Disaster Response Technology by Hélio Guilherme Dias Silva

