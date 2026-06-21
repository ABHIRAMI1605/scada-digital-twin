import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Alarms from './pages/Alarms'
import { LiveDataProvider } from './context/LiveDataContext'

export default function App() {
  return (
    <LiveDataProvider>
      <BrowserRouter>
        <div className="flex">
          <Sidebar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/alarms" element={<Alarms />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </LiveDataProvider>
  )
}