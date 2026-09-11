import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from 'recharts'
import api from '../api/client'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/dashboard/overview'),
      api.get('/dashboard/attendance-trend?days=14'),
    ])
      .then(([o, t]) => {
        setOverview(o.data)
        setTrend(t.data)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-slate-500">Loading dashboard...</div>

  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Workforce Overview</h2>
        <p className="text-slate-500 text-sm">Real-time snapshot of your organization</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Active Employees" value={overview.total_active_employees} accent="indigo" />
        <StatCard label="Present Today" value={overview.present_today} accent="green" />
        <StatCard label="On Leave Today" value={overview.on_leave_today} accent="amber" />
        <StatCard label="Pending Leave Requests" value={overview.pending_leave_requests} accent="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-4">Attendance Trend (14 days)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="present_count" stroke="#4f46e5" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-4">Headcount by Department</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={overview.department_breakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="department" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
