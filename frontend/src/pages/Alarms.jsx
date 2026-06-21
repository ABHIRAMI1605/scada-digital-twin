import { useEffect, useState } from 'react'
import { useLiveData } from '../context/LiveDataContext'
import { injectFault, clearFault, getAlarms } from '../api/client'

export default function Alarms() {
  const { alarms, setAlarms } = useLiveData()
  const [pending, setPending] = useState(false)

  useEffect(() => {
    getAlarms(50).then((res) => {
      setAlarms((prev) => {
        const seen = new Set(prev.map((a) => a.timestamp + a.ansi_code))
        const merged = [...prev]
        for (const a of res.data) {
          if (!seen.has(a.timestamp + a.ansi_code)) merged.push(a)
        }
        return merged.slice(0, 100)
      })
    })
  }, [])

  const handleFault = async (type) => {
    setPending(true)
    try {
      await injectFault(type)
    } finally {
      setPending(false)
    }
  }

  const handleClear = async () => {
    setPending(true)
    try {
      await clearFault()
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-6">Fault Control & Alarm History</h2>

      <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg p-4 mb-6 flex gap-3">
        <button disabled={pending} onClick={() => handleFault('overload')}
          className="px-4 py-2 rounded-md bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/20 disabled:opacity-50">
          Trigger Overload Fault
        </button>
        <button disabled={pending} onClick={() => handleFault('short_circuit')}
          className="px-4 py-2 rounded-md bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 disabled:opacity-50">
          Trigger Short Circuit Fault
        </button>
        <button disabled={pending} onClick={handleClear}
          className="px-4 py-2 rounded-md bg-green-500/10 text-green-400 border border-green-500/30 hover:bg-green-500/20 disabled:opacity-50">
          Clear Fault
        </button>
      </div>

      <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-[#2a2e3a]">
              <th className="p-3">Time</th>
              <th className="p-3">Severity</th>
              <th className="p-3">ANSI</th>
              <th className="p-3">Description</th>
              <th className="p-3">Value</th>
            </tr>
          </thead>
          <tbody>
            {alarms.length === 0 ? (
              <tr><td colSpan={5} className="p-4 text-gray-500">No active alarms or trips.</td></tr>
            ) : (
              alarms.map((a, i) => (
                <tr key={i} className="border-b border-[#1f2330]">
                  <td className="p-3 text-gray-400">{a.timestamp}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${a.severity === 'TRIP' ? 'bg-red-500/10 text-red-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="p-3 text-gray-300">{a.ansi_code}</td>
                  <td className="p-3 text-gray-300">{a.description}</td>
                  <td className="p-3 text-gray-300">{a.value} {a.unit}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}