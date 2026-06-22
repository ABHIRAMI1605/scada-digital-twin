import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({ baseURL: API_URL })

export const getReadingHistory = (limit = 60) => api.get(`/readings/history?limit=${limit}`)
export const injectFault = (faultType) => api.post('/fault/inject', { fault_type: faultType })
export const clearFault = () => api.post('/fault/clear')
export const getAlarms = (limit = 50) => api.get(`/alarms?limit=${limit}`)
export const getStatus = () => api.get('/status')

export default api