import { useEffect, useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  const canEdit = ['Admin', 'HR'].includes(user?.role)

  const load = () => {
    setLoading(true)
    api
      .get('/employees', { params: { search: search || undefined, limit: 100 } })
      .then(({ data }) => setEmployees(data))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const timeout = setTimeout(load, 300)
    return () => clearTimeout(timeout)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search])

  const statusColor = (status) =>
    ({
      Active: 'bg-emerald-50 text-emerald-700',
      Resigned: 'bg-red-50 text-red-700',
      Terminated: 'bg-red-50 text-red-700',
      'On Leave': 'bg-amber-50 text-amber-700',
    }[status] || 'bg-slate-100 text-slate-600')

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Employees</h2>
          <p className="text-slate-500 text-sm">Manage your workforce roster</p>
        </div>
        {canEdit && (
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
            + Add Employee
          </button>
        )}
      </div>

      <input
        type="text"
        placeholder="Search by name, code, or email..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-5 py-3">Employee</th>
              <th className="text-left px-5 py-3">Code</th>
              <th className="text-left px-5 py-3">Designation</th>
              <th className="text-left px-5 py-3">Email</th>
              <th className="text-left px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : employees.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-slate-400">
                  No employees found.
                </td>
              </tr>
            ) : (
              employees.map((emp) => (
                <tr key={emp.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 font-medium text-slate-800">{emp.full_name}</td>
                  <td className="px-5 py-3 text-slate-500">{emp.employee_code}</td>
                  <td className="px-5 py-3 text-slate-500">{emp.designation || '—'}</td>
                  <td className="px-5 py-3 text-slate-500">{emp.email}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(emp.status)}`}>
                      {emp.status}
                    </span>
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
