import React from 'react'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ForecastChart({ results }){
  const data = []
  if(results?.rule) data.push({name: 'Rule', rain: results.rule.tomorrow_rain_mm})
  if(results?.prophet?.predicted_rain_mm !== undefined) data.push({name: 'Prophet', rain: results.prophet.predicted_rain_mm})
  if(results?.xgb?.predicted_rain_mm !== undefined) data.push({name: 'XGBoost', rain: results.xgb.predicted_rain_mm})

  if(data.length === 0) return null
  return (
    <div style={{width:'100%', height: 300, marginTop: 16}}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="rain" stroke="#4CAF50" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
