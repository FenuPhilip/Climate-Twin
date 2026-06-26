'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const NAV_ITEMS = [
  { href: '/dashboard', icon: '⚡', label: 'Dashboard' },
  { href: '/dashboard/live', icon: '📡', label: 'Live Climate' },
  { href: '/dashboard/map', icon: '🗺️', label: 'GIS Map' },
  { href: '/dashboard/forecast', icon: '🔭', label: 'Forecast' },
  { href: '/dashboard/replay', icon: '⏪', label: 'Historical Replay' },
  { href: '/dashboard/simulation', icon: '🧪', label: 'What-if Simulator' },
  { href: '/dashboard/ai-predictions', icon: '🤖', label: 'AI Predictions' },
  { href: '/dashboard/analytics', icon: '📊', label: 'Analytics' },
  { href: '/dashboard/assistant', icon: '💬', label: 'AI Assistant' },
  { href: '/dashboard/datasets', icon: '🗄️', label: 'Datasets' },
  { href: '/dashboard/settings', icon: '⚙️', label: 'Settings' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`sidebar flex flex-col h-screen sticky top-0 transition-all duration-300 z-50
        ${collapsed ? 'w-16' : 'w-60'}`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/5">
        <div className="relative flex-shrink-0">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-600 flex items-center justify-center text-sm font-bold font-mono">
            CT
          </div>
          <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-green-400 border-2 border-[#030712]">
            <div className="w-full h-full rounded-full bg-green-400 animate-ping opacity-75" />
          </div>
        </div>
        {!collapsed && (
          <div>
            <p className="text-xs font-bold text-cyan-400 font-mono tracking-widest uppercase">
              ClimateTwin
            </p>
            <p className="text-[10px] text-slate-500 tracking-wider">India Digital Twin</p>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="ml-auto text-slate-500 hover:text-slate-300 transition-colors text-xs"
          aria-label="Toggle sidebar"
        >
          {collapsed ? '▶' : '◀'}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {!collapsed && (
          <p className="text-[10px] text-slate-600 uppercase tracking-widest px-2 py-2">
            Mission Control
          </p>
        )}
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${isActive ? 'active' : ''} ${collapsed ? 'justify-center px-0' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <span className="text-base flex-shrink-0">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
              {!collapsed && isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/5 p-3">
        {!collapsed ? (
          <div className="flex items-center gap-2 px-2">
            <div className="status-dot status-live" />
            <div>
              <p className="text-[10px] text-slate-400 font-mono">SYSTEM ONLINE</p>
              <p className="text-[9px] text-slate-600">v1.0.0 — ISRO POC</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="status-dot status-live" />
          </div>
        )}
      </div>
    </aside>
  );
}
