import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
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
  title: "Live Transcript — Real-Time Speech Transcription for Windows",
  description:
    "Live Transcript captures system audio and transcribes speech to text in real time on your Windows PC. No cloud required, no subscriptions — powered by Faster-Whisper.",
  keywords: [
    "live transcription",
    "speech to text",
    "Windows transcription app",
    "real-time transcription",
    "offline transcription",
    "Faster-Whisper",
    "audio transcription",
  ],
  openGraph: {
    title: "Live Transcript — Real-Time Speech Transcription for Windows",
    description:
      "Capture any system audio and get an instant text transcript. 100% local, private, and free.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Live Transcript",
    description: "Real-time speech transcription for Windows. Local, private, free.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#0f1117] text-gray-100`}
      >
        {children}
      </body>
    </html>
  );
}
