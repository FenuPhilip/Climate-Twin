'use client';

import { useEffect, useState } from 'react';
import { api, type IndiaSummary } from '@/lib/api';
import { formatDate } from '@/lib/constants';

export default function TopBar({ title }: { title: string }) {
  const [summary, setSummary] = useState<Partial<IndiaSummary>>({});
  const [currentTime, setCurrentTime] = useState(new Date());
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const tick = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    api.health()
      .then(() => setConnected(true))
      .catch(() => setConnected(false));

    api.getIndiaSummary()
      .then(setSummary)
      .catch(() => {});
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl sticky top-0 z-40">
      {/* Left — Page Title */}
      <div>
        <h1 className="text-sm font-bold text-display text-slate-100 tracking-wider">
          {title}
        </h1>
        <p className="text-[10px] text-slate-500 font-mono">
          AI-Powered Digital Twin · India Climate System
        </p>
      </div>

      {/* Center — Live Stats */}
      <div className="hidden md:flex items-center gap-6 text-[11px]">
        <div className="text-center">
          <p className="text-cyan-400 font-mono font-bold">
            {summary.india_avg_temperature?.toFixed(1) ?? '—'}°C
          </p>
          <p className="text-slate-500">Avg Temp</p>
        </div>
        <div className="w-px h-8 bg-white/5" />
        <div className="text-center">
          <p className="text-blue-400 font-mono font-bold">
            {summary.india_avg_rainfall?.toFixed(1) ?? '—'} mm
          </p>
          <p className="text-slate-500">Avg Rainfall</p>
        </div>
        <div className="w-px h-8 bg-white/5" />
        <div className="text-center">
          <p className="text-orange-400 font-mono font-bold">
            {summary.active_alerts ?? '—'}
          </p>
          <p className="text-slate-500">Active Alerts</p>
        </div>
        <div className="w-px h-8 bg-white/5" />
        <div className="text-center">
          <p className="text-green-400 font-mono font-bold">
            {summary.total_regions_monitored ?? 30}
          </p>
          <p className="text-slate-500">Regions</p>
        </div>
      </div>

      {/* Right — Clock & Status */}
      <div className="flex items-center gap-4">
        {/* API Status */}
        <div className="flex items-center gap-2">
          <div className={`status-dot ${connected ? 'status-live' : 'status-danger'}`} />
          <span className="text-[10px] font-mono text-slate-400">
            {connected ? 'API LIVE' : 'OFFLINE'}
          </span>
        </div>

        {/* Clock */}
        <div className="text-right hidden sm:block">
          <p className="text-[11px] font-mono text-slate-300">
            {currentTime.toLocaleTimeString('en-IN', { hour12: false })}
          </p>
          <p className="text-[9px] text-slate-500">
            {currentTime.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
          </p>
        </div>

        {/* IST indicator */}
        <div className="glass-card px-2 py-1">
          <p className="text-[9px] font-mono text-cyan-400 tracking-widest">IST UTC+5:30</p>
        </div>
      </div>
    </header>
  );
}
