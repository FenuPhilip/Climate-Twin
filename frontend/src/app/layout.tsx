import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ClimateTwin India — AI-Powered Digital Twin of India\'s Climate',
  description:
    'ISRO-aligned AI-powered Digital Twin platform for real-time monitoring, prediction, and simulation of India\'s climate system. Integrates IMD, INSAT, and MOSDAC data.',
  keywords: ['India climate', 'digital twin', 'ISRO', 'AI weather prediction', 'climate simulation', 'IMD', 'INSAT'],
  authors: [{ name: 'ClimateTwin India Research Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'ClimateTwin India',
    description: 'AI-Powered Digital Twin of India\'s Climate System',
    type: 'website',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#030712',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#030712] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
