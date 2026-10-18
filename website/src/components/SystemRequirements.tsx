import { Check, X } from "lucide-react";

const requirements = [
  { label: "Operating System", value: "Windows 10 or Windows 11 (64-bit)" },
  { label: "Architecture", value: "x86-64 (Intel or AMD processor)" },
  { label: "RAM", value: "4 GB minimum · 8 GB recommended" },
  { label: "Disk Space", value: "~600 MB (app + speech model)" },
  { label: "Audio", value: "System audio output (speakers or headphones)" },
  { label: "Internet", value: "Required only on first launch (model download)" },
  { label: "Python", value: "Not required — bundled in the executable" },
  { label: "Admin Rights", value: "Not required for installation" },
];

const supported = [
  { label: "Windows 11", supported: true },
  { label: "Windows 10 (21H2+)", supported: true },
  { label: "Windows 10 (older builds)", supported: null, note: "May work" },
  { label: "Windows 8 / 8.1", supported: false },
  { label: "Windows 7", supported: false },
  { label: "macOS", supported: false, note: "Planned" },
  { label: "Linux", supported: false, note: "Planned" },
];

export default function SystemRequirements() {
  return (
    <section
      id="requirements"
      className="py-24 lg:py-32 bg-[#0b0e18]"
      aria-labelledby="requirements-heading"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Compatibility
          </p>
          <h2
            id="requirements-heading"
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
          >
            System requirements
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Live Transcript is a self-contained Windows application. No
            additional software required.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Requirements table */}
          <div className="rounded-2xl border border-white/8 bg-[#161b27] overflow-hidden">
            <div className="px-6 py-4 bg-[#1a2033] border-b border-white/5">
              <h3 className="text-white font-semibold text-sm">Requirements</h3>
            </div>
            <div className="divide-y divide-white/5">
              {requirements.map((req) => (
                <div
                  key={req.label}
                  className="flex items-start justify-between px-6 py-3.5 text-sm"
                >
                  <span className="text-gray-500 shrink-0 w-36">{req.label}</span>
                  <span className="text-gray-300 text-right">{req.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Compatibility table */}
          <div className="rounded-2xl border border-white/8 bg-[#161b27] overflow-hidden">
            <div className="px-6 py-4 bg-[#1a2033] border-b border-white/5">
              <h3 className="text-white font-semibold text-sm">Platform Support</h3>
            </div>
            <div className="divide-y divide-white/5">
              {supported.map((item) => (
                <div
                  key={item.label}
                  className="flex items-center justify-between px-6 py-3.5 text-sm"
                >
                  <span className="text-gray-300">{item.label}</span>
                  <div className="flex items-center gap-2">
                    {item.note && (
                      <span className="text-xs text-gray-600 italic">{item.note}</span>
                    )}
                    {item.supported === true && (
                      <Check className="w-4 h-4 text-green-500" aria-label="Supported" />
                    )}
                    {item.supported === false && (
                      <X className="w-4 h-4 text-red-500/70" aria-label="Not supported" />
                    )}
                    {item.supported === null && (
                      <span className="text-yellow-600 text-xs font-mono">~</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
