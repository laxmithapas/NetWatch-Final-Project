import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, LayoutDashboard, FileText, LogOut, BarChart4 } from 'lucide-react'

const Analytics = ({ setToken }) => {
  const navigate = useNavigate()

  const handleLogout = () => {
    setToken(null)
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar - Copied for simplicity but normally a separate component */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col items-start hidden md:flex">
        <div className="flex items-center space-x-3 mb-10 text-indigo-400">
          <Activity size={28} />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-rose-400 bg-clip-text text-transparent">NetWatch</h1>
        </div>

        <nav className="w-full space-y-2 flex-grow">
          <Link to="/" className="flex items-center space-x-3 p-3 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-xl transition-all">
            <LayoutDashboard size={20} />
            <span className="font-semibold">Dashboard</span>
          </Link>
          <Link to="/analytics" className="flex items-center space-x-3 p-3 bg-indigo-500/10 text-indigo-400 rounded-xl transition-all">
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
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
              <BarChart4 size={32} className="text-indigo-400" />
              Model Explainability & Metrics
            </h2>
            <p className="text-slate-400 mt-2">Insights into XGBoost decisions on CIC-IDS2018 Data</p>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* SHAP Values */}
          <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl col-span-1 lg:col-span-2 flex flex-col items-center">
            <h3 className="text-xl font-bold text-slate-200 mb-6 self-start">Feature Importance (SHAP Summary)</h3>
            <div className="w-full max-w-4xl bg-white/5 rounded-2xl p-4 flex justify-center border border-slate-700/50">
              <img 
                src="http://localhost:8000/plots/shap_summary.png" 
                alt="SHAP Summary Plot" 
                className="max-h-[500px] object-contain rounded-lg"
                onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }}
              />
              <div className="hidden text-slate-500 text-center py-20 flex-col items-center gap-4 w-full">
                 <BarChart4 size={48} className="opacity-50" />
                 <p>SHAP plot generation pending. Please ensure ML Pipeline has completed training.</p>
              </div>
            </div>
          </div>

          {/* Confusion Matrix */}
          <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-col items-center">
            <h3 className="text-xl font-bold text-slate-200 mb-6 self-start">Confusion Matrix</h3>
            <div className="w-full bg-white/5 rounded-2xl p-4 flex justify-center border border-slate-700/50">
              <img 
                src="http://localhost:8000/plots/XGBoost_cm.png" 
                alt="Confusion Matrix" 
                className="max-h-72 object-contain rounded-lg"
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
            <p className="text-sm text-slate-400 mt-4 self-start">Illustrates True Positives against False Positives on the validation set.</p>
          </div>

          {/* ROC Curve */}
          <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-col items-center">
            <h3 className="text-xl font-bold text-slate-200 mb-6 self-start">ROC Curve</h3>
            <div className="w-full bg-white/5 rounded-2xl p-4 flex justify-center border border-slate-700/50">
              <img 
                src="http://localhost:8000/plots/XGBoost_roc.png" 
                alt="ROC Curve" 
                className="max-h-72 object-contain rounded-lg"
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
            <p className="text-sm text-slate-400 mt-4 self-start">Receiver Operating Characteristic demonstrating the tradeoff between sensitivity and specificity.</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Analytics
