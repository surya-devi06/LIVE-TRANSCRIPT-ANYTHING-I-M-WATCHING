import { Download, Monitor, HardDrive, Tag, FileText } from "lucide-react";
import downloadConfig from "@/config/download";

export default function DownloadSection() {
  const isPlaceholder = downloadConfig.DOWNLOAD_URL === "PLACEHOLDER_DOWNLOAD_URL";

  return (
    <section
      id="download"
      className="py-24 lg:py-32 bg-[#0f1117] relative overflow-hidden"
      aria-labelledby="download-heading"
    >
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-indigo-900/20 rounded-full blur-[120px]" />
      </div>

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">
          Download
        </p>
        <h2
          id="download-heading"
          className="text-3xl sm:text-4xl font-bold text-white mb-4"
        >
          Get Live Transcript
        </h2>
        <p className="text-gray-400 text-lg mb-12 max-w-xl mx-auto">
          A single executable — no installer required. Download, double-click, start transcribing.
        </p>

        {/* Release card */}
        <div className="rounded-2xl border border-white/10 bg-[#161b27] p-8 mb-8 text-left">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-white font-semibold text-lg">Live Transcript for Windows</h3>
              <p className="text-gray-500 text-sm mt-1">Stable release</p>
            </div>
            <span className="px-2.5 py-1 rounded-md bg-indigo-900/50 border border-indigo-700/50 text-indigo-300 text-xs font-mono">
              v{downloadConfig.VERSION}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <Stat icon={Tag} label="Version" value={`v${downloadConfig.VERSION}`} />
            <Stat icon={Monitor} label="Platform" value="Windows" />
            <Stat icon={HardDrive} label="Size" value={downloadConfig.FILE_SIZE} />
            <Stat icon={FileText} label="Format" value=".exe" />
          </div>

          {/* Download button */}
          {isPlaceholder ? (
            <div className="rounded-xl border border-yellow-800/40 bg-yellow-900/10 p-4 text-sm text-yellow-400">
              <p className="font-semibold mb-1">Download not yet configured</p>
              <p className="text-yellow-600">
                Edit{" "}
                <code className="bg-black/30 px-1 rounded font-mono text-xs">
                  src/config/download.ts
                </code>{" "}
                and replace{" "}
                <code className="bg-black/30 px-1 rounded font-mono text-xs">
                  PLACEHOLDER_DOWNLOAD_URL
                </code>{" "}
                with your actual release URL.
              </p>
            </div>
          ) : (
            <a
              href={downloadConfig.DOWNLOAD_URL}
              download
              className="flex items-center justify-center gap-3 w-full py-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl transition-all shadow-xl shadow-indigo-900/40 hover:shadow-indigo-500/30 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-[#161b27]"
            >
              <Download className="w-5 h-5" />
              Download LiveTranscript.exe
              <span className="text-indigo-300 font-normal text-sm">
                ({downloadConfig.FILE_SIZE})
              </span>
            </a>
          )}
        </div>

        {/* Notes */}
        <div className="space-y-2 text-sm text-gray-600">
          <p>Requires Windows 10 or Windows 11 (64-bit) · No Python installation needed</p>
          <p>
            First launch downloads the speech recognition model (~150 MB).{" "}
            <a
              href={downloadConfig.RELEASE_NOTES_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-500 hover:text-indigo-400 underline underline-offset-2"
            >
              Release notes →
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}

function Stat({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-1.5 text-gray-600 text-xs">
        <Icon className="w-3.5 h-3.5" />
        <span>{label}</span>
      </div>
      <span className="text-gray-200 font-medium text-sm">{value}</span>
    </div>
  );
}
