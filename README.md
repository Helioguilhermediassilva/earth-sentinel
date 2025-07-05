# Earth Sentinel - Anticipatory Disaster Response Platform

**Author:** Hélio Guilherme Dias Silva  
**Project:** Advanced Disaster Response System with AI and Blockchain Integration

## Overview

Earth Sentinel is a comprehensive anticipatory disaster response platform that leverages cutting-edge technologies including federated learning, smart contracts, and autonomous resource dispatch to create an integrated emergency management system.

## Features

### 🌍 Data Layer
- **X-Road Integration**: Secure data ingestion from IoT sensors, satellite imagery, and weather stations
- **Identity Registry**: MOSIP/Inji-style identity management for sensors and beneficiaries
- **Real-time Data Processing**: Continuous monitoring and data validation

### 🧠 Risk Modeling
- **Federated Learning**: Distributed machine learning for privacy-preserving risk assessment
- **Multi-hazard Models**: Specialized models for floods, earthquakes, fires, and extreme weather
- **Geofencing**: Automatic risk zone definition with confidence scoring

### 🔗 Smart Contracts
- **OpenSPP Trust Framework**: Blockchain-based automated decision making
- **Threshold Triggers**: Automatic activation based on risk scores
- **Multi-signature Verification**: Consensus-based contract execution

### 💰 Payment Systems
- **Aadhaar Payment Bridge**: Secure biometric payment processing
- **OpenG2P Integration**: Social protection program management
- **Multi-currency Support**: Flexible payment methods and currencies

### 🚁 Dispatch & Fulfillment
- **BeckN Discovery**: Resource discovery and matching algorithms
- **Autonomous Vehicles**: Drone and AGV coordination
- **Real-time Tracking**: GPS monitoring and progress updates

### 📊 Frontend Dashboard
- **Real-time Visualization**: Interactive risk maps and monitoring
- **Multi-tab Interface**: Organized access to all system functions
- **Responsive Design**: Desktop and mobile compatibility

## Architecture

![Earth Sentinel Architecture](earth_sentinel_architecture_diagram.png)

The system follows a microservices architecture with the following key components:

1. **Data Layer**: X-Road interface for secure data ingestion
2. **Risk Modeling**: Federated learning infrastructure
3. **Smart Contracts**: OpenSPP trust framework
4. **Payment Bridge**: Aadhaar and OpenG2P integration
5. **Dispatch System**: BeckN-style resource coordination
6. **Frontend**: React-based dashboard

## Prerequisites

### System Requirements
- Python 3.11+
- Node.js 20+
- 4GB RAM minimum
- 10GB disk space

### Dependencies
- Flask (backend framework)
- React (frontend framework)
- SQLAlchemy (database ORM)
- NumPy (numerical computing)
- Requests (HTTP client)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd earth-sentinel
```

### 2. Backend Setup
```bash
cd earth_sentinel_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-cors flask-sqlalchemy numpy requests

# Initialize database
python src/main.py
```

### 3. Frontend Setup
```bash
cd ../earth_sentinel_frontend

# Install dependencies
pnpm install

# Start development server
pnpm run dev --host
```

## Running the System

### Start Backend Server
```bash
cd earth_sentinel_backend
source venv/bin/activate
python src/main.py
```
Backend will be available at: http://localhost:5000

### Start Frontend Server
```bash
cd earth_sentinel_frontend
pnpm run dev --host
```
Frontend will be available at: http://localhost:5173

## API Documentation

### Data Layer APIs

#### IoT Sensors
```http
GET /api/xroad/iot-sensors
```
Returns simulated IoT sensor data including environmental readings.

#### Satellite Imagery
```http
GET /api/xroad/satellite-imagery
```
Returns satellite image metadata and download links.

#### Weather Data
```http
GET /api/xroad/weather-data
```
Returns weather station data and forecasts.

### Risk Assessment APIs

#### Assess Risk
```http
POST /api/risk/assess
Content-Type: application/json

{
  "location": {
    "lat": -23.5505,
    "lon": -46.6333
  }
}
```

#### Federated Learning Simulation
```http
POST /api/risk/federated/simulate-training
Content-Type: application/json

{
  "num_nodes": 3
}
```

### Smart Contract APIs

#### Create Contract
```http
POST /api/contracts/create
Content-Type: application/json

{
  "conditions": [
    {
      "condition_type": "risk_threshold",
      "parameters": {"threshold": 0.7},
      "description": "Trigger when risk exceeds 0.7"
    }
  ],
  "payment_instructions": [
    {
      "beneficiary_id": "BEN_001",
      "amount": 1000,
      "currency": "USD",
      "payment_method": "aadhaar_bridge",
      "priority": 1
    }
  ]
}
```

#### Auto-trigger Contracts
```http
POST /api/contracts/auto-trigger
Content-Type: application/json

{
  "risk_assessment_id": 1
}
```

### Payment APIs

#### Aadhaar Payment Bridge
```http
POST /api/payments/aadhaar-bridge
Content-Type: application/json

{
  "beneficiary_aadhaar": "1234567890123456",
  "amount": 1000,
  "currency": "USD",
  "purpose": "Emergency relief"
}
```

#### OpenG2P Program
```http
POST /api/payments/openg2p/program
Content-Type: application/json

{
  "program_name": "Emergency Relief Program",
  "budget": 100000,
  "criteria": {
    "disaster_affected": true,
    "income_threshold": 50000
  }
}
```

### Dispatch APIs

#### Discover Resources
```http
POST /api/dispatch/resources/discover
Content-Type: application/json

{
  "location": {"lat": -23.5505, "lon": -46.6333},
  "resource_type": "drone",
  "requirements": {"capabilities": ["aerial_surveillance"]},
  "max_distance_km": 30
}
```

#### Create Dispatch Request
```http
POST /api/dispatch/request
Content-Type: application/json

{
  "requester_id": "emergency_operator_001",
  "location": {
    "lat": -23.5505,
    "lon": -46.6333,
    "address": "Emergency Zone"
  },
  "resource_type": "drone",
  "priority": 1,
  "description": "Emergency surveillance needed"
}
```

#### Track Assignment
```http
GET /api/dispatch/assignment/{assignment_id}/track
```

## Testing

### Run Test Suite
```bash
cd earth-sentinel
python3 test_system.py
```

The test suite validates:
- All API endpoints
- Data layer integration
- Risk modeling functionality
- Smart contract execution
- Payment processing
- Dispatch coordination
- End-to-end workflows

### Manual Testing

1. **Access Frontend**: Open http://localhost:5173
2. **Trigger Event**: Click "Trigger Event" button to simulate emergency
3. **Monitor Dashboard**: Watch real-time updates across all tabs
4. **Check APIs**: Use curl or Postman to test individual endpoints

## Deployment

### Production Deployment

#### Backend Deployment
```bash
# Build for production
cd earth_sentinel_backend
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

#### Frontend Deployment
```bash
# Build for production
cd earth_sentinel_frontend
pnpm run build

# Serve static files
pnpm run preview --host
```

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

#### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./earth_sentinel_backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
  
  frontend:
    build: ./earth_sentinel_frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

### Cloud Deployment

#### Google Cloud Platform
```bash
# Deploy backend
gcloud app deploy earth_sentinel_backend/app.yaml

# Deploy frontend
gcloud app deploy earth_sentinel_frontend/app.yaml
```

#### AWS
```bash
# Deploy with Elastic Beanstalk
eb init earth-sentinel
eb create production
eb deploy
```

## Configuration

### Environment Variables

#### Backend (.env)
```bash
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=*
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_TITLE=Earth Sentinel
```

### Database Configuration

The system uses SQLite by default. For production, configure PostgreSQL:

```python
# src/main.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/earthsentinel'
```

## Monitoring and Logging

### Application Monitoring
- Health check endpoint: `/api/health`
- Metrics endpoint: `/api/metrics`
- System status: `/api/dispatch/dashboard`

### Log Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earth_sentinel.log'),
        logging.StreamHandler()
    ]
)
```

## Security

### Authentication
- API key authentication for external integrations
- JWT tokens for user sessions
- Role-based access control

### Data Protection
- Encryption at rest and in transit
- PII anonymization
- GDPR compliance features

### Network Security
- HTTPS enforcement
- CORS configuration
- Rate limiting

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

### Performance Optimization

#### Backend
- Use Redis for caching
- Implement connection pooling
- Enable gzip compression

#### Frontend
- Enable code splitting
- Optimize bundle size
- Use CDN for static assets

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Write comprehensive tests
- Document all APIs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## Acknowledgments

- OpenSPP for smart contract framework
- BeckN for discovery protocols
- MOSIP for identity management
- X-Road for data exchange standards

---

**Earth Sentinel** - Building resilient communities through anticipatory disaster response.

