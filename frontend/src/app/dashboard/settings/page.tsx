'use client';

export default function SettingsPage() {
  return (
    <div className="p-6 space-y-5 max-w-2xl">
      <div>
        <h2 className="text-lg font-bold text-display">Settings</h2>
        <p className="text-xs text-slate-500">Configure API endpoints, update frequency, and display preferences</p>
      </div>

      {/* API Configuration */}
      <div className="glass-card p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200">🔧 API Configuration</h3>
        {[
          { label: 'Backend API URL', value: 'http://localhost:8000', type: 'text' },
          { label: 'Data Refresh Interval (seconds)', value: '60', type: 'number' },
          { label: 'Map Tile Layer', value: 'Dark (CartoDB)', type: 'select' },
        ].map((setting) => (
          <div key={setting.label}>
            <label className="text-xs text-slate-400 block mb-1">{setting.label}</label>
            <input
              type={setting.type}
              defaultValue={setting.value}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors font-mono"
            />
          </div>
        ))}
        <button className="btn-primary text-xs px-4 py-2">Save Configuration</button>
      </div>

      {/* Data Sources */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">🛰️ Data Source Mode</h3>
        <div className="space-y-3">
          {[
            { id: 'mock', label: 'Mock Data (Synthetic)', desc: 'Scientifically calibrated synthetic data — good for development and demos', active: true },
            { id: 'netcdf', label: 'NetCDF Files (IMD)', desc: 'Real IMD NetCDF data files — set data_path in IMDDataLoader', active: false },
            { id: 'api', label: 'IMD API (Live)', desc: 'Direct IMD API connection — requires API key', active: false },
          ].map((mode) => (
            <label key={mode.id} className="flex items-start gap-3 cursor-pointer p-3 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
              <input type="radio" name="data_mode" defaultChecked={mode.active} className="mt-0.5 accent-cyan-400" />
              <div>
                <p className="text-xs font-semibold text-slate-200">{mode.label}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">{mode.desc}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* System Info */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">ℹ️ System Information</h3>
        <div className="space-y-2 text-[11px]">
          {[
            { label: 'ClimateTwin Version', value: '1.0.0-poc' },
            { label: 'Frontend', value: 'Next.js 14 + Tailwind CSS' },
            { label: 'Backend', value: 'FastAPI + Async SQLAlchemy' },
            { label: 'Database', value: 'PostgreSQL + PostGIS' },
            { label: 'AI Framework', value: 'PyTorch + scikit-learn' },
            { label: 'Geospatial', value: 'React Leaflet + OpenStreetMap' },
            { label: 'Charts', value: 'Recharts' },
            { label: 'Hackathon', value: 'ISRO Bharatiya Antariksh Hackathon 2024' },
          ].map(([label, value]) => (
            <div key={label as string} className="flex justify-between">
              <span className="text-slate-400">{label}</span>
              <span className="font-mono text-cyan-400">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
