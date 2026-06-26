'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDatasetCatalog()
      .then((d) => setDatasets(d.datasets || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-5">
      <div>
        <h2 className="text-lg font-bold text-display">Dataset Catalog</h2>
        <p className="text-xs text-slate-500">National climate data sources integrated with ClimateTwin India</p>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="glass-card h-48 skeleton" />
            ))
          : datasets.map((ds) => (
              <div key={ds.id} className="glass-card p-5 hover:scale-[1.01] transition-transform">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-sm font-bold text-slate-200">{ds.name}</p>
                    <p className="text-[10px] text-cyan-400 font-mono mt-0.5">{ds.source_agency}</p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className={`w-2 h-2 rounded-full ${ds.is_active ? 'bg-green-400' : 'bg-slate-500'}`} />
                    <span className="text-[9px] text-slate-500">{ds.is_active ? 'Active' : 'Inactive'}</span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-400 leading-relaxed mb-3">{ds.description}</p>

                <div className="grid grid-cols-2 gap-2 text-[10px] mb-3">
                  <div>
                    <span className="text-slate-500">Format</span>
                    <p className="text-slate-300 font-mono">{ds.format}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Update Freq.</span>
                    <p className="text-slate-300 font-mono">{ds.update_frequency}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Coverage</span>
                    <p className="text-slate-300">{ds.spatial_coverage}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Records</span>
                    <p className="text-slate-300 font-mono">{ds.total_records?.toLocaleString() || '—'}</p>
                  </div>
                </div>

                {ds.last_update && (
                  <p className="text-[9px] text-slate-600">
                    Last updated: {new Date(ds.last_update).toLocaleDateString('en-IN')}
                  </p>
                )}

                {ds.url && (
                  <a
                    href={ds.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    View Source ↗
                  </a>
                )}
              </div>
            ))}
      </div>

      {/* Architecture Note */}
      <div className="glass-card p-5 border-cyan-500/10">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">🔌 Data Integration Architecture</h3>
        <div className="grid md:grid-cols-3 gap-4 text-[11px] text-slate-400">
          <div>
            <p className="font-semibold text-cyan-400 mb-1">Current Mode</p>
            <p>All datasets use scientifically calibrated synthetic data generators based on real IMD statistical parameters.</p>
          </div>
          <div>
            <p className="font-semibold text-cyan-400 mb-1">NetCDF Plug-in</p>
            <p>Set <code className="text-violet-400">source=&quot;netcdf&quot;</code> in the data loaders and provide the file path to switch to real IMD NetCDF files.</p>
          </div>
          <div>
            <p className="font-semibold text-cyan-400 mb-1">HDF5 / MOSDAC</p>
            <p>INSAT-3D MOSDAC products (3RIMG_*.h5) are read via h5py. Set <code className="text-violet-400">source=&quot;hdf5&quot;</code> in the INSAT loader.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
