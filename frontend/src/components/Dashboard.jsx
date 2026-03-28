import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldAlert, ShieldCheck, Activity, Download, FileText, LayoutDashboard, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import axios from 'axios'

const Dashboard = ({ setToken }) => {
  const navigate = useNavigate()
  const [trafficData, setTrafficData] = useState([])
  const [alerts, setAlerts] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [activeAlert, setActiveAlert] = useState(null)
  
  // Stats
  const [stats, setStats] = useState({
    totalPackets: 0,
    anomalies: 0,
    benign: 0
  })

  useEffect(() => {
    // Initial fetch of recent alerts
    const fetchAlerts = async () => {
      try {
        const token = localStorage.getItem('token')
        const res = await axios.get('http://localhost:8000/api/v1/alerts/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setAlerts(res.data)
      } catch (err) {
        console.error("Failed to fetch alerts:", err)
      }
    }
    fetchAlerts()

    // WebSocket Connection
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/traffic')

    ws.onopen = () => setIsConnected(true)
    ws.onclose = () => setIsConnected(false)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      // Update charts
      setTrafficData(prev => {
        const newArr = [...prev, { time: new Date().toLocaleTimeString(), confidence: data.confidence, isAnomaly: data.is_anomaly }]
        if (newArr.length > 20) newArr.shift() // Keep last 20
        return newArr
      })

      // Update Stats
      setStats(prev => ({
        totalPackets: prev.totalPackets + 1,
        anomalies: data.is_anomaly ? prev.anomalies + 1 : prev.anomalies,
        benign: !data.is_anomaly ? prev.benign + 1 : prev.benign
      }))

      if (data.is_anomaly) {
        setActiveAlert(data)
        setAlerts(prev => [data, ...prev].slice(0, 50)) // Keep last 50
        
        // Hide red banner after 3 seconds
        setTimeout(() => setActiveAlert(null), 3000)
      }
    }

    return () => ws.close()
  }, [])

  const handleLogout = () => {
    setToken(null)
    navigate('/login')
  }

  const handleDownloadPDF = async (alertId) => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`http://localhost:8000/api/v1/alerts/${alertId}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `NetWatch_Alert_${alertId}.pdf`)
      document.body.appendChild(link)
      link.click()
    } catch (err) {
      console.error("Failed to download PDF", err)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col items-start hidden md:flex">
        <div className="flex items-center space-x-3 mb-10 text-indigo-400">
          <Activity size={28} />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-rose-400 bg-clip-text text-transparent">NetWatch</h1>
        </div>

        <nav className="w-full space-y-2 flex-grow">
          <Link to="/" className="flex items-center space-x-3 p-3 bg-indigo-500/10 text-indigo-400 rounded-xl transition-all">
            <LayoutDashboard size={20} />
            <span className="font-semibold">Dashboard</span>
          </Link>
          <Link to="/analytics" className="flex items-center space-x-3 p-3 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-xl transition-all">
            <FileText size={20} />
            <span className="font-semibold">Analytics View</span>
          </Link>
        </nav>

        <button onClick={handleLogout} className="flex items-center space-x-3 p-3 text-slate-400 hover:text-rose-400 w-full rounded-xl transition-all">
          <LogOut size={20} />
          <span className="font-semibold">Sign Out</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-100">Live Traffic Surveillance</h2>
            <div className="flex items-center space-x-2 mt-2">
              <span className="relative flex h-3 w-3">
                {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
              <p className="text-sm text-slate-400">{isConnected ? 'System Online & Processing' : 'Disconnected from Node'}</p>
            </div>
          </div>
        </header>

        {/* Dynamic Red Banner for active attacks */}
        <AnimatePresence>
          {activeAlert && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="mb-8 p-4 bg-rose-500/20 border border-rose-500 rounded-xl flex items-center justify-between"
            >
              <div className="flex items-center space-x-4 text-rose-400">
                <ShieldAlert className="animate-pulse" size={28} />
                <div>
                  <h4 className="font-bold text-lg text-rose-300">INTRUSION DETECTED!</h4>
                  <p className="text-sm">Type: {activeAlert.attack_type} | Source IP: {activeAlert.source_ip} | Confidence: {activeAlert.confidence.toFixed(1)}%</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-semibold mb-1">Total Packets</p>
              <h3 className="text-3xl font-bold text-slate-100">{stats.totalPackets}</h3>
            </div>
            <div className="p-4 bg-indigo-500/10 rounded-xl text-indigo-400">
              <Activity size={24} />
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-semibold mb-1">Benign Traffic</p>
              <h3 className="text-3xl font-bold text-emerald-400">{stats.benign}</h3>
            </div>
            <div className="p-4 bg-emerald-500/10 rounded-xl text-emerald-400">
              <ShieldCheck size={24} />
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex items-center justify-between relative overflow-hidden">
            <div className="absolute right-0 top-0 w-32 h-32 bg-rose-500/10 blur-2xl rounded-full" />
            <div className="relative z-10">
              <p className="text-slate-400 text-sm font-semibold mb-1">Anomalies Blocked</p>
              <h3 className="text-3xl font-bold text-rose-400">{stats.anomalies}</h3>
            </div>
            <div className="p-4 bg-rose-500/10 rounded-xl text-rose-400 relative z-10">
              <ShieldAlert size={24} />
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl mb-8">
          <h3 className="text-xl font-bold text-slate-100 mb-6">Threat Confidence Trajectory</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trafficData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                  itemStyle={{ color: '#818cf8' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="confidence" 
                  stroke="#818cf8" 
                  strokeWidth={3} 
                  dot={false}
                  activeDot={{ r: 8, fill: '#818cf8', stroke: '#0f172a', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alerts Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
          <div className="p-6 border-b border-slate-800">
            <h3 className="text-xl font-bold text-slate-100">Recent Incidence Logs</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-400">
              <thead className="bg-slate-950/50 text-slate-300 font-semibold uppercase text-xs">
                <tr>
                  <th className="px-6 py-4">Time</th>
                  <th className="px-6 py-4">Source IP</th>
                  <th className="px-6 py-4">Target IP</th>
                  <th className="px-6 py-4">Attack Vector</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, i) => (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                    <td className="px-6 py-4 font-mono text-xs">{alert.source_ip}</td>
                    <td className="px-6 py-4 font-mono text-xs">{alert.destination_ip}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-rose-500/10 text-rose-400 rounded text-xs font-semibold">
                        {alert.attack_type || 'Anomaly'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-rose-500" 
                            style={{ width: `${alert.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs">{alert.confidence?.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {(alert.id || alert.db_id) && (
                        <button 
                          onClick={() => handleDownloadPDF(alert.id || alert.db_id)}
                          className="p-2 text-indigo-400 hover:bg-indigo-500/20 rounded-lg transition-colors"
                          title="Download PDF Report"
                        >
                          <Download size={16} />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {alerts.length === 0 && (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-slate-500">
                      No anomalies detected yet. Monitoring systems active.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  )
}

export default Dashboard
