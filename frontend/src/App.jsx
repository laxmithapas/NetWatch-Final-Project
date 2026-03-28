import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Analytics from './components/Analytics'
import './index.css'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }, [token])

  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-indigo-500/30">
        <Routes>
          <Route path="/login" element={!token ? <Login setToken={setToken} /> : <Navigate to="/" />} />
          <Route path="/" element={token ? <Dashboard setToken={setToken} /> : <Navigate to="/login" />} />
          <Route path="/analytics" element={token ? <Analytics setToken={setToken}/> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
