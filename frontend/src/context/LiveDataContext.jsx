import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { getReadingHistory } from '../api/client'

const LiveDataContext = createContext(null)
const WS_URL = 'ws://localhost:8000/ws/live'
const HISTORY_SIZE = 60

export function LiveDataProvider({ children }) {
  const [reading, setReading] = useState(null)
  const [history, setHistory] = useState([])
  const [alarms, setAlarms] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    getReadingHistory(HISTORY_SIZE)
      .then((res) => setHistory(res.data))
      .catch(() => {})

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      setReading(payload.reading)
      setHistory((prev) => [...prev, payload.reading].slice(-HISTORY_SIZE))
      if (payload.new_alarms?.length) {
        setAlarms((prev) => [...payload.new_alarms, ...prev].slice(0, 100))
      }
    }

    return () => ws.close()
  }, [])

  return (
    <LiveDataContext.Provider value={{ reading, history, alarms, setAlarms, connected }}>
      {children}
    </LiveDataContext.Provider>
  )
}

export function useLiveData() {
  return useContext(LiveDataContext)
}