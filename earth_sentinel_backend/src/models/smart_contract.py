from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import hashlib

class ContractStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXECUTED = "executed"
    FAILED = "failed"
    EXPIRED = "expired"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class ContractCondition:
    """Defines a condition for smart contract execution"""
    condition_type: str  # risk_threshold, time_based, manual_trigger
    parameters: Dict
    description: str

@dataclass
class PaymentInstruction:
    """Payment instruction for beneficiaries"""
    beneficiary_id: str
    amount: float
    currency: str
    payment_method: str  # aadhaar_bridge, digital_wallet, bank_transfer
    priority: int  # 1=highest, 5=lowest
    metadata: Dict

class SmartContract:
    """OpenSPP-style smart contract for disaster response"""
    
    def __init__(self, contract_id: str = None):
        self.contract_id = contract_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.status = ContractStatus.PENDING
        self.conditions: List[ContractCondition] = []
        self.payment_instructions: List[PaymentInstruction] = []
        self.execution_history: List[Dict] = []
        self.trust_score = 1.0
        self.version = "1.0"
        
    def add_condition(self, condition: ContractCondition):
        """Add a condition to the contract"""
        self.conditions.append(condition)
        
    def add_payment_instruction(self, instruction: PaymentInstruction):
        """Add a payment instruction to the contract"""
        self.payment_instructions.append(instruction)
        
    def evaluate_conditions(self, context: Dict) -> bool:
        """Evaluate if all conditions are met"""
        for condition in self.conditions:
            if not self._evaluate_single_condition(condition, context):
                return False
        return True
    
    def _evaluate_single_condition(self, condition: ContractCondition, context: Dict) -> bool:
        """Evaluate a single condition"""
        if condition.condition_type == "risk_threshold":
            risk_score = context.get('risk_score', 0)
            threshold = condition.parameters.get('threshold', 0.7)
            risk_type = condition.parameters.get('risk_type')
            
            # Check if risk score exceeds threshold
            if risk_score >= threshold:
                # If specific risk type is required, check it
                if risk_type and context.get('risk_type') != risk_type:
                    return False
                return True
            return False
            
        elif condition.condition_type == "time_based":
            current_time = datetime.utcnow()
            start_time = condition.parameters.get('start_time')
            end_time = condition.parameters.get('end_time')
            
            if start_time and current_time < start_time:
                return False
            if end_time and current_time > end_time:
                return False
            return True
            
        elif condition.condition_type == "manual_trigger":
            return context.get('manual_trigger', False)
            
        elif condition.condition_type == "geofence":
            location = context.get('location')
            if not location:
                return False
                
            center = condition.parameters.get('center')
            radius = condition.parameters.get('radius', 1000)
            
            if center and location:
                distance = self._calculate_distance(
                    location['lat'], location['lon'],
                    center['lat'], center['lon']
                )
                return distance <= radius
            return False
            
        return False
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters"""
        import math
        
        R = 6371000  # Earth's radius in meters
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def execute(self, context: Dict) -> Dict:
        """Execute the smart contract"""
        execution_id = str(uuid.uuid4())
        execution_time = datetime.utcnow()
        
        try:
            # Check if conditions are met
            if not self.evaluate_conditions(context):
                return {
                    'execution_id': execution_id,
                    'status': 'failed',
                    'reason': 'Conditions not met',
                    'timestamp': execution_time.isoformat()
                }
            
            # Update contract status
            self.status = ContractStatus.TRIGGERED
            
            # Execute payment instructions
            payment_results = []
            for instruction in self.payment_instructions:
                payment_result = self._execute_payment(instruction, context)
                payment_results.append(payment_result)
            
            # Update status based on payment results
            if all(result['status'] == 'completed' for result in payment_results):
                self.status = ContractStatus.EXECUTED
            else:
                self.status = ContractStatus.FAILED
            
            # Record execution
            execution_record = {
                'execution_id': execution_id,
                'timestamp': execution_time.isoformat(),
                'context': context,
                'payment_results': payment_results,
                'status': self.status.value
            }
            
            self.execution_history.append(execution_record)
            
            return {
                'execution_id': execution_id,
                'status': 'success',
                'contract_status': self.status.value,
                'payments_executed': len(payment_results),
                'total_amount': sum(r.get('amount', 0) for r in payment_results),
                'timestamp': execution_time.isoformat(),
                'payment_results': payment_results
            }
            
        except Exception as e:
            self.status = ContractStatus.FAILED
            error_record = {
                'execution_id': execution_id,
                'timestamp': execution_time.isoformat(),
                'error': str(e),
                'status': 'error'
            }
            self.execution_history.append(error_record)
            
            return {
                'execution_id': execution_id,
                'status': 'error',
                'error': str(e),
                'timestamp': execution_time.isoformat()
            }
    
    def _execute_payment(self, instruction: PaymentInstruction, context: Dict) -> Dict:
        """Execute a payment instruction"""
        payment_id = str(uuid.uuid4())
        
        # Simulate payment processing based on method
        if instruction.payment_method == "aadhaar_bridge":
            return self._process_aadhaar_payment(instruction, payment_id)
        elif instruction.payment_method == "digital_wallet":
            return self._process_digital_wallet_payment(instruction, payment_id)
        elif instruction.payment_method == "bank_transfer":
            return self._process_bank_transfer(instruction, payment_id)
        else:
            return {
                'payment_id': payment_id,
                'status': 'failed',
                'reason': f'Unsupported payment method: {instruction.payment_method}'
            }
    
    def _process_aadhaar_payment(self, instruction: PaymentInstruction, payment_id: str) -> Dict:
        """Simulate Aadhaar Payment Bridge processing"""
        # Simulate API call to Aadhaar Payment Bridge
        import random
        
        # Simulate processing time and success rate
        processing_time = random.uniform(1, 5)  # 1-5 seconds
        success_rate = 0.95  # 95% success rate
        
        if random.random() < success_rate:
            return {
                'payment_id': payment_id,
                'status': 'completed',
                'method': 'aadhaar_bridge',
                'beneficiary_id': instruction.beneficiary_id,
                'amount': instruction.amount,
                'currency': instruction.currency,
                'transaction_id': f"AADHAAR_{uuid.uuid4().hex[:8].upper()}",
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'payment_id': payment_id,
                'status': 'failed',
                'method': 'aadhaar_bridge',
                'beneficiary_id': instruction.beneficiary_id,
                'reason': 'Aadhaar verification failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _process_digital_wallet_payment(self, instruction: PaymentInstruction, payment_id: str) -> Dict:
        """Simulate digital wallet payment processing"""
        import random
        
        success_rate = 0.92  # 92% success rate
        processing_time = random.uniform(0.5, 2)  # 0.5-2 seconds
        
        if random.random() < success_rate:
            return {
                'payment_id': payment_id,
                'status': 'completed',
                'method': 'digital_wallet',
                'beneficiary_id': instruction.beneficiary_id,
                'amount': instruction.amount,
                'currency': instruction.currency,
                'transaction_id': f"WALLET_{uuid.uuid4().hex[:8].upper()}",
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'payment_id': payment_id,
                'status': 'failed',
                'method': 'digital_wallet',
                'beneficiary_id': instruction.beneficiary_id,
                'reason': 'Insufficient wallet balance',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _process_bank_transfer(self, instruction: PaymentInstruction, payment_id: str) -> Dict:
        """Simulate bank transfer processing"""
        import random
        
        success_rate = 0.98  # 98% success rate
        processing_time = random.uniform(2, 10)  # 2-10 seconds
        
        if random.random() < success_rate:
            return {
                'payment_id': payment_id,
                'status': 'completed',
                'method': 'bank_transfer',
                'beneficiary_id': instruction.beneficiary_id,
                'amount': instruction.amount,
                'currency': instruction.currency,
                'transaction_id': f"BANK_{uuid.uuid4().hex[:8].upper()}",
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'payment_id': payment_id,
                'status': 'failed',
                'method': 'bank_transfer',
                'beneficiary_id': instruction.beneficiary_id,
                'reason': 'Bank account not found',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def to_dict(self) -> Dict:
        """Convert contract to dictionary"""
        return {
            'contract_id': self.contract_id,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'conditions': [
                {
                    'condition_type': c.condition_type,
                    'parameters': c.parameters,
                    'description': c.description
                } for c in self.conditions
            ],
            'payment_instructions': [
                {
                    'beneficiary_id': p.beneficiary_id,
                    'amount': p.amount,
                    'currency': p.currency,
                    'payment_method': p.payment_method,
                    'priority': p.priority,
                    'metadata': p.metadata
                } for p in self.payment_instructions
            ],
            'execution_history': self.execution_history,
            'trust_score': self.trust_score,
            'version': self.version
        }

class OpenG2PIntegration:
    """Integration with OpenG2P (Government-to-Person) payment system"""
    
    def __init__(self):
        self.api_endpoint = "https://api.openg2p.org/v1"  # Mock endpoint
        self.api_key = "mock_api_key"
        
    def create_payment_program(self, program_name: str, budget: float, criteria: Dict) -> Dict:
        """Create a new payment program"""
        program_id = str(uuid.uuid4())
        
        return {
            'program_id': program_id,
            'name': program_name,
            'budget': budget,
            'criteria': criteria,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
    
    def enroll_beneficiary(self, program_id: str, beneficiary_id: str, eligibility_data: Dict) -> Dict:
        """Enroll a beneficiary in a payment program"""
        enrollment_id = str(uuid.uuid4())
        
        # Simulate eligibility check
        import random
        eligible = random.random() > 0.1  # 90% eligibility rate
        
        return {
            'enrollment_id': enrollment_id,
            'program_id': program_id,
            'beneficiary_id': beneficiary_id,
            'eligible': eligible,
            'eligibility_score': random.uniform(0.7, 1.0) if eligible else random.uniform(0, 0.5),
            'enrolled_at': datetime.utcnow().isoformat()
        }
    
    def process_bulk_payment(self, program_id: str, payment_list: List[Dict]) -> Dict:
        """Process bulk payments for a program"""
        batch_id = str(uuid.uuid4())
        
        # Simulate bulk payment processing
        processed_payments = []
        total_amount = 0
        
        for payment in payment_list:
            import random
            success = random.random() > 0.05  # 95% success rate
            
            if success:
                processed_payments.append({
                    'beneficiary_id': payment['beneficiary_id'],
                    'amount': payment['amount'],
                    'status': 'completed',
                    'transaction_id': f"G2P_{uuid.uuid4().hex[:8].upper()}"
                })
                total_amount += payment['amount']
            else:
                processed_payments.append({
                    'beneficiary_id': payment['beneficiary_id'],
                    'amount': payment['amount'],
                    'status': 'failed',
                    'reason': 'Account verification failed'
                })
        
        return {
            'batch_id': batch_id,
            'program_id': program_id,
            'total_payments': len(payment_list),
            'successful_payments': len([p for p in processed_payments if p['status'] == 'completed']),
            'total_amount': total_amount,
            'processed_at': datetime.utcnow().isoformat(),
            'payments': processed_payments
        }

class TrustLayer:
    """OpenSPP-style trust layer for contract verification"""
    
    def __init__(self):
        self.trust_threshold = 0.7
        self.verification_nodes = ['node1', 'node2', 'node3', 'node4', 'node5']
        
    def verify_contract(self, contract: SmartContract) -> Dict:
        """Verify contract integrity and trustworthiness"""
        verification_id = str(uuid.uuid4())
        
        # Simulate multi-node verification
        verifications = []
        for node in self.verification_nodes:
            verification = self._node_verification(contract, node)
            verifications.append(verification)
        
        # Calculate consensus
        trust_scores = [v['trust_score'] for v in verifications]
        consensus_score = sum(trust_scores) / len(trust_scores)
        
        # Determine verification result
        verified = consensus_score >= self.trust_threshold
        
        return {
            'verification_id': verification_id,
            'contract_id': contract.contract_id,
            'verified': verified,
            'consensus_score': consensus_score,
            'trust_threshold': self.trust_threshold,
            'node_verifications': verifications,
            'verified_at': datetime.utcnow().isoformat()
        }
    
    def _node_verification(self, contract: SmartContract, node_id: str) -> Dict:
        """Simulate verification by a single node"""
        import random
        
        # Simulate various verification checks
        checks = {
            'syntax_valid': random.random() > 0.05,  # 95% pass rate
            'conditions_valid': random.random() > 0.1,  # 90% pass rate
            'payments_valid': random.random() > 0.08,  # 92% pass rate
            'security_check': random.random() > 0.02,  # 98% pass rate
        }
        
        # Calculate trust score based on checks
        passed_checks = sum(checks.values())
        trust_score = passed_checks / len(checks)
        
        return {
            'node_id': node_id,
            'checks': checks,
            'trust_score': trust_score,
            'verified_at': datetime.utcnow().isoformat()
        }
    
    def create_contract_hash(self, contract: SmartContract) -> str:
        """Create a hash of the contract for integrity verification"""
        contract_data = json.dumps(contract.to_dict(), sort_keys=True)
        return hashlib.sha256(contract_data.encode()).hexdigest()

# Global instances
openg2p = OpenG2PIntegration()
trust_layer = TrustLayer()

