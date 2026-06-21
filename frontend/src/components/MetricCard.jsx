export default function MetricCard({ label, value, unit }) {
  return (
    <div className="bg-[#161922] border border-[#2a2e3a] rounded-lg p-4 flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-gray-400">{label}</span>
      <span className="text-2xl font-semibold text-gray-100">
        {value} <span className="text-sm text-gray-400">{unit}</span>
      </span>
    </div>
  )
}