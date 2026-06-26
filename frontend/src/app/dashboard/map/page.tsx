'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { api, type RegionState } from '@/lib/api';
import { LAYER_CONFIGS, getColorForValue, formatTemp, formatRain, formatPct } from '@/lib/constants';

// Dynamic import for Leaflet (SSR-incompatible)
let L: typeof import('leaflet') | null = null;

const INDIA_BOUNDS: [[number, number], [number, number]] = [[6.0, 67.0], [37.5, 98.0]];
const INDIA_CENTER: [number, number] = [22.5, 82.0];

type LayerKey = keyof typeof LAYER_CONFIGS;

export default function GISMapPage() {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  const [states, setStates] = useState<RegionState[]>([]);
  const [activeLayer, setActiveLayer] = useState<LayerKey>('temperature');
  const [selectedState, setSelectedState] = useState<RegionState | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const data = await api.getTwinMapData();
      setStates(data.features || []);
    } catch {
      const data = await api.getAllCurrentStates();
      setStates(data.data || []);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Initialize Leaflet map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current || mapInstanceRef.current) return;

    import('leaflet').then((leafletModule) => {
      L = leafletModule.default;

      // @ts-ignore
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current!, {
        center: INDIA_CENTER,
        zoom: 5,
        minZoom: 4,
        maxZoom: 12,
        zoomControl: false,
      });

      // Dark tile layer
      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
        {
          attribution: '&copy; OpenStreetMap, CartoDB',
          subdomains: 'abcd',
          maxZoom: 19,
        }
      ).addTo(map);

      // Label layer on top
      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png',
        { attribution: '', subdomains: 'abcd', pane: 'overlayPane' }
      ).addTo(map);

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      mapInstanceRef.current = map;
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when data or layer changes
  useEffect(() => {
    if (!mapInstanceRef.current || !L || states.length === 0) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const config = LAYER_CONFIGS[activeLayer];

    states.forEach((state) => {
      const lat = state.centroid_lat;
      const lon = state.centroid_lon;
      if (!lat || !lon) return;

      const rawValue = config.getValue({ ...state });
      const value = rawValue ?? 0;
      const color = getColorForValue(value, activeLayer);

      const radius = activeLayer === 'rainfall' ? Math.max(8, Math.min(30, value * 3)) : 16;

      const circle = L!.circleMarker([lat, lon], {
        radius,
        fillColor: color,
        fillOpacity: 0.8,
        color: 'rgba(255,255,255,0.3)',
        weight: 1,
      });

      const popup = L!.popup({
        className: 'climate-popup',
        maxWidth: 260,
      }).setContent(`
        <div style="font-family: 'Inter', sans-serif; color: #e2e8f0; min-width: 200px;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #00D4FF;">
            ${state.region_name}
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
            <div>
              <span style="color: #94a3b8;">Temperature</span><br/>
              <strong style="color: #fb923c;">${formatTemp(state.temperature_current ?? state.temperature_mean ?? null)}</strong>
            </div>
            <div>
              <span style="color: #94a3b8;">Rainfall</span><br/>
              <strong style="color: #60a5fa;">${formatRain(state.rainfall_current ?? state.rainfall ?? null)}</strong>
            </div>
            <div>
              <span style="color: #94a3b8;">Flood Risk</span><br/>
              <strong style="color: #f87171;">${formatPct(state.flood_risk)}</strong>
            </div>
            <div>
              <span style="color: #94a3b8;">Heatwave</span><br/>
              <strong style="color: #fb923c;">${formatPct(state.heatwave_probability)}</strong>
            </div>
            <div>
              <span style="color: #94a3b8;">Drought</span><br/>
              <strong style="color: #fbbf24;">${formatPct(state.drought_index)}</strong>
            </div>
            <div>
              <span style="color: #94a3b8;">AI Confidence</span><br/>
              <strong style="color: #4ade80;">${formatPct(state.prediction_confidence)}</strong>
            </div>
          </div>
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 10px; color: #64748b;">
            Sources: IMD · INSAT-3D
          </div>
        </div>
      `);

      circle.bindPopup(popup);
      circle.on('click', () => setSelectedState(state));
      circle.addTo(mapInstanceRef.current);
      markersRef.current.push(circle);
    });
  }, [states, activeLayer]);

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      {/* Controls Bar */}
      <div className="flex items-center gap-4 px-6 py-3 border-b border-white/5 bg-[#030712]/50 backdrop-blur-sm flex-wrap">
        <span className="text-xs text-slate-400 font-medium">Layer:</span>
        {Object.entries(LAYER_CONFIGS).map(([key, conf]) => (
          <button
            key={key}
            onClick={() => setActiveLayer(key as LayerKey)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeLayer === key
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'bg-white/5 text-slate-400 hover:text-slate-200 border border-white/5'
            }`}
          >
            {conf.label}
          </button>
        ))}

        <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
          <span>{loading ? 'Loading...' : `${states.length} regions`}</span>
          <button
            onClick={fetchData}
            className="btn-ghost text-xs px-3 py-1.5"
          >
            ↻
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Map */}
        <div className="flex-1 relative">
          <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
          />
          <div ref={mapRef} className="w-full h-full" />

          {/* Loading overlay */}
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#030712]/80 z-[1000]">
              <div className="text-center">
                <div className="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                <p className="text-sm text-slate-400">Loading climate data...</p>
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="absolute bottom-6 left-6 z-[1000] glass-card p-3">
            <p className="text-[10px] text-slate-400 mb-2 font-medium uppercase tracking-wider">
              {LAYER_CONFIGS[activeLayer].label}
            </p>
            <div className="flex items-center gap-1">
              <span className="text-[9px] text-slate-500">
                {LAYER_CONFIGS[activeLayer].domain[0]}
              </span>
              <div
                className="h-3 w-24 rounded-full"
                style={{
                  background: `linear-gradient(to right, ${LAYER_CONFIGS[activeLayer].colorScale.join(', ')})`,
                }}
              />
              <span className="text-[9px] text-slate-500">
                {LAYER_CONFIGS[activeLayer].domain[1]}
                {LAYER_CONFIGS[activeLayer].unit}
              </span>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        {selectedState && (
          <div className="w-72 border-l border-white/5 bg-[#030712]/95 backdrop-blur-xl p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-cyan-400">{selectedState.region_name}</h3>
              <button
                onClick={() => setSelectedState(null)}
                className="text-slate-500 hover:text-slate-300 text-lg"
              >
                ×
              </button>
            </div>

            {[
              { label: 'Temperature', value: formatTemp(selectedState.temperature_current ?? selectedState.temperature_mean ?? null), color: 'text-orange-400' },
              { label: 'Rainfall', value: formatRain(selectedState.rainfall_current ?? selectedState.rainfall ?? null), color: 'text-blue-400' },
              { label: 'Humidity', value: selectedState.humidity_current ? `${selectedState.humidity_current.toFixed(0)}%` : '—', color: 'text-cyan-400' },
              { label: 'LST', value: selectedState.lst_current ? formatTemp(selectedState.lst_current) : '—', color: 'text-yellow-400' },
              { label: 'SST', value: selectedState.sst_current ? formatTemp(selectedState.sst_current) : '—', color: 'text-blue-300' },
              { label: 'Predicted Temp', value: formatTemp(selectedState.temperature_predicted), color: 'text-violet-400' },
              { label: 'Predicted Rain', value: formatRain(selectedState.rainfall_predicted), color: 'text-indigo-400' },
              { label: 'AI Confidence', value: formatPct(selectedState.prediction_confidence), color: 'text-green-400' },
              { label: 'Flood Risk', value: formatPct(selectedState.flood_risk), color: 'text-red-400' },
              { label: 'Heatwave Risk', value: formatPct(selectedState.heatwave_probability), color: 'text-orange-500' },
              { label: 'Drought Index', value: formatPct(selectedState.drought_index), color: 'text-yellow-500' },
            ].map((item) => (
              <div key={item.label} className="flex justify-between py-2 border-b border-white/5">
                <span className="text-xs text-slate-400">{item.label}</span>
                <span className={`text-xs font-mono font-bold ${item.color}`}>{item.value}</span>
              </div>
            ))}

            <div className="mt-4">
              <p className="text-[10px] text-slate-500 mb-2">Anomaly Severity</p>
              <span className={`badge badge-${selectedState.anomaly_severity || 'normal'}`}>
                {(selectedState.anomaly_severity || 'normal').toUpperCase()}
              </span>
            </div>

            <a
              href={`/dashboard/forecast?region=${selectedState.region_id}`}
              className="mt-4 block btn-primary text-center text-xs py-2"
            >
              View 7-Day Forecast →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
