from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import json
import uuid
from src.models.user import db
from src.models.sensor import BeneficiaryHousehold, RiskAssessment
from src.models.smart_contract import (
    SmartContract, ContractCondition, PaymentInstruction,
    ContractStatus, PaymentStatus, openg2p, trust_layer
)

contracts_bp = Blueprint('contracts', __name__)

# In-memory storage for contracts (in production, use database)
active_contracts = {}
payment_history = []

@contracts_bp.route('/contracts/create', methods=['POST'])
def create_smart_contract():
    """Create a new smart contract"""
    try:
        data = request.get_json()
        
        # Create new contract
        contract = SmartContract()
        
        # Add conditions
        conditions_data = data.get('conditions', [])
        for condition_data in conditions_data:
            condition = ContractCondition(
                condition_type=condition_data['condition_type'],
                parameters=condition_data['parameters'],
                description=condition_data['description']
            )
            contract.add_condition(condition)
        
        # Add payment instructions
        payments_data = data.get('payment_instructions', [])
        for payment_data in payments_data:
            instruction = PaymentInstruction(
                beneficiary_id=payment_data['beneficiary_id'],
                amount=payment_data['amount'],
                currency=payment_data.get('currency', 'USD'),
                payment_method=payment_data['payment_method'],
                priority=payment_data.get('priority', 3),
                metadata=payment_data.get('metadata', {})
            )
            contract.add_payment_instruction(instruction)
        
        # Verify contract through trust layer
        verification_result = trust_layer.verify_contract(contract)
        
        if verification_result['verified']:
            contract.status = ContractStatus.ACTIVE
            active_contracts[contract.contract_id] = contract
            
            return jsonify({
                'status': 'success',
                'contract_id': contract.contract_id,
                'verification': verification_result,
                'contract': contract.to_dict()
            }), 201
        else:
            return jsonify({
                'status': 'failed',
                'reason': 'Contract verification failed',
                'verification': verification_result
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts/<contract_id>/execute', methods=['POST'])
def execute_contract(contract_id):
    """Execute a smart contract"""
    try:
        if contract_id not in active_contracts:
            return jsonify({'error': 'Contract not found'}), 404
        
        contract = active_contracts[contract_id]
        data = request.get_json()
        
        # Execute contract with provided context
        execution_result = contract.execute(data)
        
        # Store payment history
        if 'payment_results' in execution_result:
            for payment in execution_result['payment_results']:
                payment_history.append({
                    'contract_id': contract_id,
                    'payment': payment,
                    'executed_at': datetime.utcnow().isoformat()
                })
        
        return jsonify({
            'status': 'success',
            'execution_result': execution_result,
            'contract_status': contract.status.value
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts/auto-trigger', methods=['POST'])
def auto_trigger_contracts():
    """Automatically trigger contracts based on risk assessments"""
    try:
        data = request.get_json()
        risk_assessment_id = data.get('risk_assessment_id')
        
        if not risk_assessment_id:
            return jsonify({'error': 'risk_assessment_id required'}), 400
        
        # Get risk assessment
        risk_assessment = RiskAssessment.query.get(risk_assessment_id)
        if not risk_assessment:
            return jsonify({'error': 'Risk assessment not found'}), 404
        
        # Find contracts that should be triggered
        triggered_contracts = []
        
        for contract_id, contract in active_contracts.items():
            if contract.status != ContractStatus.ACTIVE:
                continue
            
            # Prepare context for contract evaluation
            context = {
                'risk_score': risk_assessment.risk_score,
                'risk_type': risk_assessment.risk_type,
                'location': {
                    'lat': risk_assessment.location_lat,
                    'lon': risk_assessment.location_lon
                },
                'confidence': risk_assessment.confidence,
                'timestamp': risk_assessment.timestamp.isoformat()
            }
            
            # Check if contract conditions are met
            if contract.evaluate_conditions(context):
                execution_result = contract.execute(context)
                triggered_contracts.append({
                    'contract_id': contract_id,
                    'execution_result': execution_result
                })
                
                # Store payment history
                if 'payment_results' in execution_result:
                    for payment in execution_result['payment_results']:
                        payment_history.append({
                            'contract_id': contract_id,
                            'payment': payment,
                            'executed_at': datetime.utcnow().isoformat(),
                            'trigger_type': 'auto',
                            'risk_assessment_id': risk_assessment_id
                        })
        
        return jsonify({
            'status': 'success',
            'risk_assessment': risk_assessment.to_dict(),
            'triggered_contracts': len(triggered_contracts),
            'contracts': triggered_contracts,
            'total_payments': sum(
                len(c['execution_result'].get('payment_results', []))
                for c in triggered_contracts
            )
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts', methods=['GET'])
def list_contracts():
    """List all contracts"""
    try:
        status_filter = request.args.get('status')
        
        contracts_list = []
        for contract_id, contract in active_contracts.items():
            if status_filter and contract.status.value != status_filter:
                continue
            
            contracts_list.append(contract.to_dict())
        
        return jsonify({
            'status': 'success',
            'count': len(contracts_list),
            'contracts': contracts_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get a specific contract"""
    try:
        if contract_id not in active_contracts:
            return jsonify({'error': 'Contract not found'}), 404
        
        contract = active_contracts[contract_id]
        
        return jsonify({
            'status': 'success',
            'contract': contract.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/payments/aadhaar-bridge', methods=['POST'])
def aadhaar_payment_bridge():
    """Simulate Aadhaar Payment Bridge API"""
    try:
        data = request.get_json()
        
        required_fields = ['beneficiary_aadhaar', 'amount', 'purpose']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Simulate Aadhaar verification and payment
        import random
        
        transaction_id = f"AADHAAR_{uuid.uuid4().hex[:8].upper()}"
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            return jsonify({
                'status': 'success',
                'transaction_id': transaction_id,
                'beneficiary_aadhaar': data['beneficiary_aadhaar'][:4] + 'XXXX',  # Masked
                'amount': data['amount'],
                'currency': data.get('currency', 'INR'),
                'purpose': data['purpose'],
                'processed_at': datetime.utcnow().isoformat(),
                'bank_reference': f"BANK_{uuid.uuid4().hex[:6].upper()}"
            })
        else:
            return jsonify({
                'status': 'failed',
                'error_code': 'AADHAAR_VERIFICATION_FAILED',
                'message': 'Aadhaar verification failed',
                'transaction_id': transaction_id
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/payments/openg2p/program', methods=['POST'])
def create_payment_program():
    """Create OpenG2P payment program"""
    try:
        data = request.get_json()
        
        required_fields = ['program_name', 'budget']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        program = openg2p.create_payment_program(
            program_name=data['program_name'],
            budget=data['budget'],
            criteria=data.get('criteria', {})
        )
        
        return jsonify({
            'status': 'success',
            'program': program
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/payments/openg2p/enroll', methods=['POST'])
def enroll_beneficiary():
    """Enroll beneficiary in OpenG2P program"""
    try:
        data = request.get_json()
        
        required_fields = ['program_id', 'beneficiary_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        enrollment = openg2p.enroll_beneficiary(
            program_id=data['program_id'],
            beneficiary_id=data['beneficiary_id'],
            eligibility_data=data.get('eligibility_data', {})
        )
        
        return jsonify({
            'status': 'success',
            'enrollment': enrollment
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/payments/openg2p/bulk-payment', methods=['POST'])
def process_bulk_payment():
    """Process bulk payments through OpenG2P"""
    try:
        data = request.get_json()
        
        required_fields = ['program_id', 'payments']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result = openg2p.process_bulk_payment(
            program_id=data['program_id'],
            payment_list=data['payments']
        )
        
        return jsonify({
            'status': 'success',
            'bulk_payment': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/payments/history', methods=['GET'])
def get_payment_history():
    """Get payment history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        contract_id = request.args.get('contract_id')
        
        filtered_history = payment_history
        
        if contract_id:
            filtered_history = [p for p in payment_history if p['contract_id'] == contract_id]
        
        # Sort by execution time (most recent first)
        filtered_history.sort(key=lambda x: x['executed_at'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'count': len(filtered_history[:limit]),
            'total_count': len(filtered_history),
            'payments': filtered_history[:limit]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts/templates', methods=['GET'])
def get_contract_templates():
    """Get predefined contract templates"""
    try:
        templates = {
            'disaster_response': {
                'name': 'Disaster Response Contract',
                'description': 'Automatic payment trigger for disaster-affected beneficiaries',
                'conditions': [
                    {
                        'condition_type': 'risk_threshold',
                        'parameters': {
                            'threshold': 0.7,
                            'risk_type': None  # Any risk type
                        },
                        'description': 'Trigger when risk score exceeds 0.7'
                    }
                ],
                'payment_instructions': [
                    {
                        'amount': 1000,
                        'currency': 'USD',
                        'payment_method': 'aadhaar_bridge',
                        'priority': 1,
                        'metadata': {
                            'purpose': 'Emergency disaster relief',
                            'category': 'immediate_assistance'
                        }
                    }
                ]
            },
            'flood_specific': {
                'name': 'Flood Response Contract',
                'description': 'Specific contract for flood disasters',
                'conditions': [
                    {
                        'condition_type': 'risk_threshold',
                        'parameters': {
                            'threshold': 0.6,
                            'risk_type': 'flood'
                        },
                        'description': 'Trigger when flood risk exceeds 0.6'
                    }
                ],
                'payment_instructions': [
                    {
                        'amount': 1500,
                        'currency': 'USD',
                        'payment_method': 'digital_wallet',
                        'priority': 1,
                        'metadata': {
                            'purpose': 'Flood relief and evacuation',
                            'category': 'flood_assistance'
                        }
                    }
                ]
            },
            'earthquake_response': {
                'name': 'Earthquake Response Contract',
                'description': 'Emergency response for earthquake events',
                'conditions': [
                    {
                        'condition_type': 'risk_threshold',
                        'parameters': {
                            'threshold': 0.8,
                            'risk_type': 'earthquake'
                        },
                        'description': 'Trigger when earthquake risk exceeds 0.8'
                    }
                ],
                'payment_instructions': [
                    {
                        'amount': 2000,
                        'currency': 'USD',
                        'payment_method': 'bank_transfer',
                        'priority': 1,
                        'metadata': {
                            'purpose': 'Earthquake emergency relief',
                            'category': 'structural_damage_assistance'
                        }
                    }
                ]
            }
        }
        
        return jsonify({
            'status': 'success',
            'templates': templates
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/contracts/create-from-template', methods=['POST'])
def create_contract_from_template():
    """Create contract from template"""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        beneficiaries = data.get('beneficiaries', [])
        
        if not template_name:
            return jsonify({'error': 'template_name required'}), 400
        
        # Get templates
        templates_response = get_contract_templates()
        templates = templates_response[0].get_json()['templates']
        
        if template_name not in templates:
            return jsonify({'error': 'Template not found'}), 404
        
        template = templates[template_name]
        
        # Create contract from template
        contract_data = {
            'conditions': template['conditions'],
            'payment_instructions': []
        }
        
        # Create payment instructions for each beneficiary
        for beneficiary_id in beneficiaries:
            for payment_template in template['payment_instructions']:
                payment_instruction = payment_template.copy()
                payment_instruction['beneficiary_id'] = beneficiary_id
                contract_data['payment_instructions'].append(payment_instruction)
        
        # Create the contract
        return create_smart_contract_internal(contract_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_smart_contract_internal(data):
    """Internal function to create smart contract"""
    # Create new contract
    contract = SmartContract()
    
    # Add conditions
    conditions_data = data.get('conditions', [])
    for condition_data in conditions_data:
        condition = ContractCondition(
            condition_type=condition_data['condition_type'],
            parameters=condition_data['parameters'],
            description=condition_data['description']
        )
        contract.add_condition(condition)
    
    # Add payment instructions
    payments_data = data.get('payment_instructions', [])
    for payment_data in payments_data:
        instruction = PaymentInstruction(
            beneficiary_id=payment_data['beneficiary_id'],
            amount=payment_data['amount'],
            currency=payment_data.get('currency', 'USD'),
            payment_method=payment_data['payment_method'],
            priority=payment_data.get('priority', 3),
            metadata=payment_data.get('metadata', {})
        )
        contract.add_payment_instruction(instruction)
    
    # Verify contract through trust layer
    verification_result = trust_layer.verify_contract(contract)
    
    if verification_result['verified']:
        contract.status = ContractStatus.ACTIVE
        active_contracts[contract.contract_id] = contract
        
        return jsonify({
            'status': 'success',
            'contract_id': contract.contract_id,
            'verification': verification_result,
            'contract': contract.to_dict()
        }), 201
    else:
        return jsonify({
            'status': 'failed',
            'reason': 'Contract verification failed',
            'verification': verification_result
        }), 400

