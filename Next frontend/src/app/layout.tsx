// import '../styles/globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Student Certificate Portal',
  description: 'A portal for students to view and download degree certificates.',
  icons: {
    icon: 'https://i.ibb.co/Z6NdKVws/dominic-kurniawan-suryaputra-r0-U2y0-Hhd-GE-unsplash.jpg',
  },
  themeColor: '#1e40af',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: "auto" }}>{children}</body>
    </html>
  );
}
