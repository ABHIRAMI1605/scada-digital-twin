import { useState } from 'react'
import { useLiveData } from '../context/LiveDataContext'
import MetricCard from '../components/MetricCard'
import SingleLineDiagram from '../components/SingleLineDiagram'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const { reading, history, alarms, connected } = useLiveData()
  const [selected, setSelected] = useState(null)
  const latestAlarm = alarms[0] || null

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-100">Plant Overview</h2>
        <span className={`text-sm px-3 py-1 rounded-full ${connected ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
          {connected ? 'LIVE' : 'DISCONNECTED'}
        </span>
      </div>

      {!reading ? (
        <p className="text-gray-400">Waiting for data...</p>
      ) : (
        <>
          <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg p-4 mb-6">
            <h3 className="text-sm text-gray-400 mb-2">Single-Line Diagram</h3>
            <SingleLineDiagram
              reading={reading}
              latestAlarm={latestAlarm}
              onSelectNode={(nodeId, status) => setSelected({ nodeId, status })}
            />
            {selected && (
              <p className="text-sm text-gray-300 mt-2">
                Selected: <span className="font-semibold">{selected.nodeId.toUpperCase()}</span> — status: {selected.status.toUpperCase()}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <MetricCard label="Bus Voltage" value={reading.bus_voltage_v} unit="V" />
            <MetricCard label="Active Power" value={reading.total_kw} unit="kW" />
            <MetricCard label="Reactive Power" value={reading.total_kvar} unit="kVAR" />
            <MetricCard label="Power Factor" value={reading.power_factor} unit="" />
            <MetricCard label="Current" value={reading.current_a} unit="A" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg p-4">
              <h3 className="text-sm text-gray-400 mb-2">Bus Voltage Trend</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={history}>
                  <CartesianGrid stroke="#2a2e3a" strokeDasharray="3 3" />
                  <XAxis dataKey="sim_time_s" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ backgroundColor: '#161922', border: '1px solid #2a2e3a' }} />
                  <Line type="monotone" dataKey="bus_voltage_v" stroke="#3b82f6" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg p-4">
              <h3 className="text-sm text-gray-400 mb-2">Real vs Reactive Power</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={history}>
                  <CartesianGrid stroke="#2a2e3a" strokeDasharray="3 3" />
                  <XAxis dataKey="sim_time_s" stroke="#6b7280" fontSize={12} />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#161922', border: '1px solid #2a2e3a' }} />
                  <Line type="monotone" dataKey="total_kw" stroke="#22c55e" dot={false} strokeWidth={2} name="kW" />
                  <Line type="monotone" dataKey="total_kvar" stroke="#eab308" dot={false} strokeWidth={2} name="kVAR" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  )
}