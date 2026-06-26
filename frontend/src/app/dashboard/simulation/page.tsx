'use client';

import { useState, useCallback } from 'react';
import { api, type SimulationResult } from '@/lib/api';
import { formatTemp, formatRain, formatPct } from '@/lib/constants';

const PRESETS = [
  { id: 'moderate_warming', name: 'Moderate Warming (+2°C)', icon: '🌡️', color: 'text-orange-400',
    params: { temperature_delta: 2, rainfall_delta_pct: -5 } },
  { id: 'extreme_warming', name: 'Extreme Warming (+4°C)', icon: '🔥', color: 'text-red-400',
    params: { temperature_delta: 4, rainfall_delta_pct: -15 } },
  { id: 'extreme_rainfall', name: 'Extreme Monsoon (+50%)', icon: '🌧️', color: 'text-blue-400',
    params: { temperature_delta: 0.5, rainfall_delta_pct: 50 } },
  { id: 'drought', name: 'Drought Scenario (-60%)', icon: '🏜️', color: 'text-yellow-600',
    params: { temperature_delta: 1.5, rainfall_delta_pct: -60 } },
  { id: 'heatwave', name: 'Heatwave Event (+5°C)', icon: '☀️', color: 'text-orange-600',
    params: { temperature_delta: 5, rainfall_delta_pct: -30, humidity_delta: -30 } },
];

export default function SimulationPage() {
  const [tempDelta, setTempDelta] = useState(0);
  const [rainfallDelta, setRainfallDelta] = useState(0);
  const [humidityDelta, setHumidityDelta] = useState(0);
  const [horizon, setHorizon] = useState(7);
  const [name, setName] = useState('');
  const [results, setResults] = useState<SimulationResult[] | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activePreset, setActivePreset] = useState<string | null>(null);

  const applyPreset = useCallback((preset: typeof PRESETS[0]) => {
    setTempDelta(preset.params.temperature_delta ?? 0);
    setRainfallDelta(preset.params.rainfall_delta_pct ?? 0);
    setHumidityDelta((preset.params as any).humidity_delta ?? 0);
    setName(preset.name);
    setActivePreset(preset.id);
  }, []);

  const runSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.runSimulation({
        temperature_delta: tempDelta,
        rainfall_delta_pct: rainfallDelta,
        humidity_delta: humidityDelta,
        simulation_horizon_days: horizon,
        name: name || 'Custom Scenario',
      });
      setResults(res.results || []);
      setSummary(res.summary);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [tempDelta, rainfallDelta, humidityDelta, horizon, name]);

  function SliderControl({
    label, value, onChange, min, max, step = 0.5, unit, color,
  }: {
    label: string; value: number; onChange: (v: number) => void;
    min: number; max: number; step?: number; unit: string; color: string;
  }) {
    return (
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-xs text-slate-400">{label}</span>
          <span className={`text-sm font-bold font-mono ${color}`}>
            {value > 0 ? '+' : ''}{value}{unit}
          </span>
        </div>
        <input
          type="range"
          min={min} max={max} step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-slate-600">
          <span>{min}{unit}</span>
          <span>0</span>
          <span>+{max}{unit}</span>
        </div>
      </div>
    );
  }

  const highRiskResults = results?.filter(
    (r) => r.flood_risk_new > 0.5 || r.heatwave_probability_new > 0.5
  ) ?? [];

  return (
    <div className="p-6 space-y-5">
      <div>
        <h2 className="text-lg font-bold text-display">What-if Climate Simulator</h2>
        <p className="text-xs text-slate-500">
          Adjust climate parameters and instantly visualize cascading effects across India
        </p>
      </div>

      <div className="grid xl:grid-cols-3 gap-5">
        {/* Left — Controls */}
        <div className="space-y-4">
          {/* Presets */}
          <div className="glass-card p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-3">⚡ Quick Scenarios</h3>
            <div className="space-y-2">
              {PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => applyPreset(preset)}
                  className={`w-full text-left p-3 rounded-lg border transition-all flex items-center gap-3 ${
                    activePreset === preset.id
                      ? 'bg-cyan-500/10 border-cyan-500/30'
                      : 'bg-white/[0.02] border-white/5 hover:border-white/10'
                  }`}
                >
                  <span>{preset.icon}</span>
                  <span className={`text-xs font-medium ${preset.color}`}>{preset.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Sliders */}
          <div className="glass-card p-4 space-y-5">
            <h3 className="text-sm font-semibold text-slate-200">🎛️ Custom Parameters</h3>

            <SliderControl
              label="Temperature Change"
              value={tempDelta}
              onChange={setTempDelta}
              min={-5}
              max={10}
              unit="°C"
              color="text-orange-400"
            />
            <SliderControl
              label="Rainfall Change"
              value={rainfallDelta}
              onChange={setRainfallDelta}
              min={-100}
              max={200}
              step={5}
              unit="%"
              color="text-blue-400"
            />
            <SliderControl
              label="Humidity Change"
              value={humidityDelta}
              onChange={setHumidityDelta}
              min={-50}
              max={50}
              step={2}
              unit="%"
              color="text-cyan-400"
            />

            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">Horizon:</span>
              {[3, 7, 14, 30].map((d) => (
                <button
                  key={d}
                  onClick={() => setHorizon(d)}
                  className={`px-3 py-1 rounded text-xs transition-all ${
                    horizon === d ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {d}D
                </button>
              ))}
            </div>

            <input
              type="text"
              placeholder="Scenario name (optional)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder:text-slate-600 outline-none"
            />

            <button
              onClick={runSimulation}
              disabled={loading}
              className="w-full btn-primary py-3 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Running Simulation...
                </span>
              ) : (
                '🧪 Run Simulation'
              )}
            </button>
          </div>

          {/* Summary */}
          {summary && (
            <div className="glass-card p-4">
              <h3 className="text-sm font-semibold text-slate-200 mb-3">📋 Scenario Summary</h3>
              <div className="space-y-2 text-xs">
                {[
                  { label: 'Regions Affected', value: summary.regions_affected, color: 'text-cyan-400' },
                  { label: 'Avg Temperature', value: `${summary.avg_temperature?.toFixed(1)}°C`, color: 'text-orange-400' },
                  { label: 'Avg Flood Risk', value: formatPct(summary.avg_flood_risk), color: 'text-red-400' },
                  { label: 'Avg Drought Index', value: formatPct(summary.avg_drought_index), color: 'text-yellow-500' },
                  { label: 'Max Heatwave Prob', value: formatPct(summary.max_heatwave_probability), color: 'text-orange-500' },
                ].map((item) => (
                  <div key={item.label} className="flex justify-between">
                    <span className="text-slate-400">{item.label}</span>
                    <span className={`font-mono font-bold ${item.color}`}>{item.value}</span>
                  </div>
                ))}
                {summary.risk_alerts?.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {summary.risk_alerts.map((alert: string, i: number) => (
                      <div key={i} className="text-[10px] text-red-400 bg-red-500/10 border border-red-500/20 rounded px-2 py-1">
                        ⚠️ {alert}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right — Results */}
        <div className="xl:col-span-2 space-y-4">
          {!results ? (
            <div className="glass-card p-12 text-center">
              <p className="text-4xl mb-4">🧪</p>
              <h3 className="text-sm font-semibold text-slate-300 mb-2">Ready to Simulate</h3>
              <p className="text-xs text-slate-500">
                Select a preset scenario or adjust the sliders, then click <strong className="text-cyan-400">Run Simulation</strong>
              </p>
            </div>
          ) : (
            <>
              {/* High Risk Alerts */}
              {highRiskResults.length > 0 && (
                <div className="glass-card p-4 border-red-500/20 bg-red-950/10">
                  <h3 className="text-sm font-semibold text-red-400 mb-3">
                    🚨 High Risk Regions ({highRiskResults.length})
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {highRiskResults.slice(0, 6).map((r) => (
                      <div key={r.region_id} className="text-[11px] bg-red-500/10 border border-red-500/20 rounded-lg p-2">
                        <p className="font-semibold text-slate-200">{r.region_name}</p>
                        <p className="text-red-400">Flood: {formatPct(r.flood_risk_new)}</p>
                        <p className="text-orange-400">Heat: {formatPct(r.heatwave_probability_new)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Results Table */}
              <div className="glass-card overflow-hidden">
                <div className="p-4 border-b border-white/5">
                  <h3 className="text-sm font-semibold text-slate-200">
                    📊 Simulation Results — All Regions
                  </h3>
                </div>
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-[#030712]">
                      <tr className="border-b border-white/5">
                        <th className="text-left p-3 text-slate-400">Region</th>
                        <th className="text-right p-3 text-slate-400">New Temp</th>
                        <th className="text-right p-3 text-slate-400">New Rain</th>
                        <th className="text-right p-3 text-slate-400">Flood Risk</th>
                        <th className="text-right p-3 text-slate-400">Drought</th>
                        <th className="text-right p-3 text-slate-400">Crop Stress</th>
                        <th className="text-right p-3 text-slate-400">Heatwave</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((r, i) => (
                        <tr
                          key={r.region_id}
                          className={`border-b border-white/5 hover:bg-white/[0.02] ${
                            r.flood_risk_new > 0.5 ? 'bg-red-950/10' :
                            r.heatwave_probability_new > 0.5 ? 'bg-orange-950/10' : ''
                          }`}
                        >
                          <td className="p-3 font-medium text-slate-200">{r.region_name}</td>
                          <td className="p-3 text-right font-mono text-orange-400">
                            {formatTemp(r.temperature_new)}
                            <span className={`ml-1 text-[9px] ${tempDelta > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                              {tempDelta > 0 ? `+${tempDelta}` : tempDelta}°
                            </span>
                          </td>
                          <td className="p-3 text-right font-mono text-blue-400">{formatRain(r.rainfall_new)}</td>
                          <td className="p-3 text-right font-mono">
                            <span className={r.flood_risk_new > 0.5 ? 'text-red-400 font-bold' : 'text-slate-300'}>
                              {formatPct(r.flood_risk_new)}
                            </span>
                          </td>
                          <td className="p-3 text-right font-mono text-yellow-500">{formatPct(r.drought_index_new)}</td>
                          <td className="p-3 text-right font-mono text-amber-400">{formatPct(r.crop_stress_index)}</td>
                          <td className="p-3 text-right font-mono">
                            <span className={r.heatwave_probability_new > 0.5 ? 'text-orange-400 font-bold' : 'text-slate-300'}>
                              {formatPct(r.heatwave_probability_new)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
