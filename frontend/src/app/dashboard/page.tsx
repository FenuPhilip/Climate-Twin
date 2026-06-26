'use client';

import { useEffect, useState, useCallback } from 'react';
import { api, type IndiaSummary, type RegionState, type Alert } from '@/lib/api';
import { formatTemp, formatRain, formatPct } from '@/lib/constants';

function StatCard({
  label,
  value,
  sub,
  icon,
  color = 'cyan',
}: {
  label: string;
  value: string;
  sub?: string;
  icon: string;
  color?: string;
}) {
  const colorMap: Record<string, string> = {
    cyan: 'text-cyan-400',
    blue: 'text-blue-400',
    orange: 'text-orange-400',
    green: 'text-green-400',
    red: 'text-red-400',
    violet: 'text-violet-400',
  };

  return (
    <div className="glass-card p-5 animate-fade-up">
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider border border-white/10 px-2 py-0.5 rounded-full">
          LIVE
        </span>
      </div>
      <p className={`metric-value text-2xl ${colorMap[color] || 'text-cyan-400'}`}>{value}</p>
      <p className="metric-label mt-1">{label}</p>
      {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
    </div>
  );
}

function AlertBadge({ severity }: { severity: string }) {
  const cls = `badge badge-${severity}`;
  const labels: Record<string, string> = {
    low: 'LOW',
    medium: 'MEDIUM',
    high: 'HIGH',
    extreme: 'EXTREME',
  };
  return <span className={cls}>{labels[severity] || severity.toUpperCase()}</span>;
}

function RegionCard({ state }: { state: RegionState }) {
  const severity = state.anomaly_severity || 'normal';
  return (
    <div className="glass-card p-3 hover:scale-[1.01] transition-transform">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-200">{state.region_name}</span>
        <span className={`badge badge-${severity} text-[9px]`}>{severity.toUpperCase()}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-[10px]">
        <div>
          <span className="text-slate-500">Temp</span>
          <p className="text-orange-400 font-mono font-bold">
            {formatTemp(state.temperature_current ?? state.temperature_mean ?? null)}
          </p>
        </div>
        <div>
          <span className="text-slate-500">Rain</span>
          <p className="text-blue-400 font-mono font-bold">
            {formatRain(state.rainfall_current ?? state.rainfall ?? null)}
          </p>
        </div>
        <div>
          <span className="text-slate-500">Flood</span>
          <p className="text-red-400 font-mono font-bold">{formatPct(state.flood_risk)}</p>
        </div>
        <div>
          <span className="text-slate-500">Confidence</span>
          <p className="text-green-400 font-mono font-bold">
            {formatPct(state.prediction_confidence)}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<IndiaSummary | null>(null);
  const [states, setStates] = useState<RegionState[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchAll = useCallback(async () => {
    try {
      const [summaryData, statesData, alertsData] = await Promise.all([
        api.getIndiaSummary(),
        api.getAllCurrentStates(),
        api.getAlerts(),
      ]);
      setSummary(summaryData);
      setStates(statesData.data || []);
      setAlerts(alertsData.alerts || []);
      setLastUpdate(new Date());
    } catch (e) {
      console.error('Dashboard fetch failed:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 60000); // refresh every 60s
    return () => clearInterval(interval);
  }, [fetchAll]);

  const topStates = states
    .filter((s) => s.anomaly_severity && s.anomaly_severity !== 'normal')
    .slice(0, 12);
  const normalStates = states.filter((s) => !s.anomaly_severity || s.anomaly_severity === 'normal').slice(0, 6);
  const displayStates = [...topStates, ...normalStates].slice(0, 12);

  return (
    <div className="p-6 space-y-6">
      {/* Header Banner */}
      <div className="glass-card p-5 border-cyan-500/20 bg-gradient-to-r from-cyan-950/30 to-violet-950/30">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="status-dot status-live" />
              <span className="text-[10px] font-mono text-green-400 tracking-widest uppercase">
                Digital Twin Active
              </span>
            </div>
            <h2 className="text-xl font-bold text-display text-slate-100">
              India Climate Digital Twin
            </h2>
            <p className="text-sm text-slate-400 mt-0.5">
              Real-time AI-powered virtual replica of India&apos;s climate system
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-[10px] text-slate-500">Data Sources Active</p>
              <p className="font-bold text-cyan-400 font-mono">IMD · INSAT · MOSDAC</p>
            </div>
            <button
              onClick={fetchAll}
              className="btn-primary text-xs px-4 py-2"
            >
              ↻ Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {loading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-5 h-28 skeleton" />
          ))
        ) : (
          <>
            <StatCard
              icon="🌡️"
              label="Avg Temperature"
              value={`${summary?.india_avg_temperature?.toFixed(1) ?? '—'}°C`}
              sub={`Max: ${summary?.india_max_temperature?.toFixed(1) ?? '—'}°C`}
              color="orange"
            />
            <StatCard
              icon="🌧️"
              label="Avg Rainfall"
              value={`${summary?.india_avg_rainfall?.toFixed(1) ?? '—'} mm`}
              sub="Daily mean"
              color="blue"
            />
            <StatCard
              icon="⚠️"
              label="Active Alerts"
              value={String(summary?.active_alerts ?? alerts.length)}
              sub="Across India"
              color="red"
            />
            <StatCard
              icon="🔬"
              label="Regions Monitored"
              value={String(summary?.total_regions_monitored ?? 30)}
              sub="States + UTs"
              color="green"
            />
            <StatCard
              icon="🤖"
              label="Predictions Today"
              value={String(summary?.predictions_made_today ?? '—')}
              sub="LSTM + RF models"
              color="violet"
            />
            <StatCard
              icon="⏱️"
              label="Data Freshness"
              value={`${summary?.data_freshness_minutes ?? '—'} min`}
              sub="Last ingestion"
              color="cyan"
            />
          </>
        )}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left — India Map Teaser + Hotspots */}
        <div className="xl:col-span-2 space-y-4">
          {/* Map CTA */}
          <div className="glass-card p-4 bg-gradient-to-br from-slate-900/50 to-cyan-950/20">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <span>🗺️</span> India Climate Heatmap
              </h3>
              <a href="/dashboard/map" className="text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors">
                Open Full Map →
              </a>
            </div>
            {/* Mini India SVG placeholder with gradient overlay */}
            <div className="relative h-48 rounded-lg overflow-hidden border border-white/5">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-950 via-cyan-950 to-slate-950 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-4xl mb-2">🇮🇳</p>
                  <p className="text-sm text-cyan-400 font-mono">Interactive Map Available</p>
                  <a href="/dashboard/map" className="btn-primary text-xs mt-3 inline-block">
                    Launch GIS Map
                  </a>
                </div>
              </div>
              {/* Animated dots representing regions */}
              {states.slice(0, 15).map((s, i) => (
                <div
                  key={s.region_id}
                  className="absolute w-2 h-2 rounded-full opacity-70"
                  style={{
                    left: `${20 + ((s.centroid_lon - 68) / 30) * 70}%`,
                    top: `${15 + ((37 - s.centroid_lat) / 30) * 75}%`,
                    background: s.flood_risk > 0.5 ? '#FF1744' : s.heatwave_probability > 0.5 ? '#FF6D00' : '#00D4FF',
                    boxShadow: `0 0 6px ${s.flood_risk > 0.5 ? '#FF1744' : '#00D4FF'}`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </div>
            {/* Legend */}
            <div className="flex gap-4 mt-2 text-[10px] text-slate-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block" /> Normal
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-orange-500 inline-block" /> Heatwave Risk
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Flood Risk
              </span>
            </div>
          </div>

          {/* State Grid */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <span>📡</span> Region Status Overview
              <span className="ml-auto text-[10px] text-slate-500 font-normal">
                Updated {lastUpdate.toLocaleTimeString('en-IN')}
              </span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="glass-card p-3 h-24 skeleton" />
                  ))
                : displayStates.map((state) => (
                    <RegionCard key={state.region_id} state={state} />
                  ))}
            </div>
          </div>
        </div>

        {/* Right — Alerts + Quick Actions */}
        <div className="space-y-4">
          {/* Alerts Panel */}
          <div className="glass-card p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
              <span>🚨</span> Active Climate Alerts
              {alerts.length > 0 && (
                <span className="ml-auto bg-red-500/20 text-red-400 text-[10px] px-2 py-0.5 rounded-full border border-red-500/30">
                  {alerts.length}
                </span>
              )}
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {loading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-14 skeleton rounded-lg" />
                ))
              ) : alerts.length === 0 ? (
                <div className="text-center py-6">
                  <p className="text-2xl mb-2">✅</p>
                  <p className="text-xs text-slate-500">No active alerts</p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="p-3 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-xs font-semibold text-slate-200 leading-tight">
                          {alert.alert_type}
                        </p>
                        <p className="text-[10px] text-slate-500 mt-0.5">{alert.region_name}</p>
                      </div>
                      <AlertBadge severity={alert.severity} />
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1.5 line-clamp-2">{alert.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
              <span>⚡</span> Quick Actions
            </h3>
            <div className="space-y-2">
              {[
                { href: '/dashboard/simulation', icon: '🧪', label: 'Run What-if Simulation', color: 'text-violet-400' },
                { href: '/dashboard/forecast', icon: '🔭', label: 'View 7-Day Forecast', color: 'text-cyan-400' },
                { href: '/dashboard/map', icon: '🗺️', label: 'Open Climate Map', color: 'text-blue-400' },
                { href: '/dashboard/assistant', icon: '💬', label: 'Ask AI Assistant', color: 'text-green-400' },
                { href: '/dashboard/analytics', icon: '📊', label: 'Analytics Dashboard', color: 'text-orange-400' },
              ].map((action) => (
                <a
                  key={action.href}
                  href={action.href}
                  className="flex items-center gap-3 p-2.5 rounded-lg border border-white/5 hover:border-white/10 hover:bg-white/[0.03] transition-all group"
                >
                  <span className="text-base">{action.icon}</span>
                  <span className={`text-xs font-medium ${action.color} group-hover:underline`}>
                    {action.label}
                  </span>
                  <span className="ml-auto text-slate-600 group-hover:text-slate-400 transition-colors">→</span>
                </a>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="glass-card p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
              <span>🔬</span> System Status
            </h3>
            <div className="space-y-2">
              {[
                { label: 'Digital Twin Engine', status: 'online', value: '30 regions' },
                { label: 'LSTM Model', status: 'online', value: 'v1.0' },
                { label: 'Random Forest', status: 'online', value: 'baseline' },
                { label: 'IMD Data Feed', status: summary ? 'online' : 'connecting', value: 'mock' },
                { label: 'INSAT Feed', status: 'ready', value: 'plug-in ready' },
              ].map((sys) => (
                <div key={sys.label} className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">{sys.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-slate-500">{sys.value}</span>
                    <div
                      className={`w-1.5 h-1.5 rounded-full ${
                        sys.status === 'online'
                          ? 'bg-green-400'
                          : sys.status === 'ready'
                          ? 'bg-blue-400'
                          : 'bg-yellow-400'
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
