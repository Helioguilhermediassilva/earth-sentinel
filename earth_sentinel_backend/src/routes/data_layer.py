from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import json
import uuid
from src.models.sensor import db, SensorNode, SensorReading, BeneficiaryHousehold, RiskAssessment

data_bp = Blueprint('data', __name__)

# X-Road style interface simulation
@data_bp.route('/xroad/iot-sensors', methods=['GET'])
def get_iot_sensor_data():
    """Simulate X-Road IoT sensor data ingestion"""
    try:
        # Simulate multiple sensor types
        sensor_types = ['temperature', 'humidity', 'seismic', 'water_level', 'air_quality']
        mock_data = []
        
        for i in range(10):  # Generate 10 mock sensors
            sensor_id = f"IOT_{random.randint(1000, 9999)}"
            sensor_type = random.choice(sensor_types)
            
            # Generate realistic coordinates (focusing on disaster-prone areas)
            lat = random.uniform(-23.5, -22.5)  # São Paulo region
            lon = random.uniform(-46.8, -46.3)
            
            # Generate sensor-specific readings
            if sensor_type == 'temperature':
                value = random.uniform(15, 45)  # Celsius
                unit = '°C'
            elif sensor_type == 'humidity':
                value = random.uniform(30, 95)  # Percentage
                unit = '%'
            elif sensor_type == 'seismic':
                value = random.uniform(0, 5)  # Richter scale
                unit = 'magnitude'
            elif sensor_type == 'water_level':
                value = random.uniform(0, 10)  # Meters
                unit = 'm'
            else:  # air_quality
                value = random.uniform(0, 300)  # AQI
                unit = 'AQI'
            
            mock_data.append({
                'sensor_id': sensor_id,
                'timestamp': datetime.utcnow().isoformat(),
                'location': {'lat': lat, 'lon': lon},
                'sensor_type': sensor_type,
                'reading': {
                    'type': sensor_type,
                    'value': round(value, 2),
                    'unit': unit
                },
                'status': 'active',
                'metadata': {
                    'battery_level': random.uniform(20, 100),
                    'signal_strength': random.uniform(50, 100)
                }
            })
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'X-Road IoT Connector',
            'sensor_count': len(mock_data),
            'sensors': mock_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/xroad/satellite-imagery', methods=['GET'])
def get_satellite_imagery():
    """Simulate satellite imagery data ingestion"""
    try:
        # Simulate satellite imagery metadata
        satellites = ['Landsat-8', 'Sentinel-2', 'MODIS', 'VIIRS']
        imagery_types = ['optical', 'thermal', 'radar', 'multispectral']
        
        mock_imagery = []
        for i in range(5):  # Generate 5 mock satellite images
            satellite = random.choice(satellites)
            imagery_type = random.choice(imagery_types)
            
            # Generate bounding box for image coverage
            center_lat = random.uniform(-25, -20)
            center_lon = random.uniform(-48, -43)
            
            mock_imagery.append({
                'image_id': f"SAT_{uuid.uuid4().hex[:8]}",
                'satellite': satellite,
                'imagery_type': imagery_type,
                'timestamp': (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'coverage_area': {
                    'center': {'lat': center_lat, 'lon': center_lon},
                    'bounds': {
                        'north': center_lat + 0.1,
                        'south': center_lat - 0.1,
                        'east': center_lon + 0.1,
                        'west': center_lon - 0.1
                    }
                },
                'resolution': f"{random.choice([10, 30, 100, 250])}m",
                'cloud_coverage': random.uniform(0, 30),
                'quality_score': random.uniform(0.7, 1.0),
                'download_url': f"https://mock-satellite-api.com/images/SAT_{uuid.uuid4().hex[:8]}.tif",
                'metadata': {
                    'bands': random.choice([3, 4, 8, 13]),
                    'file_size_mb': random.uniform(50, 500)
                }
            })
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'X-Road Satellite Connector',
            'image_count': len(mock_imagery),
            'imagery': mock_imagery
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/xroad/weather-data', methods=['GET'])
def get_weather_data():
    """Simulate weather data ingestion"""
    try:
        # Simulate weather stations
        weather_stations = []
        weather_types = ['precipitation', 'wind_speed', 'atmospheric_pressure', 'visibility']
        
        for i in range(8):  # Generate 8 weather stations
            station_id = f"WS_{random.randint(100, 999)}"
            lat = random.uniform(-25, -20)
            lon = random.uniform(-48, -43)
            
            # Generate weather readings
            readings = {}
            for weather_type in weather_types:
                if weather_type == 'precipitation':
                    value = random.uniform(0, 50)  # mm/hour
                    unit = 'mm/h'
                elif weather_type == 'wind_speed':
                    value = random.uniform(0, 30)  # km/h
                    unit = 'km/h'
                elif weather_type == 'atmospheric_pressure':
                    value = random.uniform(980, 1030)  # hPa
                    unit = 'hPa'
                else:  # visibility
                    value = random.uniform(1, 20)  # km
                    unit = 'km'
                
                readings[weather_type] = {
                    'value': round(value, 2),
                    'unit': unit
                }
            
            weather_stations.append({
                'station_id': station_id,
                'timestamp': datetime.utcnow().isoformat(),
                'location': {'lat': lat, 'lon': lon},
                'readings': readings,
                'forecast': {
                    'next_6h': {
                        'precipitation_probability': random.uniform(0, 100),
                        'severe_weather_risk': random.choice(['low', 'medium', 'high'])
                    }
                }
            })
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'X-Road Weather Connector',
            'station_count': len(weather_stations),
            'weather_stations': weather_stations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Identity & Registry Module (MOSIP/Inji style)
@data_bp.route('/registry/sensor-nodes', methods=['POST'])
def register_sensor_node():
    """Register a new sensor node"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name', 'location_lat', 'location_lon', 'sensor_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if sensor already exists
        existing_sensor = SensorNode.query.filter_by(id=data['id']).first()
        if existing_sensor:
            return jsonify({'error': 'Sensor node already registered'}), 409
        
        # Create new sensor node
        sensor = SensorNode(
            id=data['id'],
            name=data['name'],
            location_lat=data['location_lat'],
            location_lon=data['location_lon'],
            sensor_type=data['sensor_type'],
            status=data.get('status', 'active')
        )
        
        db.session.add(sensor)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sensor node registered successfully',
            'sensor': sensor.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/registry/beneficiaries', methods=['POST'])
def register_beneficiary():
    """Register a new beneficiary household"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'head_of_household', 'location_lat', 'location_lon', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if beneficiary already exists
        existing_beneficiary = BeneficiaryHousehold.query.filter_by(id=data['id']).first()
        if existing_beneficiary:
            return jsonify({'error': 'Beneficiary already registered'}), 409
        
        # Create new beneficiary
        beneficiary = BeneficiaryHousehold(
            id=data['id'],
            head_of_household=data['head_of_household'],
            location_lat=data['location_lat'],
            location_lon=data['location_lon'],
            address=data['address'],
            phone_number=data.get('phone_number'),
            family_size=data.get('family_size', 1),
            vulnerability_score=data.get('vulnerability_score', 0.0),
            payment_account=data.get('payment_account'),
            status=data.get('status', 'active')
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Beneficiary registered successfully',
            'beneficiary': beneficiary.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/registry/sensor-nodes', methods=['GET'])
def get_sensor_nodes():
    """Get all registered sensor nodes"""
    try:
        sensors = SensorNode.query.all()
        return jsonify({
            'status': 'success',
            'count': len(sensors),
            'sensors': [sensor.to_dict() for sensor in sensors]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/registry/beneficiaries', methods=['GET'])
def get_beneficiaries():
    """Get all registered beneficiaries"""
    try:
        beneficiaries = BeneficiaryHousehold.query.all()
        return jsonify({
            'status': 'success',
            'count': len(beneficiaries),
            'beneficiaries': [beneficiary.to_dict() for beneficiary in beneficiaries]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Data ingestion endpoint for real-time sensor readings
@data_bp.route('/ingest/sensor-reading', methods=['POST'])
def ingest_sensor_reading():
    """Ingest a new sensor reading"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sensor_id', 'reading_type', 'value', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verify sensor exists
        sensor = SensorNode.query.filter_by(id=data['sensor_id']).first()
        if not sensor:
            return jsonify({'error': 'Sensor node not found'}), 404
        
        # Create new reading
        reading = SensorReading(
            sensor_id=data['sensor_id'],
            reading_type=data['reading_type'],
            value=data['value'],
            unit=data['unit'],
            additional_data=json.dumps(data.get('metadata', {}))
        )
        
        # Update sensor last_seen
        sensor.last_seen = datetime.utcnow()
        
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sensor reading ingested successfully',
            'reading': reading.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

