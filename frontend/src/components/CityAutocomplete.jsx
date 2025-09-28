import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function CityAutocomplete({ onSelect }){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  useEffect(() => {
    if(query.length < 2){
      setResults([])
      return
    }
    const timeout = setTimeout(async () => {
      try {
        const r = await axios.get(`http://localhost:8000/api/search_city?q=${encodeURIComponent(query)}`)
        setResults(r.data)
      } catch(e){
        setResults([])
      }
    }, 300)
    return () => clearTimeout(timeout)
  }, [query])

  return (
    <div style={{position:'relative', marginBottom: 12}}>
      <input
        value={query}
        onChange={e=>setQuery(e.target.value)}
        placeholder="Search city…"
        style={{padding:'8px', width:'100%'}}
      />
      {results.length > 0 && (
        <ul style={{
          position:'absolute', background:'#fff', border:'1px solid #ccc',
          width:'100%', listStyle:'none', margin:0, padding:0, maxHeight:200, overflowY:'auto', zIndex: 10
        }}>
          {results.map(c => (
            <li key={c.id}
                style={{padding:'6px', cursor:'pointer'}}
                onClick={() => {onSelect(c); setQuery(c.name); setResults([])}}>
              {c.name}, {c.country} ({Number(c.lat).toFixed(2)}, {Number(c.lon).toFixed(2)})
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}


