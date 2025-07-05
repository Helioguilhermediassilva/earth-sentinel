from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import json
import uuid
from src.models.user import db
from src.models.dispatch_system import (
    discovery_service, fulfillment_service,
    ResourceType, ResourceStatus, DispatchStatus,
    Location, Resource, DispatchRequest
)

dispatch_bp = Blueprint('dispatch', __name__)

@dispatch_bp.route('/dispatch/resources/discover', methods=['POST'])
def discover_resources():
    """Discover available resources for emergency response"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['location', 'resource_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create temporary dispatch request for discovery
        temp_request = DispatchRequest(
            request_id="temp",
            requester_id=data.get('requester_id', 'system'),
            location=Location(
                lat=data['location']['lat'],
                lon=data['location']['lon'],
                address=data['location'].get('address')
            ),
            resource_type=ResourceType(data['resource_type']),
            priority=data.get('priority', 3),
            requirements=data.get('requirements', {}),
            description=data.get('description', 'Resource discovery'),
            created_at=datetime.utcnow()
        )
        
        # Discover resources
        max_distance = data.get('max_distance_km', 50)
        available_resources = discovery_service.discover_resources(temp_request, max_distance)
        
        # Calculate distances and add to response
        resources_with_distance = []
        for resource in available_resources:
            distance = resource.location.distance_to(temp_request.location)
            resource_dict = resource.to_dict()
            resource_dict['distance_km'] = round(distance / 1000, 2)
            resource_dict['estimated_arrival_minutes'] = round(
                distance / (fulfillment_service._get_resource_speed(resource.resource_type) * 60), 1
            )
            resources_with_distance.append(resource_dict)
        
        return jsonify({
            'status': 'success',
            'search_criteria': {
                'location': data['location'],
                'resource_type': data['resource_type'],
                'max_distance_km': max_distance,
                'requirements': data.get('requirements', {})
            },
            'resources_found': len(resources_with_distance),
            'resources': resources_with_distance
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/request', methods=['POST'])
def create_dispatch_request():
    """Create a new dispatch request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['requester_id', 'location', 'resource_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create dispatch request
        request_obj = fulfillment_service.create_dispatch_request(data)
        
        # Automatically try to assign a resource
        assignment = fulfillment_service.assign_resource(request_obj.request_id)
        
        response = {
            'status': 'success',
            'request': request_obj.to_dict()
        }
        
        if assignment:
            response['assignment'] = assignment.to_dict()
            response['message'] = 'Request created and resource assigned successfully'
        else:
            response['message'] = 'Request created but no resources available'
            response['assignment'] = None
        
        return jsonify(response), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/assign', methods=['POST'])
def assign_resource_to_request():
    """Manually assign a specific resource to a request"""
    try:
        data = request.get_json()
        
        required_fields = ['request_id', 'resource_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        assignment = fulfillment_service.assign_resource(
            data['request_id'], 
            data['resource_id']
        )
        
        if assignment:
            return jsonify({
                'status': 'success',
                'assignment': assignment.to_dict(),
                'message': 'Resource assigned successfully'
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Failed to assign resource (request not found, resource unavailable, or already assigned)'
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/assignment/<assignment_id>/status', methods=['GET'])
def get_assignment_status(assignment_id):
    """Get current status and location of an assignment"""
    try:
        # Update progress before returning status
        fulfillment_service.update_assignment_progress(assignment_id)
        
        status = fulfillment_service.get_assignment_status(assignment_id)
        
        if status:
            return jsonify({
                'status': 'success',
                'assignment_status': status
            })
        else:
            return jsonify({'error': 'Assignment not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/assignment/<assignment_id>/track', methods=['GET'])
def track_assignment(assignment_id):
    """Get real-time tracking information for an assignment"""
    try:
        # Update progress
        assignment = fulfillment_service.update_assignment_progress(assignment_id)
        
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404
        
        # Get resource info
        resource = discovery_service.resources[assignment.resource_id]
        request_obj = fulfillment_service.active_requests[assignment.request_id]
        
        # Calculate progress percentage
        progress_percentage = 0
        if assignment.status == DispatchStatus.DISPATCHED and assignment.estimated_arrival:
            elapsed = (datetime.utcnow() - assignment.assigned_at).total_seconds()
            total_time = (assignment.estimated_arrival - assignment.assigned_at).total_seconds()
            progress_percentage = min(100, int((elapsed / total_time) * 100))
        elif assignment.status in [DispatchStatus.IN_PROGRESS, DispatchStatus.COMPLETED]:
            progress_percentage = 100
        
        return jsonify({
            'status': 'success',
            'tracking_info': {
                'assignment_id': assignment_id,
                'resource_name': resource.name,
                'resource_type': resource.resource_type.value,
                'current_status': assignment.status.value,
                'progress_percentage': progress_percentage,
                'current_location': {
                    'lat': assignment.current_location.lat,
                    'lon': assignment.current_location.lon,
                    'address': assignment.current_location.address
                } if assignment.current_location else None,
                'destination': {
                    'lat': request_obj.location.lat,
                    'lon': request_obj.location.lon,
                    'address': request_obj.location.address
                },
                'route': [
                    {'lat': loc.lat, 'lon': loc.lon, 'address': loc.address}
                    for loc in assignment.route
                ],
                'estimated_arrival': assignment.estimated_arrival.isoformat() if assignment.estimated_arrival else None,
                'actual_arrival': assignment.actual_arrival.isoformat() if assignment.actual_arrival else None,
                'recent_updates': assignment.progress_updates[-5:],  # Last 5 updates
                'contact_info': resource.contact_info
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/assignment/<assignment_id>/cancel', methods=['POST'])
def cancel_assignment(assignment_id):
    """Cancel an assignment"""
    try:
        success = fulfillment_service.cancel_assignment(assignment_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Assignment cancelled successfully'
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Assignment not found or cannot be cancelled'
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/resources', methods=['GET'])
def list_resources():
    """List all available resources"""
    try:
        resource_type = request.args.get('type')
        status = request.args.get('status')
        
        resources = []
        for resource in discovery_service.resources.values():
            # Apply filters
            if resource_type and resource.resource_type.value != resource_type:
                continue
            if status and resource.status.value != status:
                continue
            
            resources.append(resource.to_dict())
        
        return jsonify({
            'status': 'success',
            'count': len(resources),
            'resources': resources
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/resources/<resource_id>', methods=['GET'])
def get_resource_details(resource_id):
    """Get detailed information about a specific resource"""
    try:
        if resource_id not in discovery_service.resources:
            return jsonify({'error': 'Resource not found'}), 404
        
        resource = discovery_service.resources[resource_id]
        
        # Find current assignment if any
        current_assignment = None
        for assignment in fulfillment_service.assignments.values():
            if (assignment.resource_id == resource_id and 
                assignment.status not in [DispatchStatus.COMPLETED, DispatchStatus.CANCELLED]):
                current_assignment = assignment.to_dict()
                break
        
        return jsonify({
            'status': 'success',
            'resource': resource.to_dict(),
            'current_assignment': current_assignment
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/resources/register', methods=['POST'])
def register_resource():
    """Register a new resource in the system"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'resource_type', 'location', 'capabilities', 'operator']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new resource
        resource = Resource(
            resource_id=data.get('resource_id', str(uuid.uuid4())),
            resource_type=ResourceType(data['resource_type']),
            name=data['name'],
            location=Location(
                lat=data['location']['lat'],
                lon=data['location']['lon'],
                address=data['location'].get('address')
            ),
            capabilities=data['capabilities'],
            capacity=data.get('capacity', {}),
            status=ResourceStatus(data.get('status', 'available')),
            operator=data['operator'],
            contact_info=data.get('contact_info', {}),
            metadata=data.get('metadata', {})
        )
        
        # Register resource
        success = discovery_service.register_resource(resource)
        
        if success:
            return jsonify({
                'status': 'success',
                'resource': resource.to_dict(),
                'message': 'Resource registered successfully'
            }), 201
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Failed to register resource'
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/resources/<resource_id>/status', methods=['PUT'])
def update_resource_status(resource_id):
    """Update resource status and location"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Missing required field: status'}), 400
        
        status = ResourceStatus(data['status'])
        location = None
        
        if 'location' in data:
            location = Location(
                lat=data['location']['lat'],
                lon=data['location']['lon'],
                address=data['location'].get('address')
            )
        
        success = discovery_service.update_resource_status(resource_id, status, location)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Resource status updated successfully'
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Resource not found'
            }), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/assignments', methods=['GET'])
def list_assignments():
    """List all assignments"""
    try:
        status_filter = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        assignments = []
        for assignment in fulfillment_service.assignments.values():
            if status_filter and assignment.status.value != status_filter:
                continue
            
            # Update progress before adding to list
            fulfillment_service.update_assignment_progress(assignment.assignment_id)
            assignments.append(assignment.to_dict())
        
        # Sort by assigned time (most recent first)
        assignments.sort(key=lambda x: x['assigned_at'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'count': len(assignments[:limit]),
            'total_count': len(assignments),
            'assignments': assignments[:limit]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/dashboard', methods=['GET'])
def get_dispatch_dashboard():
    """Get dashboard overview of dispatch system"""
    try:
        # Count resources by type and status
        resource_stats = {}
        for resource in discovery_service.resources.values():
            res_type = resource.resource_type.value
            if res_type not in resource_stats:
                resource_stats[res_type] = {'total': 0, 'available': 0, 'dispatched': 0, 'maintenance': 0}
            
            resource_stats[res_type]['total'] += 1
            if resource.status == ResourceStatus.AVAILABLE:
                resource_stats[res_type]['available'] += 1
            elif resource.status in [ResourceStatus.DISPATCHED, ResourceStatus.EN_ROUTE]:
                resource_stats[res_type]['dispatched'] += 1
            elif resource.status == ResourceStatus.MAINTENANCE:
                resource_stats[res_type]['maintenance'] += 1
        
        # Count assignments by status
        assignment_stats = {}
        for assignment in fulfillment_service.assignments.values():
            status = assignment.status.value
            assignment_stats[status] = assignment_stats.get(status, 0) + 1
        
        # Get recent activity
        recent_assignments = []
        for assignment in list(fulfillment_service.assignments.values())[-10:]:
            fulfillment_service.update_assignment_progress(assignment.assignment_id)
            recent_assignments.append({
                'assignment_id': assignment.assignment_id,
                'resource_id': assignment.resource_id,
                'status': assignment.status.value,
                'assigned_at': assignment.assigned_at.isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'dashboard': {
                'resource_statistics': resource_stats,
                'assignment_statistics': assignment_stats,
                'total_resources': len(discovery_service.resources),
                'active_assignments': len([a for a in fulfillment_service.assignments.values() 
                                         if a.status not in [DispatchStatus.COMPLETED, DispatchStatus.CANCELLED]]),
                'recent_assignments': recent_assignments,
                'system_status': 'operational',
                'last_updated': datetime.utcnow().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dispatch_bp.route('/dispatch/simulate-emergency', methods=['POST'])
def simulate_emergency_dispatch():
    """Simulate an emergency scenario with automatic dispatch"""
    try:
        data = request.get_json()
        
        # Default emergency location if not provided
        emergency_location = data.get('location', {
            'lat': -23.5505,
            'lon': -46.6333,
            'address': 'São Paulo Emergency Zone'
        })
        
        emergency_type = data.get('emergency_type', 'general')
        
        # Define emergency scenarios
        scenarios = {
            'fire': {
                'resource_types': ['drone', 'emergency_team'],
                'requirements': {'capabilities': ['aerial_surveillance', 'search_rescue']},
                'description': 'Fire emergency - aerial surveillance and rescue team needed'
            },
            'flood': {
                'resource_types': ['autonomous_vehicle', 'emergency_team'],
                'requirements': {'capabilities': ['evacuation', 'passenger_transport']},
                'description': 'Flood emergency - evacuation vehicles and rescue team needed'
            },
            'earthquake': {
                'resource_types': ['emergency_team', 'medical_unit'],
                'requirements': {'capabilities': ['search_rescue', 'medical_aid']},
                'description': 'Earthquake emergency - search and rescue with medical support'
            },
            'general': {
                'resource_types': ['drone', 'emergency_team'],
                'requirements': {'capabilities': ['search_rescue']},
                'description': 'General emergency - assessment and rescue needed'
            }
        }
        
        scenario = scenarios.get(emergency_type, scenarios['general'])
        dispatched_resources = []
        
        # Create dispatch requests for each resource type needed
        for resource_type_str in scenario['resource_types']:
            request_data = {
                'requester_id': 'emergency_system',
                'location': emergency_location,
                'resource_type': resource_type_str,
                'priority': 1,  # Highest priority
                'requirements': scenario['requirements'],
                'description': scenario['description']
            }
            
            # Create request
            request_obj = fulfillment_service.create_dispatch_request(request_data)
            
            # Try to assign resource
            assignment = fulfillment_service.assign_resource(request_obj.request_id)
            
            if assignment:
                dispatched_resources.append({
                    'request': request_obj.to_dict(),
                    'assignment': assignment.to_dict()
                })
        
        return jsonify({
            'status': 'success',
            'emergency_simulation': {
                'emergency_type': emergency_type,
                'location': emergency_location,
                'scenario': scenario,
                'resources_dispatched': len(dispatched_resources),
                'dispatched_resources': dispatched_resources
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

