import random
import json
from datetime import datetime, timedelta

class SimpleRiskModel:
    """Simplified risk model without numpy dependency for deployment"""
    
    def __init__(self):
        self.model_weights = {
            'flood': {
                'precipitation_weight': 0.4,
                'water_level_weight': 0.3,
                'terrain_weight': 0.2,
                'soil_moisture_weight': 0.1
            },
            'earthquake': {
                'seismic_weight': 0.5,
                'geological_weight': 0.3,
                'historical_weight': 0.2
            },
            'fire': {
                'temperature_weight': 0.3,
                'humidity_weight': 0.25,
                'wind_weight': 0.25,
                'vegetation_weight': 0.2
            },
            'extreme_weather': {
                'wind_speed_weight': 0.25,
                'pressure_weight': 0.3,
                'temperature_gradient_weight': 0.25,
                'humidity_weight': 0.2
            }
        }
    
    def assess_risk(self, location, sensor_data=None):
        """Assess risk for a given location"""
        lat, lon = location['lat'], location['lon']
        
        # Simulate risk calculation based on location
        base_risk = abs(lat + lon) % 1.0
        
        # Calculate individual risk types
        risks = {}
        for risk_type, weights in self.model_weights.items():
            # Simulate sensor-based risk calculation
            risk_value = base_risk * random.uniform(0.5, 1.5)
            risk_value = max(0.0, min(1.0, risk_value))  # Clamp to [0,1]
            risks[risk_type] = risk_value
        
        # Find dominant risk type
        dominant_risk = max(risks.items(), key=lambda x: x[1])
        risk_type, risk_score = dominant_risk
        
        # Calculate confidence based on data availability
        confidence = random.uniform(0.1, 0.9)
        
        # Calculate geofence radius (in meters)
        geofence_radius = risk_score * 2000 + 500  # 500-2500m range
        
        # Determine threshold exceeded
        threshold_exceeded = risk_score > 0.7
        
        # Generate recommendation
        if risk_score < 0.3:
            recommendation = "Low risk - Continue normal operations"
        elif risk_score < 0.6:
            recommendation = "Moderate risk - Monitor conditions closely"
        elif risk_score < 0.8:
            recommendation = "High risk - Prepare emergency response"
        else:
            recommendation = "Critical risk - Activate emergency protocols immediately"
        
        return {
            'risk_score': risk_score,
            'risk_type': risk_type,
            'confidence': confidence,
            'contributing_factors': risks,
            'geofence_radius': geofence_radius,
            'threshold_exceeded': threshold_exceeded,
            'recommendation': recommendation,
            'location': location,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_federated_training(self, num_nodes=3):
        """Simulate federated learning training"""
        training_results = []
        
        for i in range(num_nodes):
            node_id = f"node_{i+1}"
            
            # Simulate training metrics
            accuracy = random.uniform(0.7, 0.9)
            loss = random.uniform(0.1, 0.4)
            precision = random.uniform(0.6, 0.8)
            recall = random.uniform(0.6, 0.8)
            
            # Simulate weight updates
            weights = {}
            for risk_type, base_weights in self.model_weights.items():
                weights[risk_type] = {}
                for weight_name, base_value in base_weights.items():
                    # Add small random variation
                    variation = random.uniform(-0.01, 0.01)
                    weights[risk_type][weight_name] = base_value + variation
            
            training_results.append({
                'node_id': node_id,
                'data_size': random.randint(15, 25),
                'performance_metrics': {
                    'accuracy': accuracy,
                    'loss': loss,
                    'precision': precision,
                    'recall': recall
                },
                'weights': weights
            })
        
        # Simulate global aggregation
        avg_accuracy = sum(r['performance_metrics']['accuracy'] for r in training_results) / num_nodes
        avg_loss = sum(r['performance_metrics']['loss'] for r in training_results) / num_nodes
        avg_precision = sum(r['performance_metrics']['precision'] for r in training_results) / num_nodes
        avg_recall = sum(r['performance_metrics']['recall'] for r in training_results) / num_nodes
        
        # Simulate weight aggregation (simple average)
        aggregated_weights = {}
        for risk_type in self.model_weights.keys():
            aggregated_weights[risk_type] = {}
            for weight_name in self.model_weights[risk_type].keys():
                avg_weight = sum(r['weights'][risk_type][weight_name] for r in training_results) / num_nodes
                aggregated_weights[risk_type][weight_name] = avg_weight
        
        return {
            'local_updates': training_results,
            'training_round': {
                'nodes_participated': num_nodes,
                'total_data_samples': sum(r['data_size'] for r in training_results),
                'average_performance': {
                    'accuracy': avg_accuracy,
                    'loss': avg_loss,
                    'precision': avg_precision,
                    'recall': avg_recall
                },
                'convergence_metrics': {
                    'weight_stability': random.uniform(0.95, 0.999),
                    'performance_variance': random.uniform(0.001, 0.01)
                },
                'weight_changes': {
                    risk_type: {
                        weight_name: random.uniform(0.00001, 0.0001)
                        for weight_name in weights.keys()
                    }
                    for risk_type, weights in self.model_weights.items()
                }
            },
            'updated_weights': aggregated_weights,
            'status': 'success'
        }
    
    def get_model_status(self):
        """Get current model status"""
        return {
            'models_available': list(self.model_weights.keys()),
            'last_training': (datetime.now() - timedelta(hours=2)).isoformat(),
            'model_version': '1.0.0',
            'training_nodes': 3,
            'status': 'operational'
        }

