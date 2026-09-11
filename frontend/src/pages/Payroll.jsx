import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Payroll() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/payroll').then(({ data }) => setRecords(data)).finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Payroll</h2>
        <p className="text-slate-500 text-sm">Salary processing and payment records</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-5 py-3">Employee ID</th>
              <th className="text-left px-5 py-3">Month/Year</th>
              <th className="text-left px-5 py-3">Basic</th>
              <th className="text-left px-5 py-3">Allowances</th>
              <th className="text-left px-5 py-3">Deductions</th>
              <th className="text-left px-5 py-3">Net Salary</th>
              <th className="text-left px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={7} className="px-5 py-6 text-center text-slate-400">Loading...</td></tr>
            ) : records.length === 0 ? (
              <tr><td colSpan={7} className="px-5 py-6 text-center text-slate-400">No payroll records.</td></tr>
            ) : (
              records.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3">{r.employee_id}</td>
                  <td className="px-5 py-3">{r.month}/{r.year}</td>
                  <td className="px-5 py-3">₹{r.basic_salary.toLocaleString()}</td>
                  <td className="px-5 py-3">₹{r.allowances.toLocaleString()}</td>
                  <td className="px-5 py-3">₹{r.deductions.toLocaleString()}</td>
                  <td className="px-5 py-3 font-medium">₹{r.net_salary.toLocaleString()}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${r.status === 'Paid' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                      {r.status}
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
