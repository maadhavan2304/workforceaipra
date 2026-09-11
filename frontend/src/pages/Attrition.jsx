import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import api from '../api/client'
import StatCard from '../components/StatCard'

const RISK_COLORS = { Low: '#10b981', Medium: '#f59e0b', High: '#f97316', Critical: '#ef4444' }

export default function Attrition() {
  const [summary, setSummary] = useState(null)
  const [risks, setRisks] = useState([])
  const [loading, setLoading] = useState(true)
  const [runningBatch, setRunningBatch] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    Promise.all([api.get('/ai/analytics/summary'), api.get('/ai/risk-monitor')])
      .then(([s, r]) => {
        setSummary(s.data)
        setRisks(r.data)
      })
      .catch((e) => setError(e.response?.data?.detail || 'AI model not available yet. Train it first.'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const runBatchPrediction = async () => {
    setRunningBatch(true)
    setError('')
    try {
      await api.post('/ai/predict/batch/all')
      load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to run predictions')
    } finally {
      setRunningBatch(false)
    }
  }

  const pieData = summary
    ? Object.entries(summary.risk_distribution).map(([level, count]) => ({ name: level, value: count }))
    : []

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">AI Attrition Intelligence</h2>
          <p className="text-slate-500 text-sm">Predictive risk scoring powered by machine learning</p>
        </div>
        <button
          onClick={runBatchPrediction}
          disabled={runningBatch}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-60"
        >
          {runningBatch ? 'Running predictions...' : 'Run Predictions for All Employees'}
        </button>
      </div>

      {error && (
        <div className="bg-amber-50 text-amber-800 text-sm px-4 py-3 rounded-lg border border-amber-200">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-slate-500">Loading...</div>
      ) : summary ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Attrition Rate" value={`${summary.attrition_rate_percent}%`} accent="red" />
            <StatCard label="High Risk Employees" value={summary.high_risk_employee_count} accent="amber" />
            <StatCard label="Active Employees" value={summary.total_active_employees} accent="indigo" />
            <StatCard label="Exited Employees" value={summary.total_exited_employees} accent="green" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <h3 className="font-semibold text-slate-800 mb-4">Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-100">
                <h3 className="font-semibold text-slate-800">Employees at Risk</h3>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="text-left px-5 py-3">Employee</th>
                    <th className="text-left px-5 py-3">Risk Score</th>
                    <th className="text-left px-5 py-3">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {risks.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="px-5 py-6 text-center text-slate-400">
                        No predictions yet. Click "Run Predictions" above.
                      </td>
                    </tr>
                  ) : (
                    risks.slice(0, 15).map((r) => (
                      <tr key={r.employee_id} className="hover:bg-slate-50">
                        <td className="px-5 py-3 font-medium text-slate-800">{r.employee_name}</td>
                        <td className="px-5 py-3 text-slate-500">{(r.risk_score * 100).toFixed(1)}%</td>
                        <td className="px-5 py-3">
                          <span
                            className="px-2 py-1 rounded-full text-xs font-medium"
                            style={{
                              color: RISK_COLORS[r.risk_level],
                              backgroundColor: `${RISK_COLORS[r.risk_level]}1a`,
                            }}
                          >
                            {r.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}
