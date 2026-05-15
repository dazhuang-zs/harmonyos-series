import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HarmonyOS 开发助手",
  description: "MiMo 大模型驱动的鸿蒙开发助手",
};

const NAV_ITEMS = [
  { href: "/", label: "问答" },
  { href: "/codegen", label: "代码生成" },
  { href: "/diagnose", label: "错误诊断" },
  { href: "/migrate", label: "代码迁移" },
  { href: "/publish", label: "CSDN 发布" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-zinc-50 dark:bg-zinc-950">
        <header className="sticky top-0 z-50 border-b bg-white/80 dark:bg-zinc-900/80 backdrop-blur">
          <div className="max-w-5xl mx-auto flex items-center justify-between px-4 h-14">
            <Link href="/" className="flex items-center gap-2 font-bold text-lg">
              <span className="text-2xl">🦋</span>
              <span className="hidden sm:inline">HarmonyOS 开发助手</span>
            </Link>
            <nav className="flex items-center gap-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-3 py-1.5 text-sm rounded-md text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
