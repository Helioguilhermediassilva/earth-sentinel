from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import random
import math

class ResourceType(Enum):
    DRONE = "drone"
    AUTONOMOUS_VEHICLE = "autonomous_vehicle"
    EMERGENCY_TEAM = "emergency_team"
    SUPPLY_DELIVERY = "supply_delivery"
    MEDICAL_UNIT = "medical_unit"

class ResourceStatus(Enum):
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class DispatchStatus(Enum):
    PENDING = "pending"
    SEARCHING = "searching"
    ASSIGNED = "assigned"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Location:
    lat: float
    lon: float
    address: Optional[str] = None
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance to another location in meters"""
        R = 6371000  # Earth's radius in meters
        lat1_rad = math.radians(self.lat)
        lat2_rad = math.radians(other.lat)
        delta_lat = math.radians(other.lat - self.lat)
        delta_lon = math.radians(other.lon - self.lon)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

@dataclass
class Resource:
    """Represents an emergency response resource"""
    resource_id: str
    resource_type: ResourceType
    name: str
    location: Location
    capabilities: List[str]
    capacity: Dict[str, int]  # e.g., {"passengers": 4, "cargo_kg": 100}
    status: ResourceStatus
    operator: str
    contact_info: Dict[str, str]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type.value,
            'name': self.name,
            'location': {
                'lat': self.location.lat,
                'lon': self.location.lon,
                'address': self.location.address
            },
            'capabilities': self.capabilities,
            'capacity': self.capacity,
            'status': self.status.value,
            'operator': self.operator,
            'contact_info': self.contact_info,
            'metadata': self.metadata
        }

@dataclass
class DispatchRequest:
    """Request for emergency resource dispatch"""
    request_id: str
    requester_id: str
    location: Location
    resource_type: ResourceType
    priority: int  # 1=highest, 5=lowest
    requirements: Dict[str, any]
    description: str
    created_at: datetime
    deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'request_id': self.request_id,
            'requester_id': self.requester_id,
            'location': {
                'lat': self.location.lat,
                'lon': self.location.lon,
                'address': self.location.address
            },
            'resource_type': self.resource_type.value,
            'priority': self.priority,
            'requirements': self.requirements,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None
        }

@dataclass
class DispatchAssignment:
    """Assignment of resource to a dispatch request"""
    assignment_id: str
    request_id: str
    resource_id: str
    status: DispatchStatus
    assigned_at: datetime
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    route: List[Location] = None
    current_location: Optional[Location] = None
    progress_updates: List[Dict] = None
    
    def __post_init__(self):
        if self.route is None:
            self.route = []
        if self.progress_updates is None:
            self.progress_updates = []
    
    def to_dict(self) -> Dict:
        return {
            'assignment_id': self.assignment_id,
            'request_id': self.request_id,
            'resource_id': self.resource_id,
            'status': self.status.value,
            'assigned_at': self.assigned_at.isoformat(),
            'estimated_arrival': self.estimated_arrival.isoformat() if self.estimated_arrival else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'completion_time': self.completion_time.isoformat() if self.completion_time else None,
            'route': [{'lat': loc.lat, 'lon': loc.lon, 'address': loc.address} for loc in self.route],
            'current_location': {
                'lat': self.current_location.lat,
                'lon': self.current_location.lon,
                'address': self.current_location.address
            } if self.current_location else None,
            'progress_updates': self.progress_updates
        }

class BeckNDiscoveryService:
    """BeckN-style discovery service for emergency resources"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.service_providers: Dict[str, Dict] = {}
        self.initialize_mock_resources()
    
    def initialize_mock_resources(self):
        """Initialize mock emergency resources"""
        # Mock drones
        for i in range(5):
            drone_id = f"DRONE_{i+1:03d}"
            self.resources[drone_id] = Resource(
                resource_id=drone_id,
                resource_type=ResourceType.DRONE,
                name=f"Emergency Drone {i+1}",
                location=Location(
                    lat=random.uniform(-23.7, -23.4),
                    lon=random.uniform(-46.8, -46.4),
                    address=f"Drone Base {i+1}"
                ),
                capabilities=["aerial_surveillance", "supply_delivery", "search_rescue"],
                capacity={"cargo_kg": random.randint(5, 20), "flight_time_min": random.randint(30, 120)},
                status=random.choice([ResourceStatus.AVAILABLE, ResourceStatus.MAINTENANCE]),
                operator=f"Emergency Services Unit {i+1}",
                contact_info={"phone": f"+55-11-9999-{i+1:04d}", "radio": f"FREQ_{i+1}"},
                metadata={"battery_level": random.uniform(70, 100), "last_maintenance": "2025-07-01"}
            )
        
        # Mock autonomous vehicles
        for i in range(3):
            vehicle_id = f"AV_{i+1:03d}"
            self.resources[vehicle_id] = Resource(
                resource_id=vehicle_id,
                resource_type=ResourceType.AUTONOMOUS_VEHICLE,
                name=f"Autonomous Emergency Vehicle {i+1}",
                location=Location(
                    lat=random.uniform(-23.7, -23.4),
                    lon=random.uniform(-46.8, -46.4),
                    address=f"Vehicle Station {i+1}"
                ),
                capabilities=["passenger_transport", "supply_delivery", "evacuation"],
                capacity={"passengers": random.randint(4, 8), "cargo_kg": random.randint(200, 500)},
                status=random.choice([ResourceStatus.AVAILABLE, ResourceStatus.DISPATCHED]),
                operator=f"Autonomous Fleet {i+1}",
                contact_info={"control_center": f"+55-11-8888-{i+1:04d}", "vehicle_id": vehicle_id},
                metadata={"fuel_level": random.uniform(60, 100), "autonomous_level": "L4"}
            )
        
        # Mock emergency teams
        for i in range(4):
            team_id = f"TEAM_{i+1:03d}"
            self.resources[team_id] = Resource(
                resource_id=team_id,
                resource_type=ResourceType.EMERGENCY_TEAM,
                name=f"Emergency Response Team {i+1}",
                location=Location(
                    lat=random.uniform(-23.7, -23.4),
                    lon=random.uniform(-46.8, -46.4),
                    address=f"Emergency Station {i+1}"
                ),
                capabilities=["search_rescue", "medical_aid", "evacuation", "hazmat"],
                capacity={"team_members": random.randint(3, 6), "equipment_units": random.randint(10, 20)},
                status=random.choice([ResourceStatus.AVAILABLE, ResourceStatus.EN_ROUTE]),
                operator=f"Emergency Services Department {i+1}",
                contact_info={"team_leader": f"+55-11-7777-{i+1:04d}", "dispatch": f"+55-11-7700-{i+1:04d}"},
                metadata={"specialization": random.choice(["urban_rescue", "medical", "hazmat", "water_rescue"])}
            )
    
    def discover_resources(self, request: DispatchRequest, max_distance_km: float = 50) -> List[Resource]:
        """Discover available resources for a dispatch request"""
        available_resources = []
        
        for resource in self.resources.values():
            # Check if resource type matches
            if resource.resource_type != request.resource_type:
                continue
            
            # Check if resource is available
            if resource.status != ResourceStatus.AVAILABLE:
                continue
            
            # Check distance constraint
            distance = resource.location.distance_to(request.location)
            if distance > max_distance_km * 1000:  # Convert km to meters
                continue
            
            # Check if resource meets requirements
            if self._meets_requirements(resource, request.requirements):
                available_resources.append(resource)
        
        # Sort by distance and priority factors
        available_resources.sort(key=lambda r: (
            r.location.distance_to(request.location),
            -request.priority  # Higher priority first
        ))
        
        return available_resources
    
    def _meets_requirements(self, resource: Resource, requirements: Dict[str, any]) -> bool:
        """Check if resource meets the requirements"""
        for req_key, req_value in requirements.items():
            if req_key == "capabilities":
                required_caps = req_value if isinstance(req_value, list) else [req_value]
                if not any(cap in resource.capabilities for cap in required_caps):
                    return False
            
            elif req_key == "min_capacity":
                for capacity_type, min_value in req_value.items():
                    if capacity_type not in resource.capacity:
                        return False
                    if resource.capacity[capacity_type] < min_value:
                        return False
            
            elif req_key == "operator":
                if resource.operator != req_value:
                    return False
        
        return True
    
    def register_resource(self, resource: Resource) -> bool:
        """Register a new resource in the discovery service"""
        self.resources[resource.resource_id] = resource
        return True
    
    def update_resource_status(self, resource_id: str, status: ResourceStatus, location: Optional[Location] = None) -> bool:
        """Update resource status and location"""
        if resource_id not in self.resources:
            return False
        
        self.resources[resource_id].status = status
        if location:
            self.resources[resource_id].location = location
        
        return True

class DispatchFulfillmentService:
    """BeckN-style fulfillment service for emergency dispatch"""
    
    def __init__(self, discovery_service: BeckNDiscoveryService):
        self.discovery_service = discovery_service
        self.active_requests: Dict[str, DispatchRequest] = {}
        self.assignments: Dict[str, DispatchAssignment] = {}
        self.fulfillment_history: List[Dict] = []
    
    def create_dispatch_request(self, request_data: Dict) -> DispatchRequest:
        """Create a new dispatch request"""
        request = DispatchRequest(
            request_id=str(uuid.uuid4()),
            requester_id=request_data['requester_id'],
            location=Location(
                lat=request_data['location']['lat'],
                lon=request_data['location']['lon'],
                address=request_data['location'].get('address')
            ),
            resource_type=ResourceType(request_data['resource_type']),
            priority=request_data.get('priority', 3),
            requirements=request_data.get('requirements', {}),
            description=request_data['description'],
            created_at=datetime.utcnow(),
            deadline=datetime.fromisoformat(request_data['deadline']) if request_data.get('deadline') else None
        )
        
        self.active_requests[request.request_id] = request
        return request
    
    def assign_resource(self, request_id: str, resource_id: Optional[str] = None) -> Optional[DispatchAssignment]:
        """Assign a resource to a dispatch request"""
        if request_id not in self.active_requests:
            return None
        
        request = self.active_requests[request_id]
        
        # If no specific resource requested, find the best available one
        if not resource_id:
            available_resources = self.discovery_service.discover_resources(request)
            if not available_resources:
                return None
            resource_id = available_resources[0].resource_id
        
        # Check if resource exists and is available
        if resource_id not in self.discovery_service.resources:
            return None
        
        resource = self.discovery_service.resources[resource_id]
        if resource.status != ResourceStatus.AVAILABLE:
            return None
        
        # Create assignment
        assignment = DispatchAssignment(
            assignment_id=str(uuid.uuid4()),
            request_id=request_id,
            resource_id=resource_id,
            status=DispatchStatus.ASSIGNED,
            assigned_at=datetime.utcnow(),
            current_location=resource.location
        )
        
        # Calculate estimated arrival time
        distance = resource.location.distance_to(request.location)
        speed_mps = self._get_resource_speed(resource.resource_type)  # meters per second
        travel_time_seconds = distance / speed_mps
        assignment.estimated_arrival = datetime.utcnow() + timedelta(seconds=travel_time_seconds)
        
        # Generate route
        assignment.route = self._generate_route(resource.location, request.location)
        
        # Update resource status
        self.discovery_service.update_resource_status(resource_id, ResourceStatus.DISPATCHED)
        
        # Store assignment
        self.assignments[assignment.assignment_id] = assignment
        
        return assignment
    
    def _get_resource_speed(self, resource_type: ResourceType) -> float:
        """Get average speed for resource type in meters per second"""
        speeds = {
            ResourceType.DRONE: 15.0,  # ~54 km/h
            ResourceType.AUTONOMOUS_VEHICLE: 13.9,  # ~50 km/h
            ResourceType.EMERGENCY_TEAM: 11.1,  # ~40 km/h (with equipment)
            ResourceType.SUPPLY_DELIVERY: 8.3,  # ~30 km/h
            ResourceType.MEDICAL_UNIT: 16.7  # ~60 km/h
        }
        return speeds.get(resource_type, 10.0)
    
    def _generate_route(self, start: Location, end: Location) -> List[Location]:
        """Generate a simple route between two points"""
        # Simple linear interpolation for demo purposes
        # In production, would use actual routing service
        route = [start]
        
        # Add intermediate waypoints
        num_waypoints = max(2, int(start.distance_to(end) / 5000))  # One waypoint per 5km
        
        for i in range(1, num_waypoints):
            progress = i / num_waypoints
            lat = start.lat + (end.lat - start.lat) * progress
            lon = start.lon + (end.lon - start.lon) * progress
            route.append(Location(lat=lat, lon=lon))
        
        route.append(end)
        return route
    
    def update_assignment_progress(self, assignment_id: str) -> Optional[DispatchAssignment]:
        """Update assignment progress (simulate movement)"""
        if assignment_id not in self.assignments:
            return None
        
        assignment = self.assignments[assignment_id]
        resource = self.discovery_service.resources[assignment.resource_id]
        
        # Simulate progress based on time elapsed
        now = datetime.utcnow()
        elapsed = (now - assignment.assigned_at).total_seconds()
        
        if assignment.status == DispatchStatus.ASSIGNED:
            # Start dispatch
            assignment.status = DispatchStatus.DISPATCHED
            self.discovery_service.update_resource_status(assignment.resource_id, ResourceStatus.EN_ROUTE)
            
            assignment.progress_updates.append({
                'timestamp': now.isoformat(),
                'status': 'dispatched',
                'message': f'{resource.name} has been dispatched'
            })
        
        elif assignment.status == DispatchStatus.DISPATCHED:
            # Calculate current position along route
            if assignment.estimated_arrival:
                total_time = (assignment.estimated_arrival - assignment.assigned_at).total_seconds()
                progress = min(1.0, elapsed / total_time)
                
                if progress >= 1.0:
                    # Arrived at destination
                    assignment.status = DispatchStatus.IN_PROGRESS
                    assignment.actual_arrival = now
                    assignment.current_location = assignment.route[-1]  # Destination
                    self.discovery_service.update_resource_status(
                        assignment.resource_id, 
                        ResourceStatus.ARRIVED,
                        assignment.current_location
                    )
                    
                    assignment.progress_updates.append({
                        'timestamp': now.isoformat(),
                        'status': 'arrived',
                        'message': f'{resource.name} has arrived at destination'
                    })
                else:
                    # Update current position
                    route_index = int(progress * (len(assignment.route) - 1))
                    assignment.current_location = assignment.route[route_index]
                    
                    assignment.progress_updates.append({
                        'timestamp': now.isoformat(),
                        'status': 'en_route',
                        'message': f'{resource.name} is {int(progress * 100)}% of the way to destination',
                        'progress_percentage': int(progress * 100)
                    })
        
        elif assignment.status == DispatchStatus.IN_PROGRESS:
            # Simulate completion after some time at destination
            if assignment.actual_arrival:
                time_at_destination = (now - assignment.actual_arrival).total_seconds()
                if time_at_destination > 300:  # 5 minutes at destination
                    assignment.status = DispatchStatus.COMPLETED
                    assignment.completion_time = now
                    self.discovery_service.update_resource_status(assignment.resource_id, ResourceStatus.COMPLETED)
                    
                    assignment.progress_updates.append({
                        'timestamp': now.isoformat(),
                        'status': 'completed',
                        'message': f'{resource.name} has completed the mission'
                    })
                    
                    # Add to fulfillment history
                    self.fulfillment_history.append({
                        'assignment': assignment.to_dict(),
                        'resource': resource.to_dict(),
                        'request': self.active_requests[assignment.request_id].to_dict(),
                        'completed_at': now.isoformat()
                    })
                    
                    # Make resource available again
                    self.discovery_service.update_resource_status(assignment.resource_id, ResourceStatus.AVAILABLE)
        
        return assignment
    
    def get_assignment_status(self, assignment_id: str) -> Optional[Dict]:
        """Get current status of an assignment"""
        if assignment_id not in self.assignments:
            return None
        
        assignment = self.assignments[assignment_id]
        resource = self.discovery_service.resources[assignment.resource_id]
        request = self.active_requests[assignment.request_id]
        
        return {
            'assignment': assignment.to_dict(),
            'resource': resource.to_dict(),
            'request': request.to_dict(),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def cancel_assignment(self, assignment_id: str) -> bool:
        """Cancel an assignment"""
        if assignment_id not in self.assignments:
            return False
        
        assignment = self.assignments[assignment_id]
        assignment.status = DispatchStatus.CANCELLED
        
        # Make resource available again
        self.discovery_service.update_resource_status(assignment.resource_id, ResourceStatus.AVAILABLE)
        
        return True

# Global instances
discovery_service = BeckNDiscoveryService()
fulfillment_service = DispatchFulfillmentService(discovery_service)

