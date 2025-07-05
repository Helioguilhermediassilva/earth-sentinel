from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid
import json
import requests

from src.models.user import db
from src.models.sensor import RiskAssessment, SensorReading, SensorNode
from src.models.risk_model import (
    FederatedRiskModel, 
    FloodRiskModel, 
    EarthquakeRiskModel, 
    FireRiskModel, 
    ExtremeWeatherRiskModel,
    FederatedLearningSimulator
)
import requests
import random

risk_bp = Blueprint('risk', __name__)

# Initialize global federated model
federated_model = FederatedRiskModel()

@risk_bp.route('/risk/assess', methods=['POST'])
def assess_risk():
    """Assess disaster risk for a given location"""
    try:
        data = request.get_json()
        location = data.get('location')
        
        if not location or 'lat' not in location or 'lon' not in location:
            return jsonify({'error': 'Location with lat/lon required'}), 400
        
        # Get recent sensor data for the area
        sensor_data = get_sensor_data_for_location(location)
        
        # Perform risk assessment using ensemble of models
        assessment_result = federated_model.assess_risk(location, sensor_data)
        
        # Store assessment in database
        assessment = RiskAssessment(
            location_lat=location['lat'],
            location_lon=location['lon'],
            risk_score=assessment_result['risk_score'],
            risk_type=assessment_result['risk_type'],
            confidence=assessment_result['confidence'],
            geofence_radius=assessment_result['geofence_radius'],
            threshold_exceeded=assessment_result['threshold_exceeded'],
            additional_data=json.dumps({
                'contributing_factors': assessment_result['contributing_factors'],
                'recommendation': assessment_result['recommendation'],
                'sensor_data_used': len(sensor_data) if sensor_data else 0
            })
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        # Add assessment_id to response
        assessment_result['assessment_id'] = assessment.id
        assessment_result['status'] = 'success'
        
        return jsonify(assessment_result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_sensor_data_for_location(location, radius_km=10):
    """Get sensor data within radius of location"""
    try:
        # Simulate fetching sensor data from X-Road interface
        response = requests.get('http://localhost:5000/api/xroad/iot-sensors', timeout=5)
        if response.status_code == 200:
            all_sensors = response.json().get('sensors', [])
            
            # Filter sensors within radius (simplified distance calculation)
            nearby_sensors = []
            for sensor in all_sensors:
                if 'location' in sensor:
                    # Simple distance approximation
                    lat_diff = abs(sensor['location']['lat'] - location['lat'])
                    lon_diff = abs(sensor['location']['lon'] - location['lon'])
                    if lat_diff < 0.1 and lon_diff < 0.1:  # Roughly 10km
                        nearby_sensors.append(sensor)
            
            return nearby_sensors
    except:
        pass
    
    # Return simulated data if API call fails
    return [
        {
            'sensor_id': 'SIM_001',
            'type': 'environmental',
            'readings': {
                'temperature': random.uniform(15, 35),
                'humidity': random.uniform(30, 90),
                'pressure': random.uniform(980, 1040),
                'wind_speed': random.uniform(0, 25),
                'precipitation': random.uniform(0, 50)
            }
        }
    ]

@risk_bp.route('/risk/batch-assess', methods=['POST'])
def batch_assess_risk():
    """Perform batch risk assessment for multiple locations"""
    try:
        data = request.get_json()
        locations = data.get('locations', [])
        
        if not locations:
            return jsonify({'error': 'Locations array required'}), 400
        
        results = []
        
        for location in locations:
            if 'lat' not in location or 'lon' not in location:
                continue
                
            sensor_data = get_sensor_data_for_location(location)
            assessment_result = federated_model.assess_risk(location, sensor_data)
            
            # Store in database
            assessment = RiskAssessment(
                location_lat=location['lat'],
                location_lon=location['lon'],
                risk_score=assessment_result['risk_score'],
                risk_type=assessment_result['risk_type'],
                confidence=assessment_result['confidence'],
                geofence_radius=assessment_result['geofence_radius'],
                threshold_exceeded=assessment_result['threshold_exceeded'],
                additional_data=json.dumps({
                    'contributing_factors': assessment_result['contributing_factors'],
                    'recommendation': assessment_result['recommendation']
                })
            )
            
            db.session.add(assessment)
            assessment_result['assessment_id'] = assessment.id
            results.append(assessment_result)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'assessments': results,
            'total_processed': len(results)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@risk_bp.route('/risk/federated/simulate-training', methods=['POST'])
def simulate_federated_training():
    """Simulate federated learning training across multiple nodes"""
    try:
        data = request.get_json()
        num_nodes = data.get('num_nodes', 3)
        
        if num_nodes < 1 or num_nodes > 10:
            return jsonify({'error': 'Number of nodes must be between 1 and 10'}), 400
        
        # Initialize federated learning simulator
        fl_simulator = FederatedLearningSimulator(num_nodes)
        
        # Run training simulation
        training_results = fl_simulator.simulate_training_round()
        
        return jsonify({
            'status': 'success',
            'training_results': training_results['local_updates'],
            'aggregated_results': training_results['training_round'],
            'updated_weights': training_results['updated_weights']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@risk_bp.route('/risk/federated/status', methods=['GET'])
def get_federated_status():
    """Get status of federated learning models"""
    try:
        return jsonify({
            'status': 'success',
            'model_status': {
                'models_available': list(federated_model.models.keys()),
                'last_training': (datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                'model_version': '1.0.0',
                'training_nodes': 3,
                'status': 'operational'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@risk_bp.route('/risk/geofence/<int:assessment_id>', methods=['GET'])
def get_geofence_data(assessment_id):
    """Get geofence data for a specific risk assessment"""
    try:
        assessment = RiskAssessment.query.get(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Generate geofence polygon (simplified circle)
        center_lat = assessment.location_lat
        center_lon = assessment.location_lon
        radius_km = assessment.geofence_radius / 1000.0
        
        # Simple circle approximation with 16 points
        import math
        points = []
        for i in range(16):
            angle = 2 * math.pi * i / 16
            lat_offset = radius_km * math.cos(angle) / 111.0  # Rough km to degree conversion
            lon_offset = radius_km * math.sin(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            points.append({
                'lat': center_lat + lat_offset,
                'lon': center_lon + lon_offset
            })
        
        return jsonify({
            'status': 'success',
            'assessment_id': assessment_id,
            'center': {'lat': center_lat, 'lon': center_lon},
            'radius_meters': assessment.geofence_radius,
            'polygon_points': points,
            'risk_level': assessment.risk_type,
            'risk_score': assessment.risk_score
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@risk_bp.route('/risk/history', methods=['GET'])
def get_risk_history():
    """Get historical risk assessments"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        assessments = RiskAssessment.query.order_by(
            RiskAssessment.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        results = []
        for assessment in assessments:
            additional_data = json.loads(assessment.additional_data) if assessment.additional_data else {}
            
            results.append({
                'id': assessment.id,
                'location': {
                    'lat': assessment.location_lat,
                    'lon': assessment.location_lon
                },
                'risk_score': assessment.risk_score,
                'risk_type': assessment.risk_type,
                'confidence': assessment.confidence,
                'geofence_radius': assessment.geofence_radius,
                'threshold_exceeded': assessment.threshold_exceeded,
                'timestamp': assessment.created_at.isoformat(),
                'contributing_factors': additional_data.get('contributing_factors', {}),
                'recommendation': additional_data.get('recommendation', '')
            })
        
        return jsonify({
            'status': 'success',
            'assessments': results,
            'total_returned': len(results),
            'offset': offset,
            'limit': limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@risk_bp.route('/risk/trends', methods=['GET'])
def get_risk_trends():
    """Get risk trend analysis"""
    try:
        # Get recent assessments for trend analysis
        recent_assessments = RiskAssessment.query.order_by(
            RiskAssessment.created_at.desc()
        ).limit(100).all()
        
        if not recent_assessments:
            return jsonify({
                'status': 'success',
                'trends': {
                    'average_risk_score': 0,
                    'risk_type_distribution': {},
                    'high_risk_areas': [],
                    'trend_direction': 'stable'
                }
            }), 200
        
        # Calculate trends
        total_score = sum(a.risk_score for a in recent_assessments)
        avg_risk_score = total_score / len(recent_assessments)
        
        # Risk type distribution
        risk_types = {}
        for assessment in recent_assessments:
            risk_type = assessment.risk_type
            risk_types[risk_type] = risk_types.get(risk_type, 0) + 1
        
        # High risk areas (score > 0.7)
        high_risk_areas = []
        for assessment in recent_assessments:
            if assessment.risk_score > 0.7:
                high_risk_areas.append({
                    'location': {
                        'lat': assessment.location_lat,
                        'lon': assessment.location_lon
                    },
                    'risk_score': assessment.risk_score,
                    'risk_type': assessment.risk_type,
                    'timestamp': assessment.created_at.isoformat()
                })
        
        # Simple trend direction (compare first and last half)
        mid_point = len(recent_assessments) // 2
        first_half_avg = sum(a.risk_score for a in recent_assessments[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(a.risk_score for a in recent_assessments[mid_point:]) / (len(recent_assessments) - mid_point)
        
        if second_half_avg > first_half_avg + 0.05:
            trend_direction = 'increasing'
        elif second_half_avg < first_half_avg - 0.05:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        return jsonify({
            'status': 'success',
            'trends': {
                'average_risk_score': avg_risk_score,
                'risk_type_distribution': risk_types,
                'high_risk_areas': high_risk_areas[:10],  # Limit to top 10
                'trend_direction': trend_direction,
                'total_assessments_analyzed': len(recent_assessments)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

