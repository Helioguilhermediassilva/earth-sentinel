from src.models.user import db
from datetime import datetime
import json

class SensorNode(db.Model):
    __tablename__ = 'sensor_nodes'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_lat = db.Column(db.Float, nullable=False)
    location_lon = db.Column(db.Float, nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)  # temperature, humidity, seismic, flood, etc.
    status = db.Column(db.String(20), default='active')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': {
                'lat': self.location_lat,
                'lon': self.location_lon
            },
            'sensor_type': self.sensor_type,
            'status': self.status,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), db.ForeignKey('sensor_nodes.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reading_type = db.Column(db.String(50), nullable=False)  # temperature, humidity, vibration, water_level
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    additional_data = db.Column(db.Text)  # JSON string for additional data
    
    sensor = db.relationship('SensorNode', backref=db.backref('readings', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'reading_type': self.reading_type,
            'value': self.value,
            'unit': self.unit,
            'metadata': json.loads(self.additional_data) if self.additional_data else None
        }

class BeneficiaryHousehold(db.Model):
    __tablename__ = 'beneficiary_households'
    
    id = db.Column(db.String(50), primary_key=True)  # Aadhaar-like ID
    head_of_household = db.Column(db.String(100), nullable=False)
    location_lat = db.Column(db.Float, nullable=False)
    location_lon = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.String(20))
    family_size = db.Column(db.Integer, default=1)
    vulnerability_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    payment_account = db.Column(db.String(100))  # Bank account or digital wallet
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    
    def to_dict(self):
        return {
            'id': self.id,
            'head_of_household': self.head_of_household,
            'location': {
                'lat': self.location_lat,
                'lon': self.location_lon
            },
            'address': self.address,
            'phone_number': self.phone_number,
            'family_size': self.family_size,
            'vulnerability_score': self.vulnerability_score,
            'payment_account': self.payment_account,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'status': self.status
        }

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    location_lat = db.Column(db.Float, nullable=False)
    location_lon = db.Column(db.Float, nullable=False)
    risk_type = db.Column(db.String(50), nullable=False)  # flood, earthquake, fire, etc.
    risk_score = db.Column(db.Float, nullable=False)  # 0-1 scale
    confidence = db.Column(db.Float, nullable=False)  # 0-1 scale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    geofence_radius = db.Column(db.Float, default=1000.0)  # meters
    data_sources = db.Column(db.Text)  # JSON string listing data sources used
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': {
                'lat': self.location_lat,
                'lon': self.location_lon
            },
            'risk_type': self.risk_type,
            'risk_score': self.risk_score,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'geofence_radius': self.geofence_radius,
            'data_sources': json.loads(self.data_sources) if self.data_sources else []
        }

