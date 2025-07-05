# Earth Sentinel - User Guide

## Quick Start Guide

Welcome to Earth Sentinel, your comprehensive anticipatory disaster response platform. This guide will walk you through using all the system's features to effectively monitor, predict, and respond to natural disasters.

## Getting Started

### Accessing the System

1. **Start the Backend Server**
   ```bash
   cd earth_sentinel_backend
   source venv/bin/activate
   python src/main.py
   ```
   The backend will be available at: http://localhost:5000

2. **Start the Frontend Dashboard**
   ```bash
   cd earth_sentinel_frontend
   pnpm run dev --host
   ```
   The dashboard will be available at: http://localhost:5173

3. **Open Your Browser**
   Navigate to http://localhost:5173 to access the Earth Sentinel dashboard.

## Dashboard Overview

The Earth Sentinel dashboard provides a comprehensive view of your disaster response system through several key sections:

### Main Dashboard
- **Active Resources**: Shows the number of emergency resources currently deployed
- **Risk Assessments**: Displays recent risk evaluations in the last 24 hours
- **Smart Contracts**: Indicates active automated response contracts
- **Last Update**: Shows when the system was last refreshed

### Navigation Tabs
- **Risk Dashboard**: Real-time risk monitoring and visualization
- **Smart Contracts**: Contract management and execution history
- **Dispatch & Tracking**: Resource deployment and GPS tracking
- **Payment Logs**: Transaction history and payment processing

## Using the Risk Dashboard

### Real-Time Risk Monitoring

The Risk Dashboard provides continuous monitoring of disaster risks across your area of responsibility.

#### Viewing Risk Maps
1. Click on the **"Risk Dashboard"** tab
2. The map displays current risk levels with color-coded zones:
   - **Green**: Low risk (0.0 - 0.3)
   - **Yellow**: Moderate risk (0.3 - 0.6)
   - **Orange**: High risk (0.6 - 0.8)
   - **Red**: Critical risk (0.8 - 1.0)

#### Understanding Risk Assessments
Each risk assessment includes:
- **Risk Score**: Numerical value from 0.0 to 1.0
- **Risk Type**: Primary threat (flood, earthquake, fire, extreme weather)
- **Confidence Level**: Reliability of the prediction
- **Contributing Factors**: Breakdown of risk components
- **Geofence Radius**: Area of potential impact

#### Manual Risk Assessment
To manually assess risk for a specific location:

1. Use the API endpoint:
   ```bash
   curl -X POST http://localhost:5000/api/risk/assess \
     -H "Content-Type: application/json" \
     -d '{
       "location": {
         "lat": -23.5505,
         "lon": -46.6333
       }
     }'
   ```

2. The system will return:
   ```json
   {
     "risk_score": 0.28,
     "risk_type": "fire",
     "confidence": 0.15,
     "geofence_radius": 960,
     "recommendation": "Low risk - Continue normal operations"
   }
   ```

## Managing Smart Contracts

### Understanding Smart Contracts

Smart contracts in Earth Sentinel automatically trigger emergency responses when specific conditions are met. They operate on the OpenSPP trust framework and ensure rapid, consistent responses to disasters.

#### Contract Components
- **Conditions**: Triggers that activate the contract (e.g., risk threshold exceeded)
- **Payment Instructions**: Automatic fund disbursement to affected populations
- **Trust Verification**: Multi-node consensus for contract execution

#### Creating a New Contract

1. Navigate to the **Smart Contracts** tab
2. Use the API to create a contract:
   ```bash
   curl -X POST http://localhost:5000/api/contracts/create \
     -H "Content-Type: application/json" \
     -d '{
       "conditions": [
         {
           "condition_type": "risk_threshold",
           "parameters": {"threshold": 0.7},
           "description": "Activate when risk exceeds 70%"
         }
       ],
       "payment_instructions": [
         {
           "beneficiary_id": "COMMUNITY_001",
           "amount": 5000,
           "currency": "USD",
           "payment_method": "aadhaar_bridge",
           "priority": 1,
           "metadata": {"purpose": "Emergency evacuation funds"}
         }
       ]
     }'
   ```

#### Contract Templates

The system provides pre-configured templates for common scenarios:

**Flood Response Contract**
- Triggers at 80% flood risk
- Provides $2,000 per affected household
- Activates evacuation resources

**Earthquake Response Contract**
- Triggers at 75% seismic risk
- Provides $3,000 per affected household
- Dispatches search and rescue teams

**Fire Response Contract**
- Triggers at 70% fire risk
- Provides $1,500 per affected household
- Activates firefighting resources

#### Monitoring Contract Execution

The Smart Contracts tab displays:
- **Active Contracts**: Currently monitoring conditions
- **Execution History**: Past contract activations
- **Trust Verification**: Consensus status from multiple nodes
- **Payment Status**: Success/failure of fund disbursements

## Payment System Operations

### Aadhaar Payment Bridge

The Aadhaar Payment Bridge enables secure, biometric-verified payments to disaster-affected individuals.

#### Processing Individual Payments

1. **Verify Beneficiary Identity**
   ```bash
   curl -X POST http://localhost:5000/api/payments/aadhaar-bridge \
     -H "Content-Type: application/json" \
     -d '{
       "beneficiary_aadhaar": "1234567890123456",
       "amount": 1000,
       "currency": "USD",
       "purpose": "Emergency relief payment"
     }'
   ```

2. **Payment Verification Process**
   - Biometric authentication
   - Identity verification against registry
   - Fraud detection checks
   - Transaction processing
   - Confirmation delivery

#### Payment Status Tracking

Monitor payment status through:
- **Transaction ID**: Unique identifier for each payment
- **Processing Status**: Pending, verified, completed, failed
- **Delivery Method**: Bank transfer, digital wallet, mobile money
- **Confirmation Receipt**: Beneficiary acknowledgment

### OpenG2P Integration

OpenG2P provides comprehensive social protection program management for large-scale disaster response.

#### Creating Relief Programs

1. **Define Program Parameters**
   ```bash
   curl -X POST http://localhost:5000/api/payments/openg2p/program \
     -H "Content-Type: application/json" \
     -d '{
       "program_name": "Hurricane Relief 2025",
       "budget": 500000,
       "criteria": {
         "disaster_affected": true,
         "income_threshold": 40000,
         "vulnerability_score": 0.6
       }
     }'
   ```

2. **Program Components**
   - **Eligibility Criteria**: Who qualifies for assistance
   - **Budget Allocation**: Total funds available
   - **Payment Schedule**: Timing and frequency of disbursements
   - **Geographic Scope**: Areas covered by the program

#### Batch Payment Processing

For large-scale disasters, use batch processing:

1. **Upload Beneficiary List**
   - CSV format with Aadhaar numbers
   - Verification of eligibility
   - Duplicate detection and removal

2. **Process Payments**
   - Automated verification pipeline
   - Parallel processing for efficiency
   - Real-time status monitoring
   - Exception handling for failed payments

## Dispatch and Resource Management

### Resource Discovery

The BeckN-style discovery service helps locate and deploy emergency resources efficiently.

#### Finding Available Resources

1. **Search by Type and Location**
   ```bash
   curl -X POST http://localhost:5000/api/dispatch/resources/discover \
     -H "Content-Type: application/json" \
     -d '{
       "location": {"lat": -23.5505, "lon": -46.6333},
       "resource_type": "drone",
       "requirements": {"capabilities": ["aerial_surveillance"]},
       "max_distance_km": 30
     }'
   ```

2. **Resource Types Available**
   - **Drones**: Aerial surveillance, damage assessment, search operations
   - **Autonomous Vehicles**: Evacuation, supply delivery, medical transport
   - **Emergency Teams**: Specialized response personnel
   - **Equipment**: Generators, medical supplies, communication gear

#### Resource Capabilities

Each resource type offers specific capabilities:

**Drone Capabilities**
- Aerial surveillance and reconnaissance
- Thermal imaging for search and rescue
- Real-time video streaming
- GPS mapping and navigation
- Weather monitoring

**Autonomous Vehicle Capabilities**
- Passenger evacuation (up to 8 people)
- Supply delivery (up to 500kg)
- Medical transport with life support
- Communication relay systems
- Terrain navigation

### Creating Dispatch Requests

#### Emergency Dispatch Process

1. **Submit Dispatch Request**
   ```bash
   curl -X POST http://localhost:5000/api/dispatch/request \
     -H "Content-Type: application/json" \
     -d '{
       "requester_id": "emergency_coordinator_001",
       "location": {
         "lat": -23.5505,
         "lon": -46.6333,
         "address": "Downtown Emergency Zone"
       },
       "resource_type": "drone",
       "priority": 1,
       "requirements": {"capabilities": ["thermal_imaging"]},
       "description": "Search for missing persons in collapsed building"
     }'
   ```

2. **Automatic Resource Assignment**
   - System identifies best available resource
   - Considers distance, capabilities, and availability
   - Generates optimal route to destination
   - Provides estimated arrival time

#### Priority Levels

Dispatch requests use priority levels:
- **Priority 1**: Life-threatening emergencies (immediate response)
- **Priority 2**: Urgent situations (response within 30 minutes)
- **Priority 3**: Important but non-critical (response within 2 hours)
- **Priority 4**: Routine operations (response within 24 hours)

### Real-Time Tracking

#### GPS Monitoring

Once resources are dispatched, track their progress:

1. **Get Tracking Information**
   ```bash
   curl -X GET http://localhost:5000/api/dispatch/assignment/{assignment_id}/track
   ```

2. **Tracking Data Includes**
   - Current GPS coordinates
   - Progress percentage
   - Estimated time of arrival
   - Route optimization updates
   - Status messages from operators

#### Status Updates

Resources provide regular status updates:
- **En Route**: Traveling to destination
- **On Scene**: Arrived and operational
- **Returning**: Mission complete, returning to base
- **Maintenance**: Offline for repairs or refueling

## Emergency Simulation

### Testing System Response

Use the emergency simulation feature to test your disaster response protocols.

#### Triggering Simulations

1. **Click the "Trigger Event" Button** in the dashboard
2. **Or use the API**:
   ```bash
   curl -X POST http://localhost:5000/api/dispatch/simulate-emergency \
     -H "Content-Type: application/json" \
     -d '{
       "emergency_type": "earthquake",
       "location": {
         "lat": -23.5505,
         "lon": -46.6333,
         "address": "São Paulo Test Emergency"
       }
     }'
   ```

#### Simulation Scenarios

Available emergency types:
- **Earthquake**: Seismic event with building damage
- **Flood**: Water level rise with evacuation needs
- **Fire**: Wildfire or urban fire spread
- **Extreme Weather**: Hurricane, tornado, or severe storm
- **General**: Multi-hazard emergency scenario

#### Simulation Results

Each simulation provides:
- **Resources Dispatched**: Number and type of resources deployed
- **Response Time**: How quickly the system responded
- **Coverage Area**: Geographic scope of the response
- **Estimated Impact**: Predicted effectiveness of the response

## Data Management

### Sensor Network Monitoring

#### IoT Sensor Data

Monitor environmental conditions through the sensor network:

1. **View Sensor Status**
   ```bash
   curl -X GET http://localhost:5000/api/xroad/iot-sensors
   ```

2. **Sensor Types**
   - **Environmental**: Temperature, humidity, air pressure
   - **Seismic**: Ground motion and vibration
   - **Hydrological**: Water levels and flow rates
   - **Meteorological**: Wind speed, precipitation, visibility

#### Data Quality Assurance

The system automatically validates sensor data:
- **Range Checking**: Values within expected parameters
- **Consistency Verification**: Cross-validation between sensors
- **Temporal Analysis**: Trend validation over time
- **Anomaly Detection**: Identification of unusual readings

### Satellite Imagery Integration

#### Accessing Satellite Data

1. **Retrieve Latest Imagery**
   ```bash
   curl -X GET http://localhost:5000/api/xroad/satellite-imagery
   ```

2. **Image Types Available**
   - **Optical**: Visible light imagery for damage assessment
   - **Radar**: All-weather imaging for flood monitoring
   - **Thermal**: Heat detection for fire monitoring
   - **Multispectral**: Vegetation and environmental analysis

#### Image Analysis Features

Automated analysis provides:
- **Change Detection**: Comparison with historical imagery
- **Damage Assessment**: Identification of affected structures
- **Flood Mapping**: Water extent and depth estimation
- **Fire Perimeter**: Active fire boundaries and spread direction

## System Administration

### User Management

#### Role-Based Access Control

The system supports multiple user roles:
- **System Administrator**: Full system access and configuration
- **Emergency Coordinator**: Dispatch and response management
- **Risk Analyst**: Risk assessment and modeling
- **Payment Officer**: Financial transaction management
- **Field Operator**: Resource status updates and reporting

#### Creating User Accounts

1. **Register New Users** through the admin interface
2. **Assign Appropriate Roles** based on responsibilities
3. **Configure Access Permissions** for specific functions
4. **Set Up Authentication** using secure credentials

### System Monitoring

#### Health Checks

Monitor system health through:
- **API Endpoint Status**: Availability of all services
- **Database Connectivity**: Data storage and retrieval
- **External Integrations**: Third-party service connections
- **Resource Utilization**: CPU, memory, and storage usage

#### Performance Metrics

Track system performance:
- **Response Times**: API endpoint latency
- **Throughput**: Requests processed per second
- **Error Rates**: Failed requests and system errors
- **Availability**: System uptime and reliability

### Backup and Recovery

#### Data Backup Procedures

1. **Automated Daily Backups** of all system data
2. **Incremental Backups** every 4 hours during active operations
3. **Offsite Storage** for disaster recovery
4. **Backup Verification** to ensure data integrity

#### Recovery Procedures

In case of system failure:
1. **Assess the Scope** of the problem
2. **Activate Backup Systems** if available
3. **Restore from Latest Backup** if necessary
4. **Verify System Functionality** before resuming operations
5. **Document the Incident** for future prevention

## Best Practices

### Operational Guidelines

#### Daily Operations

1. **Morning System Check**
   - Verify all services are running
   - Review overnight alerts and notifications
   - Check sensor network status
   - Validate data quality metrics

2. **Risk Assessment Review**
   - Analyze current risk levels
   - Review model predictions
   - Update threat assessments
   - Communicate findings to stakeholders

3. **Resource Status Update**
   - Verify resource availability
   - Check maintenance schedules
   - Update capability assessments
   - Coordinate with partner organizations

#### Emergency Response Protocols

1. **Immediate Response (0-15 minutes)**
   - Activate emergency protocols
   - Deploy immediate response resources
   - Notify relevant authorities
   - Begin damage assessment

2. **Short-term Response (15 minutes - 4 hours)**
   - Coordinate resource deployment
   - Establish communication networks
   - Begin evacuation procedures if necessary
   - Activate payment systems for affected populations

3. **Medium-term Response (4-24 hours)**
   - Assess overall situation
   - Coordinate with external agencies
   - Establish temporary shelters
   - Continue search and rescue operations

4. **Long-term Response (24+ hours)**
   - Begin recovery planning
   - Coordinate reconstruction efforts
   - Provide ongoing support to affected populations
   - Conduct post-incident analysis

### Security Considerations

#### Data Protection

1. **Encrypt Sensitive Data** both at rest and in transit
2. **Implement Access Controls** based on user roles
3. **Monitor System Access** and maintain audit logs
4. **Regular Security Updates** for all system components

#### Privacy Protection

1. **Anonymize Personal Data** where possible
2. **Obtain Consent** for data collection and use
3. **Limit Data Retention** to necessary periods
4. **Provide Data Access Rights** to individuals

## Troubleshooting

### Common Issues

#### System Not Responding

1. **Check Service Status**
   ```bash
   curl -X GET http://localhost:5000/api/health
   ```

2. **Restart Services** if necessary
   ```bash
   # Backend
   cd earth_sentinel_backend
   python src/main.py
   
   # Frontend
   cd earth_sentinel_frontend
   pnpm run dev --host
   ```

#### Data Quality Issues

1. **Verify Sensor Connectivity**
2. **Check Data Validation Rules**
3. **Review Error Logs** for specific issues
4. **Contact Sensor Manufacturers** if hardware problems persist

#### Payment Processing Failures

1. **Verify Beneficiary Information**
2. **Check Payment Gateway Status**
3. **Review Transaction Logs**
4. **Retry Failed Payments** after resolving issues

### Getting Support

#### Technical Support

For technical issues:
1. **Check the Documentation** for known solutions
2. **Review System Logs** for error messages
3. **Contact the Development Team** with specific details
4. **Submit Bug Reports** through the issue tracking system

#### Training and Education

For user training:
1. **Schedule Training Sessions** for new users
2. **Provide Documentation** and user guides
3. **Conduct Regular Drills** to maintain readiness
4. **Share Best Practices** with the user community

## Conclusion

Earth Sentinel provides a comprehensive platform for anticipatory disaster response, combining advanced technologies with practical operational capabilities. By following this user guide, you can effectively leverage the system's features to protect communities and respond rapidly to natural disasters.

Remember that effective disaster response requires not just technology, but also well-trained personnel, clear procedures, and regular practice. Use Earth Sentinel as part of a comprehensive emergency management strategy that includes community engagement, inter-agency coordination, and continuous improvement based on lessons learned.

For additional support and resources, consult the technical documentation, participate in user forums, and engage with the Earth Sentinel community to share experiences and best practices.

---

**Earth Sentinel** - Empowering communities through anticipatory disaster response technology.

