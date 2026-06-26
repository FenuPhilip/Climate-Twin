import Sidebar from '@/components/layout/Sidebar';
import TopBar from '@/components/layout/TopBar';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Mission Dashboard',
  '/dashboard/live': 'Live Climate Monitor',
  '/dashboard/map': 'GIS Climate Map',
  '/dashboard/forecast': 'Climate Forecast',
  '/dashboard/replay': 'Historical Replay',
  '/dashboard/simulation': 'What-if Simulator',
  '/dashboard/ai-predictions': 'AI Predictions',
  '/dashboard/analytics': 'Analytics',
  '/dashboard/assistant': 'AI Climate Assistant',
  '/dashboard/datasets': 'Dataset Catalog',
  '/dashboard/settings': 'Settings',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar title="Mission Dashboard" />
        <main className="flex-1 overflow-y-auto">
          <div className="relative z-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
