import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google"; // Keep fonts if needed or remove if not used. Checking page.tsx, it uses sans.
import Link from "next/link";
import { Scale } from "lucide-react";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Anayasa AI",
  description: "Yapay Zeka Destekli Anayasa Asistanı",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-[#E0E0E0] flex flex-col font-sans text-gray-800`}
      >
        {/* Global Header */}
        <header className="bg-[#D32F2F] text-white py-4 px-8 flex justify-between items-center shadow-md">
          <Link href="/" className="flex items-center space-x-2 hover:opacity-90 transition">
            <Scale size={32} className="text-yellow-400" />
            <span className="text-xl font-bold tracking-wide">Anayasa AI</span>
          </Link>
          <nav className="space-x-6 text-sm font-medium hidden md:block">
            <Link href="/hakkinda" className="hover:text-gray-200 transition">Hakkında</Link>
            <Link href="/ozellikler" className="hover:text-gray-200 transition">Özellikler</Link>
            <Link href="/iletisim" className="hover:text-gray-200 transition">İletişim</Link>
          </nav>
        </header>

        {/* Main Content Rendered Here */}
        {children}

        {/* Global Footer */}
        <footer className="py-6 text-center text-gray-500 text-sm bg-[#E0E0E0]">
          © 2026 Anayasa AI. Tüm hakları saklıdır.
        </footer>
      </body>
    </html>
  );
}
