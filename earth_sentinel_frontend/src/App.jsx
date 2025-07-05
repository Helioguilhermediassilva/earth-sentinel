import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  AlertTriangle, 
  MapPin, 
  Zap, 
  DollarSign, 
  Truck, 
  Activity,
  Satellite,
  Shield,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Plane
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import './App.css'

const API_BASE = 'http://localhost:5000/api'

function App() {
  const [riskData, setRiskData] = useState([])
  const [activeContracts, setActiveContracts] = useState([])
  const [dispatchStatus, setDispatchStatus] = useState([])
  const [systemStats, setSystemStats] = useState({})
  const [isSimulating, setIsSimulating] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  // Fetch data from APIs
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch risk assessments
        const riskResponse = await fetch(`${API_BASE}/risk/historical?limit=10`)
        const riskData = await riskResponse.json()
        if (riskData.status === 'success') {
          setRiskData(riskData.assessments)
        }

        // Fetch contracts
        const contractsResponse = await fetch(`${API_BASE}/contracts`)
        const contractsData = await contractsResponse.json()
        if (contractsData.status === 'success') {
          setActiveContracts(contractsData.contracts)
        }

        // Fetch dispatch dashboard
        const dispatchResponse = await fetch(`${API_BASE}/dispatch/dashboard`)
        const dispatchData = await dispatchResponse.json()
        if (dispatchData.status === 'success') {
          setSystemStats(dispatchData.dashboard)
        }

        setLastUpdate(new Date())
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const simulateRiskEvent = async () => {
    setIsSimulating(true)
    try {
      // Create high-risk assessment
      const riskResponse = await fetch(`${API_BASE}/risk/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: { lat: -23.5505, lon: -46.6333 }
        })
      })
      
      const riskResult = await riskResponse.json()
      
      if (riskResult.status === 'success') {
        // Trigger contracts automatically
        await fetch(`${API_BASE}/contracts/auto-trigger`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            risk_assessment_id: riskResult.assessment_id
          })
        })

        // Simulate emergency dispatch
        await fetch(`${API_BASE}/dispatch/simulate-emergency`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            emergency_type: 'fire',
            location: { lat: -23.5505, lon: -46.6333, address: 'São Paulo Emergency Zone' }
          })
        })
      }
    } catch (error) {
      console.error('Error simulating event:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  const getRiskColor = (score) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  const getRiskLevel = (score) => {
    if (score >= 0.7) return 'HIGH'
    if (score >= 0.4) return 'MEDIUM'
    return 'LOW'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Earth Sentinel</h1>
                <p className="text-sm text-gray-500">Anticipatory Disaster Response Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-green-600">
                <Activity className="h-3 w-3 mr-1" />
                System Operational
              </Badge>
              <Button 
                onClick={simulateRiskEvent}
                disabled={isSimulating}
                className="bg-red-600 hover:bg-red-700"
              >
                {isSimulating ? (
                  <>
                    <Activity className="h-4 w-4 mr-2 animate-spin" />
                    Simulating...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Trigger Event
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Resources</CardTitle>
              <Truck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.total_resources || 0}</div>
              <p className="text-xs text-muted-foreground">
                {systemStats.active_assignments || 0} currently deployed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Risk Assessments</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{riskData.length}</div>
              <p className="text-xs text-muted-foreground">
                Last 24 hours
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Smart Contracts</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeContracts.length}</div>
              <p className="text-xs text-muted-foreground">
                Active contracts
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Last Update</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {lastUpdate.toLocaleTimeString()}
              </div>
              <p className="text-xs text-muted-foreground">
                Auto-refresh: 30s
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard */}
        <Tabs defaultValue="risk-map" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="risk-map">Risk Dashboard</TabsTrigger>
            <TabsTrigger value="contracts">Smart Contracts</TabsTrigger>
            <TabsTrigger value="dispatch">Dispatch & Tracking</TabsTrigger>
            <TabsTrigger value="payments">Payment Logs</TabsTrigger>
          </TabsList>

          {/* Risk Dashboard */}
          <TabsContent value="risk-map" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MapPin className="h-5 w-5 mr-2" />
                    Real-time Risk Map
                  </CardTitle>
                  <CardDescription>
                    Geographic risk assessment visualization
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-slate-100 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <Satellite className="h-12 w-12 mx-auto text-slate-400 mb-2" />
                      <p className="text-slate-600">Interactive Risk Map</p>
                      <p className="text-sm text-slate-500">São Paulo Region</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Risk Assessments</CardTitle>
                  <CardDescription>
                    Latest risk evaluations from federated models
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {riskData.slice(0, 5).map((assessment, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            assessment.risk_score >= 0.7 ? 'bg-red-500' :
                            assessment.risk_score >= 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                          }`} />
                          <div>
                            <p className="font-medium text-sm">{assessment.risk_type}</p>
                            <p className="text-xs text-slate-500">
                              {assessment.location.lat.toFixed(4)}, {assessment.location.lon.toFixed(4)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getRiskColor(assessment.risk_score)}>
                            {getRiskLevel(assessment.risk_score)}
                          </Badge>
                          <p className="text-xs text-slate-500 mt-1">
                            Score: {(assessment.risk_score * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Risk Trends</CardTitle>
                <CardDescription>
                  Risk score evolution over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={riskData.slice(-10)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis domain={[0, 1]} />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value) => [(value * 100).toFixed(1) + '%', 'Risk Score']}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="risk_score" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={{ fill: '#3b82f6' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Smart Contracts */}
          <TabsContent value="contracts" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="h-5 w-5 mr-2" />
                    Active Contracts
                  </CardTitle>
                  <CardDescription>
                    OpenSPP-style smart contracts for disaster response
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activeContracts.slice(0, 3).map((contract, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">Contract {contract.contract_id.slice(0, 8)}</h4>
                          <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
                            {contract.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">
                          {contract.conditions.length} conditions, {contract.payment_instructions.length} payments
                        </p>
                        <div className="flex items-center text-xs text-slate-500">
                          <Clock className="h-3 w-3 mr-1" />
                          Created: {new Date(contract.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Contract Execution History</CardTitle>
                  <CardDescription>
                    Recent contract triggers and executions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {activeContracts.filter(c => c.execution_history.length > 0).slice(0, 4).map((contract, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-slate-50 rounded-lg">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">Contract Executed</p>
                          <p className="text-xs text-slate-500">
                            {contract.execution_history.length} executions
                          </p>
                        </div>
                        <Badge variant="outline" className="text-green-600">
                          Success
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Dispatch & Tracking */}
          <TabsContent value="dispatch" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Truck className="h-5 w-5 mr-2" />
                    Active Dispatches
                  </CardTitle>
                  <CardDescription>
                    Real-time tracking of emergency resources
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {systemStats.recent_assignments?.slice(0, 4).map((assignment, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <Plane className="h-4 w-4 text-blue-500" />
                            <span className="font-medium">{assignment.resource_id}</span>
                          </div>
                          <Badge variant={assignment.status === 'completed' ? 'default' : 'secondary'}>
                            {assignment.status}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Progress</span>
                            <span>75%</span>
                          </div>
                          <Progress value={75} className="h-2" />
                          <p className="text-xs text-slate-500">
                            Assigned: {new Date(assignment.assigned_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Resource Status</CardTitle>
                  <CardDescription>
                    Current availability overview
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(systemStats.resource_statistics || {}).map(([type, stats]) => (
                      <div key={type} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="capitalize">{type.replace('_', ' ')}</span>
                          <span>{stats.available}/{stats.total}</span>
                        </div>
                        <Progress 
                          value={(stats.available / stats.total) * 100} 
                          className="h-2"
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Payment Logs */}
          <TabsContent value="payments" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <DollarSign className="h-5 w-5 mr-2" />
                  Payment Transaction Logs
                </CardTitle>
                <CardDescription>
                  Aadhaar Payment Bridge & OpenG2P transactions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((_, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <div>
                          <p className="font-medium">Emergency Relief Payment</p>
                          <p className="text-sm text-slate-500">
                            Beneficiary: BEN_{String(index + 1).padStart(3, '0')}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">$1,000.00</p>
                        <p className="text-sm text-slate-500">Aadhaar Bridge</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

