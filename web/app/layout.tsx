import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Nav from "@/components/Nav";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "제조 일보 AI 분석",
  description: "제조 일보 이미지를 AI로 분석하여 이상탐지, 트렌드, 인사이트를 제공합니다.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className="dark">
      <body className={`${geist.className} min-h-screen`}>
        <Nav />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 pt-20 pb-12">
          {children}
        </main>
      </body>
    </html>
  );
}
