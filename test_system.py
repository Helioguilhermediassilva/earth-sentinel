#!/usr/bin/env python3
"""
Earth Sentinel System Test Suite
Comprehensive testing of all system components and integrations
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE = 'http://localhost:5000/api'

class EarthSentinelTester:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test(self, test_name, success, message="", data=None):
        """Log test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name} - {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_data_layer(self):
        """Test X-Road data layer APIs"""
        print("\n=== TESTING DATA LAYER ===")
        
        # Test IoT sensors
        try:
            response = requests.get(f"{API_BASE}/xroad/iot-sensors")
            data = response.json()
            if response.status_code == 200 and 'sensors' in data:
                self.log_test("IoT Sensors API", True, f"Retrieved {len(data['sensors'])} sensors")
            else:
                self.log_test("IoT Sensors API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("IoT Sensors API", False, str(e))
        
        # Test satellite imagery
        try:
            response = requests.get(f"{API_BASE}/xroad/satellite-imagery")
            data = response.json()
            if response.status_code == 200 and 'images' in data:
                self.log_test("Satellite Imagery API", True, f"Retrieved {len(data['images'])} images")
            else:
                self.log_test("Satellite Imagery API", False, f"Status: {response.status_code}, Data: {data}")
        except Exception as e:
            self.log_test("Satellite Imagery API", False, str(e))
        
        # Test weather data
        try:
            response = requests.get(f"{API_BASE}/xroad/weather-data")
            data = response.json()
            if response.status_code == 200 and 'weather_stations' in data:
                self.log_test("Weather Data API", True, f"Retrieved {len(data['weather_stations'])} stations")
            else:
                self.log_test("Weather Data API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Weather Data API", False, str(e))
    
    def test_risk_modeling(self):
        """Test risk assessment and federated learning"""
        print("\n=== TESTING RISK MODELING ===")
        
        # Test risk assessment
        try:
            payload = {"location": {"lat": -23.5505, "lon": -46.6333}}
            response = requests.post(f"{API_BASE}/risk/assess", json=payload)
            data = response.json()
            if response.status_code in [200, 201] and 'risk_score' in data:
                score = data['risk_score']
                self.log_test("Risk Assessment", True, f"Risk score: {score:.3f}, Type: {data.get('risk_type', 'unknown')}")
            else:
                self.log_test("Risk Assessment", False, f"Status: {response.status_code}, Data: {data}")
        except Exception as e:
            self.log_test("Risk Assessment", False, str(e))
        
        # Test federated learning simulation
        try:
            payload = {"num_nodes": 3}
            response = requests.post(f"{API_BASE}/risk/federated/simulate-training", json=payload)
            data = response.json()
            if response.status_code in [200, 201] and 'training_results' in data:
                self.log_test("Federated Learning", True, f"Trained on {len(data['training_results'])} nodes")
            else:
                self.log_test("Federated Learning", False, f"Status: {response.status_code}, Data: {data}")
        except Exception as e:
            self.log_test("Federated Learning", False, str(e))
    
    def test_smart_contracts(self):
        """Test smart contract system"""
        print("\n=== TESTING SMART CONTRACTS ===")
        
        # Create a test contract
        try:
            contract_data = {
                "conditions": [
                    {
                        "condition_type": "risk_threshold",
                        "parameters": {"threshold": 0.8},
                        "description": "Test contract for high risk"
                    }
                ],
                "payment_instructions": [
                    {
                        "beneficiary_id": "TEST_001",
                        "amount": 500,
                        "currency": "USD",
                        "payment_method": "aadhaar_bridge",
                        "priority": 1,
                        "metadata": {"purpose": "Test payment"}
                    }
                ]
            }
            response = requests.post(f"{API_BASE}/contracts/create", json=contract_data)
            data = response.json()
            if response.status_code in [200, 201] and 'contract_id' in data:
                contract_id = data['contract_id']
                self.log_test("Contract Creation", True, f"Created contract: {contract_id[:8]}...")
                return contract_id
            else:
                self.log_test("Contract Creation", False, f"Status: {response.status_code}, Data: {data}")
                return None
        except Exception as e:
            self.log_test("Contract Creation", False, str(e))
            return None
    
    def test_payment_systems(self):
        """Test payment bridge systems"""
        print("\n=== TESTING PAYMENT SYSTEMS ===")
        
        # Test Aadhaar Payment Bridge
        try:
            payment_data = {
                "beneficiary_aadhaar": "1234567890123456",
                "amount": 750,
                "currency": "USD",
                "purpose": "Test emergency payment"
            }
            response = requests.post(f"{API_BASE}/payments/aadhaar-bridge", json=payment_data)
            data = response.json()
            if response.status_code == 200 and data.get('status') == 'success':
                self.log_test("Aadhaar Payment", True, f"Transaction: {data.get('transaction_id', 'unknown')}")
            else:
                self.log_test("Aadhaar Payment", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Aadhaar Payment", False, str(e))
        
        # Test OpenG2P program creation
        try:
            program_data = {
                "program_name": "Test Emergency Relief Program",
                "budget": 50000,
                "criteria": {
                    "disaster_affected": True,
                    "income_threshold": 30000,
                    "vulnerability_score": 0.7
                }
            }
            response = requests.post(f"{API_BASE}/payments/openg2p/program", json=program_data)
            data = response.json()
            if response.status_code in [200, 201] and 'program' in data:
                program_id = data['program']['program_id']
                self.log_test("OpenG2P Program", True, f"Created program: {program_id[:8]}...")
            else:
                self.log_test("OpenG2P Program", False, f"Status: {response.status_code}, Data: {data}")
        except Exception as e:
            self.log_test("OpenG2P Program", False, str(e))
    
    def test_dispatch_system(self):
        """Test BeckN dispatch and fulfillment"""
        print("\n=== TESTING DISPATCH SYSTEM ===")
        
        # Test resource discovery
        try:
            discovery_data = {
                "location": {"lat": -23.5505, "lon": -46.6333},
                "resource_type": "drone",
                "requirements": {"capabilities": ["aerial_surveillance"]},
                "max_distance_km": 25
            }
            response = requests.post(f"{API_BASE}/dispatch/resources/discover", json=discovery_data)
            data = response.json()
            if response.status_code == 200 and 'resources' in data:
                self.log_test("Resource Discovery", True, f"Found {len(data['resources'])} available drones")
            else:
                self.log_test("Resource Discovery", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resource Discovery", False, str(e))
        
        # Test dispatch request
        try:
            dispatch_data = {
                "requester_id": "test_operator",
                "location": {
                    "lat": -23.5505,
                    "lon": -46.6333,
                    "address": "Test Emergency Location"
                },
                "resource_type": "drone",
                "priority": 1,
                "requirements": {"capabilities": ["aerial_surveillance"]},
                "description": "Test emergency dispatch"
            }
            response = requests.post(f"{API_BASE}/dispatch/request", json=dispatch_data)
            data = response.json()
            if response.status_code == 201 and 'assignment' in data and data['assignment']:
                assignment_id = data['assignment']['assignment_id']
                self.log_test("Dispatch Request", True, f"Assignment: {assignment_id[:8]}...")
                return assignment_id
            else:
                self.log_test("Dispatch Request", False, f"Status: {response.status_code}, No assignment created")
                return None
        except Exception as e:
            self.log_test("Dispatch Request", False, str(e))
            return None
    
    def test_emergency_simulation(self):
        """Test end-to-end emergency simulation"""
        print("\n=== TESTING EMERGENCY SIMULATION ===")
        
        try:
            simulation_data = {
                "emergency_type": "earthquake",
                "location": {
                    "lat": -23.5505,
                    "lon": -46.6333,
                    "address": "São Paulo Test Emergency"
                }
            }
            response = requests.post(f"{API_BASE}/dispatch/simulate-emergency", json=simulation_data)
            data = response.json()
            if response.status_code == 200 and 'emergency_simulation' in data:
                dispatched = data['emergency_simulation']['resources_dispatched']
                self.log_test("Emergency Simulation", True, f"Dispatched {dispatched} resources")
            else:
                self.log_test("Emergency Simulation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Emergency Simulation", False, str(e))
    
    def test_system_integration(self):
        """Test full system integration workflow"""
        print("\n=== TESTING SYSTEM INTEGRATION ===")
        
        try:
            # Step 1: Create risk assessment
            risk_response = requests.post(f"{API_BASE}/risk/assess", json={
                "location": {"lat": -23.5505, "lon": -46.6333}
            })
            
            if risk_response.status_code not in [200, 201]:
                self.log_test("Integration Test", False, f"Risk assessment failed: {risk_response.status_code}")
                return
            
            risk_data = risk_response.json()
            assessment_id = risk_data.get('assessment_id')
            
            # Step 2: Trigger contracts based on risk
            trigger_response = requests.post(f"{API_BASE}/contracts/auto-trigger", json={
                "risk_assessment_id": assessment_id
            })
            
            if trigger_response.status_code != 200:
                self.log_test("Integration Test", False, "Contract trigger failed")
                return
            
            # Step 3: Simulate emergency dispatch
            dispatch_response = requests.post(f"{API_BASE}/dispatch/simulate-emergency", json={
                "emergency_type": "general",
                "location": {"lat": -23.5505, "lon": -46.6333}
            })
            
            if dispatch_response.status_code == 200:
                self.log_test("Integration Test", True, "Full workflow completed successfully")
            else:
                self.log_test("Integration Test", False, "Dispatch simulation failed")
                
        except Exception as e:
            self.log_test("Integration Test", False, str(e))
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("EARTH SENTINEL TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Test Duration: {datetime.now() - self.start_time}")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        
        # Save detailed report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'duration': str(datetime.now() - self.start_time),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results
        }
        
        with open('/home/ubuntu/earth-sentinel/test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return passed_tests == total_tests

def main():
    """Run all tests"""
    print("Earth Sentinel System Test Suite")
    print("Starting comprehensive system testing...")
    
    tester = EarthSentinelTester()
    
    # Run all test suites
    tester.test_data_layer()
    tester.test_risk_modeling()
    tester.test_smart_contracts()
    tester.test_payment_systems()
    tester.test_dispatch_system()
    tester.test_emergency_simulation()
    tester.test_system_integration()
    
    # Generate final report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

