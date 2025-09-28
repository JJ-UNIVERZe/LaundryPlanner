import React, { useEffect, useState } from 'react'
import { predictRule, predictProphet, predictXGB, fetchFeatures } from '../apiClient'
import ForecastChart from './ForecastChart'

export default function ModelCompare({ city }) {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [features, setFeatures] = useState(null)
  const [coords, setCoords] = useState(null)

  useEffect(() => {
    async function go() {
      setLoading(true)
      setError(null)
      try {
        // try to use last computed coords from features if available
        const coordPayload =
          coords || (features?.lat && features?.lon ? { lat: features.lat, lon: features.lon } : null)

        const r1 = await predictRule(city, coordPayload)
        let r2 = { error: 'not available' }
        let r3 = { error: 'not available' }
        try {
          r2 = await predictProphet(city, coordPayload)
        } catch (e) {}
        try {
          r3 = await predictXGB(city, coordPayload)
        } catch (e) {}
        try {
          const f = await fetchFeatures(city, coordPayload)
          setFeatures(f)
          setCoords({ lat: f.lat, lon: f.lon })
        } catch (e) {}
        setResults({ rule: r1, prophet: r2, xgb: r3 })
      } catch (e) {
        setError(e.message || 'Failed to load predictions')
      } finally {
        setLoading(false)
      }
    }
    go()
  }, [city])

  if (loading) return <div className="loading">Loading predictions…</div>
  if (!results) return null

  return (
    <div className="model-compare">
      {/* Laundry tip banner */}
      {results?.rule && (
        <div className="tip-banner">
          {results.rule.safe_to_dry_outside
            ? '🌞 Good weather ahead! Safe to dry clothes outside.'
            : '☔ Rain expected — plan indoor drying!'}
        </div>
      )}

      {/* Feature cards */}
      {features && (
        <div className="feature-grid">
          <div className="feature-card">
            <h4>
              {features.city}
              {features.country ? `, ${features.country}` : ''}
            </h4>
            <div className="feature-row">
              Lat: {features.lat ?? '—'} | Lon: {features.lon ?? '—'}
            </div>
          </div>
          <div className="feature-card">
            Temp (tomorrow mean): {features.features?.temp_mean_tomorrow?.toFixed(2)} °C
          </div>
          <div className="feature-card">
            Humidity (tomorrow mean): {features.features?.humidity_mean_tomorrow?.toFixed(2)}%
          </div>
          <div className="feature-card">
            Wind (tomorrow mean): {features.features?.wind_speed_mean_tomorrow?.toFixed(2)} m/s
          </div>
          <div className="feature-card">
            Rain lag-1 (today): {features.features?.rain_lag_1?.toFixed(2)} mm
          </div>
          <div className="feature-card">
            Day of year (tomorrow): {features.features?.dayofyear_tomorrow}
          </div>
        </div>
      )}

      {/* Prediction cards */}
      <div className="cards">
        <div className="card">
          <h3>Rule-based</h3>
          <p className={results.rule.safe_to_dry_outside ? 'safe' : 'not-safe'}>
            {results.rule.safe_to_dry_outside
              ? '✅ Safe to dry clothes outside tomorrow.'
              : '⚠️ Not safe to dry clothes outside tomorrow (rain expected).'}
          </p>
          <pre>{JSON.stringify(results.rule, null, 2)}</pre>
        </div>
        <div className="card">
          <h3>Prophet</h3>
          <p className={results.prophet.safe_to_dry_outside ? 'safe' : 'not-safe'}>
            {results.prophet.safe_to_dry_outside
              ? '✅ Safe to dry clothes outside tomorrow.'
              : '⚠️ Not safe to dry clothes outside tomorrow (rain expected).'}
          </p>
          <pre>{JSON.stringify(results.prophet, null, 2)}</pre>
        </div>
        <div className="card">
          <h3>XGBoost</h3>
          {results.xgb.error ? (
            <p className="error">XGBoost prediction not available</p>
          ) : (
            <p className={results.xgb.safe_to_dry_outside ? 'safe' : 'not-safe'}>
              {results.xgb.safe_to_dry_outside
                ? '✅ Safe to dry clothes outside tomorrow.'
                : '⚠️ Not safe to dry clothes outside tomorrow (rain expected).'}
            </p>
          )}
          <pre>{JSON.stringify(results.xgb, null, 2)}</pre>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <ForecastChart results={results} />

      {/* Map */}
      {features?.lat && features?.lon && (
        <div className="map-wrapper">
          <iframe
            title="city-map"
            width="100%"
            height="300"
            frameBorder="0"
            scrolling="no"
            src={`https://www.openstreetmap.org/export/embed.html?bbox=${features.lon - 0.2}%2C${
              features.lat - 0.2
            }%2C${features.lon + 0.2}%2C${features.lat + 0.2}&layer=mapnik&marker=${features.lat}%2C${features.lon}`}
          />
          <div style={{ textAlign: 'right' }}>
            <a
              href={`https://www.openstreetmap.org/#map=12/${features.lat}/${features.lon}`}
              target="_blank"
              rel="noreferrer"
            >
              View larger map
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
