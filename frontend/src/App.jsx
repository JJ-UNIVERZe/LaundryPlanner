import React, { useState } from 'react'
import CityForm from './components/CityForm'
import ModelCompare from './components/ModelCompare'
import AdviceBanner from './components/AdviceBanner'
import CityAutocomplete from './components/CityAutocomplete'

export default function App(){
  const [city, setCity] = useState('London')
  const [geoStatus, setGeoStatus] = useState('')

  React.useEffect(() => {
    async function detect(){
      try{
        if(!('geolocation' in navigator)) return
        setGeoStatus('Detecting your location…')
        navigator.geolocation.getCurrentPosition(async (pos)=>{
          try{
            const { latitude, longitude } = pos.coords
            const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`
            const res = await fetch(url, { headers: { 'Accept': 'application/json' } })
            const j = await res.json()
            const a = j.address || {}
            const resolved = a.city || a.town || a.village || a.county || a.state || a.municipality
            if(resolved){ setCity(resolved) }
            setGeoStatus('')
          } catch(e){ setGeoStatus('') }
        }, ()=> setGeoStatus(''))
      } catch(e){ setGeoStatus('') }
    }
    detect()
  }, [])
  return (
    <div className="container">
      <h1>Laundry Planner Pro</h1>
      <CityAutocomplete onSelect={(c)=> setCity(c.name)} />
      <CityForm city={city} setCity={setCity} geoStatus={geoStatus} />
      <AdviceBanner city={city} />
      <ModelCompare city={city} />
      <footer style={{marginTop: 20}}>
        Backend: FastAPI | Models: Rule / Prophet / XGBoost / LSTM (optional)
      </footer>
    </div>
  )
}
