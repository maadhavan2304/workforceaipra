import { useEffect, useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Leaves() {
  const [leaves, setLeaves] = useState([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  const canApprove = ['Admin', 'HR', 'Manager'].includes(user?.role)

  const load = () => {
    setLoading(true)
    api.get('/leaves').then(({ data }) => setLeaves(data)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const decide = async (id, status) => {
    await api.patch(`/leaves/${id}/decision`, { status })
    load()
  }

  const statusColor = (s) =>
    ({ Approved: 'bg-emerald-50 text-emerald-700', Rejected: 'bg-red-50 text-red-700', Pending: 'bg-amber-50 text-amber-700' }[s])

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Leave Management</h2>
        <p className="text-slate-500 text-sm">Track and approve leave requests</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-5 py-3">Employee ID</th>
              <th className="text-left px-5 py-3">Type</th>
              <th className="text-left px-5 py-3">From</th>
              <th className="text-left px-5 py-3">To</th>
              <th className="text-left px-5 py-3">Status</th>
              {canApprove && <th className="text-left px-5 py-3">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={6} className="px-5 py-6 text-center text-slate-400">Loading...</td></tr>
            ) : leaves.length === 0 ? (
              <tr><td colSpan={6} className="px-5 py-6 text-center text-slate-400">No leave requests.</td></tr>
            ) : (
              leaves.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3">{l.employee_id}</td>
                  <td className="px-5 py-3">{l.leave_type}</td>
                  <td className="px-5 py-3">{l.start_date}</td>
                  <td className="px-5 py-3">{l.end_date}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(l.status)}`}>{l.status}</span>
                  </td>
                  {canApprove && (
                    <td className="px-5 py-3 space-x-2">
                      {l.status === 'Pending' && (
                        <>
                          <button onClick={() => decide(l.id, 'Approved')} className="text-emerald-600 text-xs font-medium hover:underline">Approve</button>
                          <button onClick={() => decide(l.id, 'Rejected')} className="text-red-600 text-xs font-medium hover:underline">Reject</button>
                        </>
                      )}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
