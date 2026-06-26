'use client';

import { useState, useCallback, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import { api, type TimeSeriesPoint } from '@/lib/api';

const REGIONS = [
  { id: 12, name: 'Kerala' }, { id: 29, name: 'Delhi' }, { id: 14, name: 'Maharashtra' },
  { id: 21, name: 'Rajasthan' }, { id: 23, name: 'Tamil Nadu' }, { id: 3, name: 'Assam' },
];

const PARAMETERS = [
  { key: 'temperature_mean', label: 'Temperature (Mean)', unit: '°C', color: '#f97316' },
  { key: 'temperature_max', label: 'Temperature (Max)', unit: '°C', color: '#ef4444' },
  { key: 'rainfall', label: 'Rainfall', unit: 'mm', color: '#3b82f6' },
  { key: 'humidity', label: 'Humidity', unit: '%', color: '#06b6d4' },
];

const PERIOD_DAYS = [7, 14, 30, 90, 180, 365];

export default function HistoricalReplayPage() {
  const [regionId, setRegionId] = useState(12);
  const [parameter, setParameter] = useState('temperature_mean');
  const [days, setDays] = useState(30);
  const [data, setData] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [playIdx, setPlayIdx] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getTimeSeries(regionId, parameter, days);
      setData(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [regionId, parameter, days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Replay animation
  useEffect(() => {
    if (!playing) return;
    if (playIdx >= data.length - 1) {
      setPlaying(false);
      return;
    }
    const timer = setTimeout(() => setPlayIdx((i) => i + 1), 80);
    return () => clearTimeout(timer);
  }, [playing, playIdx, data.length]);

  const displayData = playing ? data.slice(0, playIdx + 1) : data;
  const paramConfig = PARAMETERS.find((p) => p.key === parameter);
  const regionName = REGIONS.find((r) => r.id === regionId)?.name ?? '';

  const chartData = displayData.map((d) => ({
    date: new Date(d.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    value: d.value,
  }));

  // Statistics
  const values = data.map((d) => d.value);
  const stats = values.length > 0 ? {
    min: Math.min(...values).toFixed(2),
    max: Math.max(...values).toFixed(2),
    mean: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2),
    std: Math.sqrt(values.reduce((acc, v) => acc + (v - values.reduce((a, b) => a + b, 0) / values.length) ** 2, 0) / values.length).toFixed(2),
  } : null;

  return (
    <div className="p-6 space-y-5">
      <div>
        <h2 className="text-lg font-bold text-display">Historical Climate Replay</h2>
        <p className="text-xs text-slate-500">Replay climate conditions over time with animated visualization</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4">
        <div className="glass-card p-3 flex items-center gap-3">
          <span className="text-xs text-slate-400">Region:</span>
          <select value={regionId} onChange={(e) => setRegionId(Number(e.target.value))}
            className="bg-transparent text-sm text-slate-200 outline-none">
            {REGIONS.map((r) => (
              <option key={r.id} value={r.id} className="bg-slate-900">{r.name}</option>
            ))}
          </select>
        </div>

        <div className="glass-card p-3 flex items-center gap-3">
          <span className="text-xs text-slate-400">Parameter:</span>
          <select value={parameter} onChange={(e) => setParameter(e.target.value)}
            className="bg-transparent text-sm text-slate-200 outline-none">
            {PARAMETERS.map((p) => (
              <option key={p.key} value={p.key} className="bg-slate-900">{p.label}</option>
            ))}
          </select>
        </div>

        <div className="glass-card p-3 flex items-center gap-2">
          <span className="text-xs text-slate-400">Period:</span>
          {PERIOD_DAYS.map((d) => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                days === d ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}>
              {d >= 365 ? '1Y' : d >= 180 ? '6M' : d >= 90 ? '3M' : `${d}D`}
            </button>
          ))}
        </div>

        {/* Playback controls */}
        <div className="glass-card p-3 flex items-center gap-2">
          <button
            onClick={() => { setPlayIdx(0); setPlaying(true); }}
            disabled={loading || data.length === 0}
            className="btn-primary text-xs px-3 py-1.5"
          >
            ▶ Replay
          </button>
          <button
            onClick={() => setPlaying(false)}
            className="btn-ghost text-xs px-3 py-1.5"
          >
            ⏸ Pause
          </button>
          <button
            onClick={() => { setPlaying(false); setPlayIdx(data.length - 1); fetchData(); }}
            className="btn-ghost text-xs px-3 py-1.5"
          >
            ↺ Reset
          </button>
        </div>
      </div>

      {/* Progress bar */}
      {playing && (
        <div className="glass-card p-3 flex items-center gap-3">
          <span className="text-[10px] text-slate-400 font-mono w-24">
            {displayData[displayData.length - 1]
              ? new Date(displayData[displayData.length - 1].timestamp).toLocaleDateString('en-IN')
              : '—'}
          </span>
          <div className="flex-1 bg-white/5 rounded-full h-2">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all"
              style={{ width: `${(playIdx / Math.max(data.length - 1, 1)) * 100}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-400 font-mono w-16 text-right">
            {playIdx + 1}/{data.length}
          </span>
        </div>
      )}

      {/* Main Chart */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-200">
            {regionName} — {paramConfig?.label} ({days} days)
          </h3>
          {loading && <div className="w-4 h-4 border border-cyan-400 border-t-transparent rounded-full animate-spin" />}
        </div>
        {loading ? (
          <div className="h-72 skeleton rounded-lg" />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }}
                tickFormatter={(v, i) => i % Math.ceil(chartData.length / 8) === 0 ? v : ''} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} unit={paramConfig?.unit} />
              <Tooltip
                contentStyle={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8 }}
                labelStyle={{ color: '#00D4FF' }}
                itemStyle={{ color: paramConfig?.color }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={paramConfig?.color ?? '#00D4FF'}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
                name={paramConfig?.label}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Minimum', value: `${stats.min} ${paramConfig?.unit}`, color: 'text-blue-400' },
            { label: 'Maximum', value: `${stats.max} ${paramConfig?.unit}`, color: 'text-red-400' },
            { label: 'Mean', value: `${stats.mean} ${paramConfig?.unit}`, color: 'text-cyan-400' },
            { label: 'Std Dev', value: `${stats.std} ${paramConfig?.unit}`, color: 'text-violet-400' },
          ].map((stat) => (
            <div key={stat.label} className="glass-card p-4">
              <p className="text-[10px] text-slate-500 mb-1">{stat.label}</p>
              <p className={`text-lg font-bold font-mono ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
