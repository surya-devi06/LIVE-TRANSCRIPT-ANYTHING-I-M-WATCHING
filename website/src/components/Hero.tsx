import { Download, Monitor, Sparkles, Shield, Cpu } from "lucide-react";
import downloadConfig from "@/config/download";

export default function Hero() {
  const isPlaceholder = downloadConfig.DOWNLOAD_URL === "PLACEHOLDER_DOWNLOAD_URL";

  return (
    <section
      className="relative min-h-[92vh] flex items-center justify-center overflow-hidden pt-24 pb-16 lg:py-28"
      aria-label="Hero"
    >
      {/* Background ambient lighting */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[450px] bg-indigo-600/15 rounded-full blur-[140px]" />
        <div className="absolute top-1/3 left-1/4 w-[400px] h-[300px] bg-violet-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-10 right-1/4 w-[350px] h-[250px] bg-purple-600/10 rounded-full blur-[100px]" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        {/* Desktop 2-column, Mobile 1-column */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Left Column: Value Prop, Headline, CTAs */}
          <div className="lg:col-span-6 flex flex-col items-center lg:items-start text-center lg:text-left">
            {/* Version Release Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-700/40 text-indigo-300 text-xs font-medium mb-6 shadow-sm shadow-indigo-950">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
              <span>v{downloadConfig.VERSION} &mdash; Standalone Windows Desktop App</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6 text-white">
              Hear It Once. <br />
              <span className="gradient-text">Read It Instantly.</span>
            </h1>

            {/* Description */}
            <p className="text-base sm:text-lg text-gray-300 max-w-xl mb-8 leading-relaxed">
              Capture your computer&apos;s audio and transcribe live speech into readable,
              editable text in real time. Powered by Faster-Whisper, running 100% locally
              on your Windows PC.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto mb-10">
              <a
                href={isPlaceholder ? "#download" : downloadConfig.DOWNLOAD_URL}
                download={!isPlaceholder}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-900/50 hover:shadow-indigo-600/30 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                aria-label="Download Live Transcript for Windows"
              >
                <Download className="w-4 h-4" />
                <span>Download for Windows</span>
              </a>
              <a
                href="#how-it-works"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-white/5 hover:bg-white/10 text-gray-200 hover:text-white font-medium rounded-xl transition-all border border-white/10 hover:border-white/20 focus:outline-none focus:ring-2 focus:ring-white/20"
              >
                See how it works
              </a>
            </div>

            {/* Core Trust Pillars */}
            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-white/10 w-full max-w-lg text-left">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Shield className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>100% Offline</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Cpu className="w-4 h-4 text-violet-400 shrink-0" />
                <span>Zero Cloud Lag</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
                <span>SQLite History</span>
              </div>
            </div>
          </div>

          {/* Right Column: High-Fidelity Desktop App Preview Mockup */}
          <div className="lg:col-span-6 w-full max-w-xl mx-auto lg:max-w-none">
            <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-indigo-950/40 bg-[#161b27]">
              {/* Window Title Bar */}
              <div className="flex items-center justify-between px-4 py-3 bg-[#131722] border-b border-white/5">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  <span className="ml-3 text-xs text-gray-400 font-medium">
                    Live Transcript v{downloadConfig.VERSION} &mdash; Desktop Session
                  </span>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800/40">
                  <span>WASAPI Loopback</span>
                </div>
              </div>

              {/* Sub-toolbar */}
              <div className="px-5 py-3 bg-[#191f2d] border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-2.5 w-2.5 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
                  </span>
                  <span className="text-xs font-semibold text-red-400 tracking-wide uppercase">
                    Live Audio Capture
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-400 font-mono">
                  <span>Model: tiny.en</span>
                  <span className="text-gray-600">|</span>
                  <span className="text-indigo-400 font-semibold">00:03:12</span>
                </div>
              </div>

              {/* Simulated Live Transcript Terminal Area */}
              <div className="p-6 space-y-4 font-mono text-xs sm:text-sm bg-[#111520] min-h-[300px]">
                <TranscriptRow
                  time="00:00:02"
                  speaker="Host"
                  text="Welcome everyone. We'll start today's project presentation now."
                  dimmed
                />
                <TranscriptRow
                  time="00:00:15"
                  speaker="Speaker 1"
                  text="Thanks. The focus of this sprint has been local real-time inference."
                  dimmed
                />
                <TranscriptRow
                  time="00:01:04"
                  speaker="Speaker 1"
                  text="By capturing system audio directly, no external virtual cable is needed."
                  dimmed
                />
                <TranscriptRow
                  time="00:02:48"
                  speaker="Speaker 2"
                  text="And all past transcripts are saved locally to SQLite for quick lookup."
                  active
                />

                {/* Live stream cursor indicator */}
                <div className="flex items-center gap-3 pt-2">
                  <span className="text-gray-600 font-mono text-xs">00:03:12</span>
                  <span className="text-indigo-400 text-xs font-semibold px-1.5 py-0.5 rounded bg-indigo-950/80 border border-indigo-800/40">
                    Transcribing...
                  </span>
                  <span className="inline-block w-2 h-4 bg-indigo-400 animate-pulse rounded-sm" />
                </div>
              </div>

              {/* Status bar */}
              <div className="px-5 py-2.5 bg-[#161b27] border-t border-white/5 flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  CTranslate2 Engine Ready
                </span>
                <span>Select any word to add to Vocabulary</span>
              </div>
            </div>

            {/* Platform Sub-detail */}
            <div className="flex items-center justify-center gap-2 mt-4 text-gray-500 text-xs">
              <Monitor className="w-3.5 h-3.5" />
              <span>{downloadConfig.OS} &middot; Approx. {downloadConfig.FILE_SIZE} standalone executable</span>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}

function TranscriptRow({
  time,
  speaker,
  text,
  active = false,
  dimmed = false,
}: {
  time: string;
  speaker: string;
  text: string;
  active?: boolean;
  dimmed?: boolean;
}) {
  return (
    <div className={`flex items-start gap-3 ${dimmed ? "opacity-60" : "opacity-100"}`}>
      <span className="text-gray-600 shrink-0 font-mono text-xs pt-0.5">{time}</span>
      <span className="text-indigo-400/90 font-medium shrink-0 text-xs pt-0.5">[{speaker}]</span>
      <span
        className={`leading-relaxed ${
          active ? "text-white font-medium pl-1 border-l-2 border-indigo-500" : "text-gray-300"
        }`}
      >
        {text}
      </span>
    </div>
  );
}
