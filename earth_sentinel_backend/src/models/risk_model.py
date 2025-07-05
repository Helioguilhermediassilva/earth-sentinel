import numpy as np
import json
from datetime import datetime, timedelta
import random

class FederatedRiskModel:
    """
    Federated learning-based risk assessment model for disaster prediction.
    
    Author: Hélio Guilherme Dias Silva
    """
    
    def __init__(self):
        self.models = {
            'flood': FloodRiskModel(),
            'earthquake': EarthquakeRiskModel(),
            'fire': FireRiskModel(),
            'extreme_weather': ExtremeWeatherRiskModel()
        }
        self.global_weights = self._initialize_global_weights()
        self.training_history = []
    
    def _initialize_global_weights(self):
        """Initialize global model weights for federated learning"""
        return {
            'flood': np.random.normal(0, 0.1, 10),
            'earthquake': np.random.normal(0, 0.1, 8),
            'fire': np.random.normal(0, 0.1, 12),
            'extreme_weather': np.random.normal(0, 0.1, 15)
        }
    
    def assess_risk(self, location, sensor_data=None):
        """Assess risk using ensemble of specialized models"""
        lat, lon = location['lat'], location['lon']
        
        # Get predictions from all models
        predictions = {}
        for risk_type, model in self.models.items():
            predictions[risk_type] = model.predict(lat, lon, sensor_data)
        
        # Find dominant risk
        dominant_risk = max(predictions.items(), key=lambda x: x[1]['risk_score'])
        risk_type, risk_data = dominant_risk
        
        # Calculate ensemble confidence
        confidence = np.mean([pred['confidence'] for pred in predictions.values()])
        
        # Calculate geofence radius based on risk score and type
        base_radius = risk_data['risk_score'] * 2000  # 0-2km base
        type_multiplier = {'flood': 1.5, 'earthquake': 1.2, 'fire': 2.0, 'extreme_weather': 1.8}
        geofence_radius = base_radius * type_multiplier.get(risk_type, 1.0)
        
        return {
            'risk_score': risk_data['risk_score'],
            'risk_type': risk_type,
            'confidence': confidence,
            'contributing_factors': predictions,
            'geofence_radius': int(geofence_radius),
            'threshold_exceeded': risk_data['risk_score'] > 0.7,
            'recommendation': self._generate_recommendation(risk_data['risk_score'], risk_type),
            'location': location,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendation(self, risk_score, risk_type):
        """Generate actionable recommendations based on risk assessment"""
        if risk_score < 0.3:
            return f"Low {risk_type} risk - Continue normal operations with routine monitoring"
        elif risk_score < 0.6:
            return f"Moderate {risk_type} risk - Increase monitoring frequency and prepare response teams"
        elif risk_score < 0.8:
            return f"High {risk_type} risk - Activate emergency protocols and consider evacuation planning"
        else:
            return f"Critical {risk_type} risk - Immediate emergency response required, initiate evacuation procedures"

class FloodRiskModel:
    """Specialized model for flood risk assessment"""
    
    def __init__(self):
        self.weights = np.array([0.4, 0.3, 0.2, 0.1])  # precipitation, water_level, terrain, soil_moisture
    
    def predict(self, lat, lon, sensor_data=None):
        # Simulate flood risk calculation
        base_risk = abs(np.sin(lat) * np.cos(lon)) * 0.5
        
        # Add sensor data influence if available
        if sensor_data:
            precipitation_factor = min(sensor_data.get('precipitation', 0) / 100.0, 1.0)
            water_level_factor = min(sensor_data.get('water_level', 0) / 10.0, 1.0)
            base_risk += (precipitation_factor * 0.3 + water_level_factor * 0.2)
        
        # Add random variation
        risk_score = np.clip(base_risk + np.random.normal(0, 0.1), 0, 1)
        confidence = np.random.uniform(0.6, 0.9)
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'factors': {
                'precipitation': float(np.random.uniform(0, 100)),
                'water_level': float(np.random.uniform(0, 10)),
                'terrain_slope': float(np.random.uniform(0, 45)),
                'soil_moisture': float(np.random.uniform(0, 100))
            }
        }

class EarthquakeRiskModel:
    """Specialized model for earthquake risk assessment"""
    
    def __init__(self):
        self.weights = np.array([0.5, 0.3, 0.2])  # seismic_activity, geological_stability, historical_data
    
    def predict(self, lat, lon, sensor_data=None):
        # Simulate earthquake risk based on location
        base_risk = abs(lat + lon) % 1.0 * 0.3
        
        # Add seismic sensor data if available
        if sensor_data:
            seismic_factor = min(sensor_data.get('seismic_activity', 0) / 10.0, 1.0)
            base_risk += seismic_factor * 0.4
        
        risk_score = np.clip(base_risk + np.random.normal(0, 0.05), 0, 1)
        confidence = np.random.uniform(0.7, 0.95)
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'factors': {
                'seismic_activity': float(np.random.uniform(0, 10)),
                'geological_stability': float(np.random.uniform(0, 100)),
                'fault_proximity': float(np.random.uniform(0, 50)),
                'historical_frequency': float(np.random.uniform(0, 5))
            }
        }

class FireRiskModel:
    """Specialized model for fire risk assessment"""
    
    def __init__(self):
        self.weights = np.array([0.3, 0.25, 0.25, 0.2])  # temperature, humidity, wind, vegetation
    
    def predict(self, lat, lon, sensor_data=None):
        # Simulate fire risk calculation
        base_risk = abs(np.tan(lat * 0.1) * np.sin(lon * 0.1)) * 0.4
        
        # Weather factors
        if sensor_data:
            temp_factor = min(sensor_data.get('temperature', 20) / 50.0, 1.0)
            humidity_factor = max(0, 1 - sensor_data.get('humidity', 50) / 100.0)
            wind_factor = min(sensor_data.get('wind_speed', 0) / 30.0, 1.0)
            base_risk += (temp_factor * 0.2 + humidity_factor * 0.2 + wind_factor * 0.1)
        
        risk_score = np.clip(base_risk + np.random.normal(0, 0.08), 0, 1)
        confidence = np.random.uniform(0.5, 0.85)
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'factors': {
                'temperature': float(np.random.uniform(15, 45)),
                'humidity': float(np.random.uniform(10, 90)),
                'wind_speed': float(np.random.uniform(0, 25)),
                'vegetation_dryness': float(np.random.uniform(0, 100)),
                'fire_weather_index': float(np.random.uniform(0, 100))
            }
        }

class ExtremeWeatherRiskModel:
    """Specialized model for extreme weather risk assessment"""
    
    def __init__(self):
        self.weights = np.array([0.25, 0.3, 0.25, 0.2])  # wind_speed, pressure, temperature_gradient, humidity
    
    def predict(self, lat, lon, sensor_data=None):
        # Simulate extreme weather risk
        base_risk = abs(np.cos(lat * 0.2) * np.sin(lon * 0.15)) * 0.35
        
        # Meteorological factors
        if sensor_data:
            pressure_factor = abs(sensor_data.get('pressure', 1013) - 1013) / 50.0
            wind_factor = min(sensor_data.get('wind_speed', 0) / 40.0, 1.0)
            base_risk += (pressure_factor * 0.2 + wind_factor * 0.15)
        
        risk_score = np.clip(base_risk + np.random.normal(0, 0.06), 0, 1)
        confidence = np.random.uniform(0.6, 0.9)
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'factors': {
                'wind_speed': float(np.random.uniform(0, 40)),
                'atmospheric_pressure': float(np.random.uniform(980, 1040)),
                'temperature_gradient': float(np.random.uniform(0, 20)),
                'humidity': float(np.random.uniform(20, 95)),
                'storm_probability': float(np.random.uniform(0, 100))
            }
        }

class FederatedLearningSimulator:
    """
    Simulates federated learning training across multiple nodes.
    
    Author: Hélio Guilherme Dias Silva
    """
    
    def __init__(self, num_nodes=3):
        self.num_nodes = num_nodes
        self.global_model = FederatedRiskModel()
        self.node_models = [FederatedRiskModel() for _ in range(num_nodes)]
    
    def simulate_training_round(self):
        """Simulate one round of federated training"""
        local_updates = []
        
        for i, node_model in enumerate(self.node_models):
            # Simulate local training
            node_id = f"node_{i+1}"
            data_size = np.random.randint(15, 25)
            
            # Simulate training metrics
            accuracy = np.random.uniform(0.7, 0.9)
            loss = np.random.uniform(0.1, 0.4)
            precision = np.random.uniform(0.6, 0.8)
            recall = np.random.uniform(0.6, 0.8)
            
            # Simulate weight updates (add noise to global weights)
            updated_weights = {}
            for risk_type, global_weights in self.global_model.global_weights.items():
                noise = np.random.normal(0, 0.01, global_weights.shape)
                updated_weights[risk_type] = global_weights + noise
            
            local_updates.append({
                'node_id': node_id,
                'data_size': data_size,
                'performance_metrics': {
                    'accuracy': float(accuracy),
                    'loss': float(loss),
                    'precision': float(precision),
                    'recall': float(recall)
                },
                'weights': {k: v.tolist() for k, v in updated_weights.items()}
            })
        
        # Simulate federated averaging (FedAvg)
        aggregated_weights = {}
        for risk_type in self.global_model.global_weights.keys():
            # Weighted average based on data size
            total_data = sum(update['data_size'] for update in local_updates)
            weighted_sum = np.zeros_like(self.global_model.global_weights[risk_type])
            
            for update in local_updates:
                weight = update['data_size'] / total_data
                node_weights = np.array(update['weights'][risk_type])
                weighted_sum += weight * node_weights
            
            aggregated_weights[risk_type] = weighted_sum
        
        # Update global model
        self.global_model.global_weights = aggregated_weights
        
        # Calculate aggregated metrics
        total_data_samples = sum(update['data_size'] for update in local_updates)
        avg_accuracy = np.mean([update['performance_metrics']['accuracy'] for update in local_updates])
        avg_loss = np.mean([update['performance_metrics']['loss'] for update in local_updates])
        avg_precision = np.mean([update['performance_metrics']['precision'] for update in local_updates])
        avg_recall = np.mean([update['performance_metrics']['recall'] for update in local_updates])
        
        # Calculate convergence metrics
        weight_stability = np.random.uniform(0.95, 0.999)  # Simulate convergence
        performance_variance = np.var([update['performance_metrics']['accuracy'] for update in local_updates])
        
        return {
            'local_updates': local_updates,
            'training_round': {
                'nodes_participated': self.num_nodes,
                'total_data_samples': int(total_data_samples),
                'average_performance': {
                    'accuracy': float(avg_accuracy),
                    'loss': float(avg_loss),
                    'precision': float(avg_precision),
                    'recall': float(avg_recall)
                },
                'convergence_metrics': {
                    'weight_stability': float(weight_stability),
                    'performance_variance': float(performance_variance)
                },
                'weight_changes': {
                    risk_type: {
                        'mean_change': float(np.mean(np.abs(weights))),
                        'max_change': float(np.max(np.abs(weights))),
                        'std_change': float(np.std(weights))
                    }
                    for risk_type, weights in aggregated_weights.items()
                }
            },
            'updated_weights': {k: v.tolist() for k, v in aggregated_weights.items()},
            'status': 'success'
        }

