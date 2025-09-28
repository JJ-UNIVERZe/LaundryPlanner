import axios from 'axios'

const API = axios.create({ baseURL: 'http://localhost:8000/api' })

export async function predictRule(city, coords){
  const r = await API.post('/predict/rule', { city, ...(coords||{}) })
  return r.data
}
export async function predictProphet(city, coords){
  const r = await API.post('/predict/prophet', { city, ...(coords||{}) })
  return r.data
}
export async function predictXGB(city, coords){
  const r = await API.post('/predict/xgboost', { city, ...(coords||{}) })
  return r.data
}

export async function fetchFeatures(city, coords){
  const r = await API.post('/features', { city, ...(coords||{}) })
  return r.data
}