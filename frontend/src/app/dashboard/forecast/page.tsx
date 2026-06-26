'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine, Area, AreaChart, Legend,
} from 'recharts';
import { api, type ForecastPoint } from '@/lib/api';
import { formatTemp, formatRain, formatDate } from '@/lib/constants';

const REGIONS = [
  { id: 12, name: 'Kerala' }, { id: 29, name: 'Delhi' }, { id: 14, name: 'Maharashtra' },
  { id: 21, name: 'Rajasthan' }, { id: 23, name: 'Tamil Nadu' }, { id: 3, name: 'Assam' },
  { id: 28, name: 'West Bengal' }, { id: 26, name: 'Uttar Pradesh' }, { id: 11, name: 'Karnataka' },
];

const HORIZONS = [1, 3, 7];

export default function ForecastPage() {
  const [regionId, setRegionId] = useState(12);
  const [horizon, setHorizon] = useState(7);
  const [forecast, setForecast] = useState<{ forecasts: ForecastPoint[]; region_name: string; model_name: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeVar, setActiveVar] = useState<'temperature' | 'rainfall'>('temperature');

  const fetchForecast = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getForecast(regionId, horizon);
      setForecast(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [regionId, horizon]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  const chartData = forecast?.forecasts.map((f) => ({
    date: new Date(f.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    temp_max: f.temperature_max,
    temp_min: f.temperature_min,
    temp_mean: f.temperature_mean,
    rainfall: f.rainfall,
    confidence: f.confidence ? f.confidence * 100 : 80,
    ci_upper: f.ci_upper,
    ci_lower: f.ci_lower,
  })) ?? [];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="glass-card p-3 text-xs border border-cyan-500/20">
        <p className="text-cyan-400 font-bold mb-2">{label}</p>
        {payload.map((entry: any) => (
          <div key={entry.name} className="flex justify-between gap-4">
            <span style={{ color: entry.color }}>{entry.name}</span>
            <span className="font-mono font-bold">{entry.value?.toFixed(1)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-display">Climate Forecast</h2>
          <p className="text-xs text-slate-500">AI-generated forecasts · LSTM + Random Forest ensemble</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 glass-card px-3 py-2">
          <span>🤖</span>
          <span>{forecast?.model_name || 'ClimateTwin-LSTM-v1.0'}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4">
        <div className="glass-card p-3 flex items-center gap-3">
          <span className="text-xs text-slate-400">Region:</span>
          <select
            value={regionId}
            onChange={(e) => setRegionId(Number(e.target.value))}
            className="bg-transparent text-sm text-slate-200 outline-none cursor-pointer"
          >
            {REGIONS.map((r) => (
              <option key={r.id} value={r.id} className="bg-slate-900">
                {r.name}
              </option>
            ))}
          </select>
        </div>

        <div className="glass-card p-3 flex items-center gap-2">
          <span className="text-xs text-slate-400">Horizon:</span>
          {HORIZONS.map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                horizon === h
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {h}D
            </button>
          ))}
        </div>

        <div className="glass-card p-3 flex items-center gap-2">
          {(['temperature', 'rainfall'] as const).map((v) => (
            <button
              key={v}
              onClick={() => setActiveVar(v)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                activeVar === v
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {v === 'temperature' ? '🌡️ Temperature' : '🌧️ Rainfall'}
            </button>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid xl:grid-cols-2 gap-5">
        {/* Main Forecast Chart */}
        <div className="glass-card p-5 xl:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200">
              {forecast?.region_name ?? '—'} — {horizon}-Day{' '}
              {activeVar === 'temperature' ? 'Temperature' : 'Rainfall'} Forecast
            </h3>
            {loading && <div className="w-4 h-4 border border-cyan-400 border-t-transparent rounded-full animate-spin" />}
          </div>

          {loading ? (
            <div className="h-64 skeleton rounded-lg" />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              {activeVar === 'temperature' ? (
                <AreaChart data={chartData} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} unit="°C" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                  <Area type="monotone" dataKey="ci_upper" stroke="transparent" fill="#f97316" fillOpacity={0.08} name="CI Upper" />
                  <Area type="monotone" dataKey="ci_lower" stroke="transparent" fill="#f97316" fillOpacity={0.08} name="CI Lower" />
                  <Line type="monotone" dataKey="temp_max" stroke="#ef4444" strokeWidth={2} dot={false} name="Max Temp" />
                  <Line type="monotone" dataKey="temp_mean" stroke="#f97316" strokeWidth={2.5} dot={{ fill: '#f97316', r: 4 }} name="Mean Temp" />
                  <Line type="monotone" dataKey="temp_min" stroke="#60a5fa" strokeWidth={2} dot={false} name="Min Temp" />
                </AreaChart>
              ) : (
                <AreaChart data={chartData} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="rainGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} unit="mm" />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="rainfall" stroke="#3b82f6" fill="url(#rainGrad)" strokeWidth={2} name="Rainfall (mm)" />
                </AreaChart>
              )}
            </ResponsiveContainer>
          )}
        </div>

        {/* Daily Forecast Cards */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">📅 Day-by-Day Forecast</h3>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {loading
              ? Array.from({ length: 7 }).map((_, i) => <div key={i} className="h-12 skeleton rounded-lg" />)
              : forecast?.forecasts.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-lg border border-white/5 hover:bg-white/[0.02]"
                  >
                    <div className="w-20 text-[11px] text-slate-400">
                      {new Date(f.date).toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short' })}
                    </div>
                    <div className="flex-1 grid grid-cols-3 gap-2 text-[11px]">
                      <div>
                        <span className="text-slate-500">Temp</span>
                        <p className="text-orange-400 font-mono font-bold">{formatTemp(f.temperature_mean)}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Rain</span>
                        <p className="text-blue-400 font-mono font-bold">{formatRain(f.rainfall)}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Conf.</span>
                        <p className="text-green-400 font-mono font-bold">
                          {f.confidence ? `${(f.confidence * 100).toFixed(0)}%` : '—'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
          </div>
        </div>

        {/* Confidence Chart */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">📈 Prediction Confidence</h3>
          {loading ? (
            <div className="h-56 skeleton rounded-lg" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={chartData} margin={{ top: 5, right: 20, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} unit="%" />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={80} stroke="#22c55e" strokeDasharray="4 4" strokeOpacity={0.4} />
                <Area
                  type="monotone"
                  dataKey="confidence"
                  stroke="#22c55e"
                  fill="url(#confGrad)"
                  strokeWidth={2}
                  name="Confidence %"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
          <p className="text-[10px] text-slate-600 mt-2">
            Confidence decreases with forecast horizon — LSTM uncertainty estimation
          </p>
        </div>
      </div>
    </div>
  );
}
