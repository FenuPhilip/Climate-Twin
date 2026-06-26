'use client';

import { useEffect, useState, useCallback } from 'react';
import { api, type RegionState } from '@/lib/api';
import { formatTemp, formatRain, formatPct } from '@/lib/constants';

export default function LiveClimatePage() {
  const [states, setStates] = useState<RegionState[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'temp' | 'rain' | 'flood'>('name');
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const fetchData = useCallback(async () => {
    try {
      const data = await api.getAllCurrentStates();
      setStates(data.data || []);
      setLastUpdate(new Date());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const filtered = states
    .filter((s) =>
      s.region_name.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'name') return a.region_name.localeCompare(b.region_name);
      if (sortBy === 'temp')
        return (b.temperature_current ?? 0) - (a.temperature_current ?? 0);
      if (sortBy === 'rain')
        return (b.rainfall_current ?? 0) - (a.rainfall_current ?? 0);
      if (sortBy === 'flood') return (b.flood_risk ?? 0) - (a.flood_risk ?? 0);
      return 0;
    });

  function getBar(value: number, max: number, color: string) {
    const pct = Math.min(100, (value / max) * 100);
    return (
      <div className="flex-1 bg-white/5 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-display">Live Climate Monitor</h2>
          <p className="text-xs text-slate-500">
            Real-time climate state across all Indian states · Updated{' '}
            {lastUpdate.toLocaleTimeString('en-IN')}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="status-dot status-live" />
          <span className="text-xs text-green-400 font-mono">LIVE</span>
          <button onClick={fetchData} className="btn-ghost text-xs">↻ Refresh</button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search state..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-slate-200 placeholder:text-slate-500 outline-none focus:border-cyan-500/50 w-56"
        />
        <div className="flex gap-1">
          {(['name', 'temp', 'rain', 'flood'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                sortBy === s
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'bg-white/5 text-slate-400 hover:text-slate-200 border border-white/5'
              }`}
            >
              {s === 'name' ? '🔤 Name' : s === 'temp' ? '🌡️ Temp' : s === 'rain' ? '🌧️ Rain' : '🌊 Flood'}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left p-4 text-xs text-slate-400 font-medium">State</th>
                <th className="text-right p-4 text-xs text-slate-400 font-medium">Temp (°C)</th>
                <th className="text-right p-4 text-xs text-slate-400 font-medium">Rainfall</th>
                <th className="text-right p-4 text-xs text-slate-400 font-medium">Humidity</th>
                <th className="text-right p-4 text-xs text-slate-400 font-medium">LST</th>
                <th className="text-center p-4 text-xs text-slate-400 font-medium w-48">Flood Risk</th>
                <th className="text-center p-4 text-xs text-slate-400 font-medium w-48">Heatwave</th>
                <th className="text-center p-4 text-xs text-slate-400 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 10 }).map((_, i) => (
                    <tr key={i} className="border-b border-white/5">
                      {Array.from({ length: 8 }).map((_, j) => (
                        <td key={j} className="p-4">
                          <div className="h-4 skeleton rounded" />
                        </td>
                      ))}
                    </tr>
                  ))
                : filtered.map((state, i) => (
                    <tr
                      key={state.region_id}
                      className="border-b border-white/5 hover:bg-white/[0.02] transition-colors animate-fade-up"
                      style={{ animationDelay: `${i * 0.02}s` }}
                    >
                      <td className="p-4">
                        <div>
                          <p className="font-medium text-slate-200">{state.region_name}</p>
                          <p className="text-[10px] text-slate-500 font-mono">{state.state_code}</p>
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <span className="font-mono font-bold text-orange-400">
                          {formatTemp(state.temperature_current ?? state.temperature_mean ?? null)}
                        </span>
                        {state.temperature_anomaly != null && (
                          <span className={`ml-1 text-[10px] ${state.temperature_anomaly > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                            {state.temperature_anomaly > 0 ? '+' : ''}{state.temperature_anomaly.toFixed(1)}
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-right font-mono font-bold text-blue-400">
                        {formatRain(state.rainfall_current ?? state.rainfall ?? null)}
                      </td>
                      <td className="p-4 text-right font-mono text-slate-300">
                        {state.humidity_current != null ? `${state.humidity_current.toFixed(0)}%` : '—'}
                      </td>
                      <td className="p-4 text-right font-mono text-slate-400">
                        {state.lst_current != null ? `${state.lst_current.toFixed(1)}°C` : '—'}
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          {getBar(state.flood_risk ?? 0, 1, '#ef4444')}
                          <span className="text-[10px] font-mono text-red-400 w-10 text-right">
                            {formatPct(state.flood_risk)}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          {getBar(state.heatwave_probability ?? 0, 1, '#f97316')}
                          <span className="text-[10px] font-mono text-orange-400 w-10 text-right">
                            {formatPct(state.heatwave_probability)}
                          </span>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <span className={`badge badge-${state.anomaly_severity || 'normal'} text-[9px]`}>
                          {(state.anomaly_severity || 'normal').toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
        {!loading && (
          <div className="p-3 border-t border-white/5 text-xs text-slate-500 flex justify-between">
            <span>Showing {filtered.length} of {states.length} regions</span>
            <span className="font-mono">Source: IMD · INSAT-3D · MOSDAC</span>
          </div>
        )}
      </div>
    </div>
  );
}
