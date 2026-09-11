import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Attendance() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/attendance').then(({ data }) => setRecords(data)).finally(() => setLoading(false))
  }, [])

  const statusColor = (s) =>
    ({
      Present: 'bg-emerald-50 text-emerald-700',
      Absent: 'bg-red-50 text-red-700',
      'Half Day': 'bg-amber-50 text-amber-700',
      Leave: 'bg-slate-100 text-slate-600',
      WFH: 'bg-indigo-50 text-indigo-700',
    }[s] || 'bg-slate-100 text-slate-600')

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Attendance</h2>
        <p className="text-slate-500 text-sm">Daily attendance and shift records</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-5 py-3">Employee ID</th>
              <th className="text-left px-5 py-3">Date</th>
              <th className="text-left px-5 py-3">Check In</th>
              <th className="text-left px-5 py-3">Check Out</th>
              <th className="text-left px-5 py-3">Hours</th>
              <th className="text-left px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={6} className="px-5 py-6 text-center text-slate-400">Loading...</td></tr>
            ) : records.length === 0 ? (
              <tr><td colSpan={6} className="px-5 py-6 text-center text-slate-400">No attendance records.</td></tr>
            ) : (
              records.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3">{r.employee_id}</td>
                  <td className="px-5 py-3">{r.date}</td>
                  <td className="px-5 py-3">{r.check_in || '—'}</td>
                  <td className="px-5 py-3">{r.check_out || '—'}</td>
                  <td className="px-5 py-3">{r.hours_worked ?? '—'}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(r.status)}`}>{r.status}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
