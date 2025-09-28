import React, { useState } from 'react'

export default function CityForm({ city, setCity }){
  const [val, setVal] = useState(city)
  function submit(e){
    e.preventDefault()
    setCity(val)
  }
  return (
    <form onSubmit={submit} className="city-form">
      <input value={val} onChange={e=>setVal(e.target.value)} placeholder="Enter city name" />
      <button type="submit">Set city</button>
    </form>
  )
}
