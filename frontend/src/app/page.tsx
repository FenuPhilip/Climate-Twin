'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

const PARTICLES = Array.from({ length: 30 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 3 + 1,
  dur: Math.random() * 5 + 4,
  delay: Math.random() * 5,
}));

const STATS = [
  { label: 'States Monitored', value: '30+', icon: '📍' },
  { label: 'Data Sources', value: '5', icon: '🛰️' },
  { label: 'AI Models Active', value: '4', icon: '🤖' },
  { label: 'Predictions/Day', value: '250K+', icon: '⚡' },
];

const FEATURES = [
  {
    icon: '🛰️',
    title: 'National Data Integration',
    desc: 'Ingests IMD, INSAT-3D, and MOSDAC satellite data in real time with automated preprocessing and quality control.',
    color: 'from-cyan-500/20 to-transparent',
  },
  {
    icon: '🤖',
    title: 'AI-Powered Prediction',
    desc: 'LSTM deep learning and Random Forest models trained on 30 years of IMD data, delivering 7-day climate forecasts.',
    color: 'from-violet-500/20 to-transparent',
  },
  {
    icon: '🌐',
    title: 'Living Digital Twin',
    desc: 'A continuously evolving virtual replica of India\'s climate — every state maintains a real-time ClimateState updated by AI.',
    color: 'from-emerald-500/20 to-transparent',
  },
  {
    icon: '🧪',
    title: 'What-if Simulations',
    desc: 'Run IPCC-aligned scenarios (+2°C, extreme monsoon, drought) and instantly visualize cascading effects across the country.',
    color: 'from-orange-500/20 to-transparent',
  },
  {
    icon: '🗺️',
    title: 'GIS Climate Maps',
    desc: 'Interactive Leaflet maps with temperature, rainfall, flood risk, and drought index layers at state and district resolution.',
    color: 'from-blue-500/20 to-transparent',
  },
  {
    icon: '💬',
    title: 'AI Climate Assistant',
    desc: 'Natural language interface for querying climate data, interpreting predictions, and generating risk advisories.',
    color: 'from-pink-500/20 to-transparent',
  },
];

export default function LandingPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 relative overflow-hidden">
      {/* Animated particle background */}
      {mounted && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {PARTICLES.map((p) => (
            <div
              key={p.id}
              className="absolute rounded-full bg-cyan-400 opacity-20"
              style={{
                left: `${p.x}%`,
                top: `${p.y}%`,
                width: p.size,
                height: p.size,
                animation: `float ${p.dur}s ease-in-out ${p.delay}s infinite alternate`,
              }}
            />
          ))}
        </div>
      )}

      <style jsx global>{`
        @keyframes float {
          from { transform: translateY(0px) translateX(0px); opacity: 0.1; }
          to   { transform: translateY(-30px) translateX(10px); opacity: 0.4; }
        }
        @keyframes gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50%       { background-position: 100% 50%; }
        }
      `}</style>

      {/* Hero */}
      <section className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6 text-center">
        {/* ISRO Badge */}
        <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-sm font-mono">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          ISRO Bharatiya Antariksh Hackathon · Proof of Concept
        </div>

        {/* Main Title */}
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-black mb-6 leading-tight">
          <span className="block text-slate-100">AI-Powered</span>
          <span
            className="block"
            style={{
              background: 'linear-gradient(135deg, #00D4FF 0%, #6C63FF 50%, #FF6B35 100%)',
              backgroundSize: '200% 200%',
              animation: 'gradient-shift 4s ease infinite',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Digital Twin
          </span>
          <span className="block text-slate-200">of India&apos;s Climate</span>
        </h1>

        <p className="max-w-2xl text-slate-400 text-lg mb-8 leading-relaxed">
          A continuously evolving virtual replica of India&apos;s climate system — integrating IMD,
          INSAT, and MOSDAC data with deep learning AI to predict, simulate, and visualize
          climate conditions across all 30 states in real time.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap gap-4 justify-center mb-16">
          <button
            onClick={() => router.push('/dashboard')}
            className="btn-primary text-base px-8 py-3 rounded-xl font-semibold"
          >
            🚀 Launch Mission Control
          </button>
          <button
            onClick={() => router.push('/dashboard/map')}
            className="btn-ghost text-base px-8 py-3 rounded-xl font-semibold"
          >
            🗺️ View Climate Map
          </button>
        </div>

        {/* Stats Row */}
        <div className="flex flex-wrap justify-center gap-6 mb-8">
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="glass-card px-6 py-4 text-center min-w-[120px]"
            >
              <div className="text-2xl mb-1">{stat.icon}</div>
              <div className="text-xl font-bold text-cyan-400 font-mono">{stat.value}</div>
              <div className="text-[11px] text-slate-500">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Scroll indicator */}
        <div className="animate-bounce text-slate-600 text-2xl">↓</div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-display">
              Platform Capabilities
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Built on clean architecture. Every module is independently swappable — plug in real
              data sources without redesigning the system.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className={`glass-card p-6 bg-gradient-to-br ${feature.color} group hover:scale-[1.02] transition-transform`}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-base font-bold text-slate-100 mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Diagram */}
      <section className="relative z-10 py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass-card p-8 text-center">
            <h2 className="text-xl font-bold mb-8 text-display text-cyan-400">
              System Architecture
            </h2>
            <div className="grid grid-cols-3 gap-4 text-sm">
              {['IMD', 'INSAT-3D', 'MOSDAC'].map((src) => (
                <div key={src} className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="text-xs text-slate-400 mb-1">Data Source</div>
                  <div className="font-bold text-cyan-400">{src}</div>
                </div>
              ))}
            </div>
            <div className="my-4 text-slate-600">↓ Data Collection · Preprocessing · Fusion</div>
            <div className="bg-gradient-to-r from-cyan-900/30 to-violet-900/30 border border-cyan-500/20 rounded-xl p-4 mb-4">
              <div className="text-lg font-bold text-cyan-300 font-display">
                🌐 Climate Digital Twin Engine
              </div>
              <div className="text-xs text-slate-400 mt-1">
                30 Regional ClimateStates · Continuous Updates · AI Predictions
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              {['AI Prediction', 'What-if Simulation', 'Historical Replay'].map((mod) => (
                <div key={mod} className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="font-bold text-slate-300">{mod}</div>
                </div>
              ))}
            </div>
            <div className="my-4 text-slate-600">↓</div>
            <div className="bg-violet-900/20 border border-violet-500/20 rounded-xl p-3">
              <div className="font-bold text-violet-300">🖥️ Interactive GIS Dashboard</div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative z-10 py-20 px-6 text-center">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Ready to explore India&apos;s climate future?
        </h2>
        <p className="text-slate-400 mb-8">
          Launch the mission control dashboard to start monitoring, predicting, and simulating.
        </p>
        <button
          onClick={() => router.push('/dashboard')}
          className="btn-primary text-lg px-10 py-4 rounded-xl"
        >
          🚀 Enter Mission Control
        </button>
        <p className="text-xs text-slate-600 mt-4">
          Demo mode — powered by scientifically calibrated synthetic data
        </p>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-6 px-6 text-center">
        <p className="text-xs text-slate-600">
          ClimateTwin India · AI-Powered Digital Twin of India&apos;s Climate ·{' '}
          <span className="text-cyan-700">ISRO Bharatiya Antariksh Hackathon 2024</span>
        </p>
      </footer>
    </div>
  );
}
