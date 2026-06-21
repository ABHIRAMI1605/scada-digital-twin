import { useEffect, useRef } from 'react'
import Plotly from 'plotly.js-dist-min'

const STATUS_COLORS = { normal: '#22c55e', warning: '#eab308', trip: '#ef4444', offline: '#6b7280' }

const NODE_POSITIONS = {
  grid: [0, 2], breaker: [1.7, 2], transformer: [3.4, 2], bus: [5.1, 2],
  motor: [6.8, 3], lighting: [6.8, 2], hvac: [6.8, 1],
}

const EDGES = [
  ['grid', 'breaker'], ['breaker', 'transformer'], ['transformer', 'bus'],
  ['bus', 'motor'], ['bus', 'lighting'], ['bus', 'hvac'],
]

const LABELS = {
  grid: ['GRID<br>11kV', 'grid'], breaker: ['CB-01', 'breaker'],
  transformer: ['T1<br>500kVA', 'transformer'], bus: ['BUS<br>415V', null],
  motor: ['Motor-1<br>75kW', 'motor'], lighting: ['Lighting<br>20kW', 'lighting'],
  hvac: ['HVAC<br>40kW', 'hvac'],
}

function determineSystemState(reading, latestAlarm) {
  const fault = reading?.fault_injected || 'none'
  const state = {
    grid: 'normal', breaker: 'normal', transformer: 'normal', motor: 'normal',
    lighting: 'normal', hvac: 'normal',
    transformerLoadingPct: reading ? Math.round((reading.total_kva / 500) * 1000) / 10 : 0,
  }
  const severity = latestAlarm?.severity
  const code = latestAlarm ? String(latestAlarm.ansi_code) : null

  if (fault === 'short_circuit' && severity === 'TRIP' && code === '50') {
    state.breaker = 'trip'
    state.transformer = state.motor = state.lighting = state.hvac = 'offline'
  } else if (fault === 'overload') {
    if (severity === 'TRIP' && code === '51') state.motor = 'trip'
    else if (severity === 'ALARM' && code === '51') state.motor = 'warning'
    if (state.transformerLoadingPct > 80) state.transformer = 'warning'
  }
  return state
}

function buildTraces(reading, latestAlarm) {
  const state = determineSystemState(reading, latestAlarm)

  const edgeTraces = EDGES.map(([src, dst]) => {
    const [x0, y0] = NODE_POSITIONS[src]
    const [x1, y1] = NODE_POSITIONS[dst]
    const dead = state[dst] === 'offline' || state[src] === 'offline'
    return {
      x: [x0, x1], y: [y0, y1], mode: 'lines', type: 'scatter',
      line: { color: dead ? '#374151' : '#3b82f6', width: 3, dash: dead ? 'dot' : 'solid' },
      hoverinfo: 'skip', showlegend: false,
    }
  })

  const nodeTraces = Object.entries(NODE_POSITIONS).map(([nodeId, [x, y]]) => {
    const [label, stateKey] = LABELS[nodeId]
    const status = stateKey ? (state[stateKey] || 'normal') : 'normal'
    return {
      x: [x], y: [y], mode: 'markers+text', type: 'scatter',
      marker: { size: 42, color: STATUS_COLORS[status], line: { color: 'white', width: 1.5 } },
      text: [label], textposition: 'bottom center',
      textfont: { color: 'white', size: 11 },
      customdata: [[nodeId, status]],
      hovertext: `${label.replace('<br>', ' ')} — ${status.toUpperCase()}`,
      hoverinfo: 'text', showlegend: false,
    }
  })

  return [...edgeTraces, ...nodeTraces]
}

export default function SingleLineDiagram({ reading, latestAlarm, onSelectNode }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (!reading || !containerRef.current) return

    const layout = {
      height: 320,
      margin: { l: 10, r: 10, t: 10, b: 10 },
      plot_bgcolor: '#0f1117', paper_bgcolor: '#0f1117',
      xaxis: { visible: false, range: [-1, 7.5] },
      yaxis: { visible: false, range: [0.5, 3.5], scaleanchor: 'x', scaleratio: 1 },
      showlegend: false,
    }
    const config = { displayModeBar: false, responsive: true }

    Plotly.react(containerRef.current, buildTraces(reading, latestAlarm), layout, config)

    const handleClick = (e) => {
      const point = e.points?.[0]
      if (point?.customdata && onSelectNode) {
        const [nodeId, status] = point.customdata
        onSelectNode(nodeId, status)
      }
    }
    containerRef.current.on('plotly_click', handleClick)

    return () => {
      containerRef.current?.removeAllListeners('plotly_click')
    }
  }, [reading, latestAlarm, onSelectNode])

  useEffect(() => {
    const node = containerRef.current
    return () => { if (node) Plotly.purge(node) }
  }, [])

  if (!reading) return null
  return <div ref={containerRef} style={{ width: '100%', maxWidth: 900, height: 320, margin: '0 auto' }} />
}