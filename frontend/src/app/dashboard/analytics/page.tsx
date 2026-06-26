'use client';

import { useEffect, useState } from 'react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts';
import { api } from '@/lib/api';

export default function AnalyticsPage() {
  const [models, setModels] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [compRegionA, setCompRegionA] = useState(12); // Kerala
  const [compRegionB, setCompRegionB] = useState(21); // Rajasthan
  const [compData, setCompData] = useState<any>(null);
  const [compParam, setCompParam] = useState('temperature_mean');

  useEffect(() => {
    Promise.all([api.getModelPerformance(), api.getAnalyticsSummary()])
      .then(([modData, sumData]) => {
        setModels(modData.models || []);
        setSummary(sumData);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    api.compareRegions(compRegionA, compRegionB, compParam, 30)
      .then(setCompData)
      .catch(() => {});
  }, [compRegionA, compRegionB, compParam]);

  const REGIONS = [
    { id: 12, name: 'Kerala' }, { id: 21, name: 'Rajasthan' }, { id: 14, name: 'Maharashtra' },
    { id: 29, name: 'Delhi' }, { id: 23, name: 'Tamil Nadu' }, { id: 3, name: 'Assam' },
  ];

  const modelBarData = models.map((m) => ({
    name: `${m.model_name} (${m.target_variable})`,
    MAE: m.mae,
    RMSE: m.rmse,
    'R²': m.r2_score,
  }));

  const radarData = models.slice(0, 2).map((m) => ({
    model: m.model_name,
    MAE: Math.max(0, 10 - m.mae * 2),
    RMSE: Math.max(0, 10 - m.rmse),
    R2: m.r2_score * 10,
    Skill: (m.skill_score || 0.7) * 10,
    Accuracy: (m.accuracy_pct || 85) / 10,
  }));

  return (
    <div className="p-6 space-y-5">
      <div>
        <h2 className="text-lg font-bold text-display">Analytics</h2>
        <p className="text-xs text-slate-500">Model performance, climate trends, and regional comparisons</p>
      </div>

      {/* Summary KPIs */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Regions Monitored', value: summary.total_regions_monitored || 30, color: 'text-cyan-400', icon: '📍' },
            { label: 'Rainfall Accuracy', value: `${summary.model_accuracy_rainfall?.toFixed(1) || '—'}%`, color: 'text-green-400', icon: '🎯' },
            { label: 'Temp Accuracy', value: `${summary.model_accuracy_temperature?.toFixed(1) || '—'}%`, color: 'text-orange-400', icon: '🌡️' },
            { label: 'Observations', value: summary.total_observations_processed?.toLocaleString() || '—', color: 'text-violet-400', icon: '📊' },
          ].map((kpi) => (
            <div key={kpi.label} className="glass-card p-4">
              <div className="text-xl mb-2">{kpi.icon}</div>
              <p className={`text-xl font-bold font-mono ${kpi.color}`}>{kpi.value}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">{kpi.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid xl:grid-cols-2 gap-5">
        {/* Model Performance Table */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">🤖 Model Performance</h3>
          {loading ? (
            <div className="h-48 skeleton rounded-lg" />
          ) : (
            <div className="space-y-3">
              {models.map((m) => (
                <div key={`${m.model_name}-${m.target_variable}`}
                  className="p-3 rounded-lg border border-white/5 bg-white/[0.02]">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <p className="text-xs font-bold text-slate-200">{m.model_name}</p>
                      <p className="text-[10px] text-slate-500">{m.target_variable} · {m.training_data}</p>
                    </div>
                    <span className="text-[10px] bg-green-500/10 text-green-400 border border-green-500/20 px-2 py-0.5 rounded-full">
                      Active
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-[11px]">
                    {[
                      { label: 'MAE', value: m.mae?.toFixed(3), color: 'text-cyan-400' },
                      { label: 'RMSE', value: m.rmse?.toFixed(3), color: 'text-violet-400' },
                      { label: 'R²', value: m.r2_score?.toFixed(3), color: 'text-green-400' },
                      { label: 'Samples', value: (m.sample_count / 1000).toFixed(0) + 'K', color: 'text-slate-300' },
                    ].map((metric) => (
                      <div key={metric.label} className="text-center">
                        <p className={`font-mono font-bold ${metric.color}`}>{metric.value}</p>
                        <p className="text-slate-500">{metric.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* RMSE Comparison Chart */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">📈 Model Comparison (MAE/RMSE)</h3>
          {loading ? (
            <div className="h-56 skeleton rounded-lg" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={modelBarData} margin={{ top: 5, right: 10, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 9 }} angle={-20} textAnchor="end" />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8 }}
                  labelStyle={{ color: '#00D4FF' }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="MAE" fill="#00D4FF" opacity={0.8} />
                <Bar dataKey="RMSE" fill="#6C63FF" opacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Region Comparison */}
        <div className="glass-card p-5 xl:col-span-2">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">🔄 Regional Comparison</h3>
          <div className="flex flex-wrap gap-3 mb-4">
            <div className="glass-card p-2 flex items-center gap-2">
              <span className="text-xs text-cyan-400">Region A:</span>
              <select value={compRegionA} onChange={(e) => setCompRegionA(Number(e.target.value))}
                className="bg-transparent text-xs text-slate-200 outline-none">
                {REGIONS.map((r) => <option key={r.id} value={r.id} className="bg-slate-900">{r.name}</option>)}
              </select>
            </div>
            <div className="glass-card p-2 flex items-center gap-2">
              <span className="text-xs text-violet-400">Region B:</span>
              <select value={compRegionB} onChange={(e) => setCompRegionB(Number(e.target.value))}
                className="bg-transparent text-xs text-slate-200 outline-none">
                {REGIONS.map((r) => <option key={r.id} value={r.id} className="bg-slate-900">{r.name}</option>)}
              </select>
            </div>
            <div className="glass-card p-2 flex items-center gap-2">
              <span className="text-xs text-slate-400">Parameter:</span>
              <select value={compParam} onChange={(e) => setCompParam(e.target.value)}
                className="bg-transparent text-xs text-slate-200 outline-none">
                <option value="temperature_mean" className="bg-slate-900">Temperature</option>
                <option value="rainfall" className="bg-slate-900">Rainfall</option>
                <option value="humidity" className="bg-slate-900">Humidity</option>
              </select>
            </div>
          </div>

          {compData && (
            <div className="grid grid-cols-3 gap-4">
              <div className="glass-card p-4 text-center border-cyan-500/20">
                <p className="text-xs text-cyan-400 mb-1">{compData.region_a?.name}</p>
                <p className="text-2xl font-bold font-mono text-cyan-400">{compData.region_a?.mean?.toFixed(2)}</p>
                <p className="text-[10px] text-slate-500 mt-1">30-day mean</p>
              </div>
              <div className="glass-card p-4 text-center">
                <p className="text-xs text-slate-400 mb-1">Difference</p>
                <p className={`text-2xl font-bold font-mono ${compData.delta > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                  {compData.delta > 0 ? '+' : ''}{compData.delta?.toFixed(2)}
                </p>
                <p className={`text-[10px] mt-1 ${compData.delta > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                  {compData.delta_pct > 0 ? '+' : ''}{compData.delta_pct?.toFixed(1)}%
                </p>
              </div>
              <div className="glass-card p-4 text-center border-violet-500/20">
                <p className="text-xs text-violet-400 mb-1">{compData.region_b?.name}</p>
                <p className="text-2xl font-bold font-mono text-violet-400">{compData.region_b?.mean?.toFixed(2)}</p>
                <p className="text-[10px] text-slate-500 mt-1">30-day mean</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
