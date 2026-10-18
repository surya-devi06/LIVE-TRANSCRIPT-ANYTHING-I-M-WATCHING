import { Mic, ExternalLink } from "lucide-react";
import downloadConfig from "@/config/download";

const links = [
  {
    heading: "Product",
    items: [
      { label: "Features", href: "#features" },
      { label: "How It Works", href: "#how-it-works" },
      { label: "Download", href: "#download" },
      { label: "FAQ", href: "#faq" },
    ],
  },
  {
    heading: "Resources",
    items: [
      { label: "Release Notes", href: downloadConfig.RELEASE_NOTES_URL, external: true },
      { label: "GitHub Repository", href: downloadConfig.REPO_URL, external: true },
      { label: "Build Instructions", href: `${downloadConfig.REPO_URL}/blob/main/BUILD_WINDOWS.md`, external: true },
      { label: "Report a Bug", href: `${downloadConfig.REPO_URL}/issues`, external: true },
    ],
  },
  {
    heading: "Legal",
    items: [
      { label: "MIT License", href: `${downloadConfig.REPO_URL}/blob/main/scripts/LICENSE.txt`, external: true },
      { label: "Privacy", href: "#faq" },
      { label: "Contact", href: `mailto:${downloadConfig.CONTACT_EMAIL}` },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="bg-[#0b0e18] border-t border-white/5" role="contentinfo">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-900/40">
                <Mic className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-white text-lg tracking-tight">
                Live<span className="text-indigo-400">Transcript</span>
              </span>
            </div>
            <p className="text-gray-500 text-sm leading-relaxed mb-4">
              Real-time speech transcription for Windows. Local, private, and free.
            </p>
            <a
              href={downloadConfig.REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-300 text-sm transition-colors"
              aria-label="GitHub Repository"
            >
              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              View on GitHub
            </a>
          </div>

          {/* Link columns */}
          {links.map((col) => (
            <div key={col.heading}>
              <h3 className="text-white font-semibold text-xs tracking-widest uppercase mb-4">
                {col.heading}
              </h3>
              <ul className="space-y-3" role="list">
                {col.items.map((item) => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      target={"external" in item && item.external ? "_blank" : undefined}
                      rel={"external" in item && item.external ? "noopener noreferrer" : undefined}
                      className="text-gray-500 hover:text-gray-300 text-sm transition-colors inline-flex items-center gap-1.5"
                    >
                      {item.label}
                      {"external" in item && item.external && (
                        <ExternalLink className="w-3 h-3 opacity-50" aria-hidden="true" />
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/5 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-600">
          <p>© {new Date().getFullYear()} Live Transcript. Released under the MIT License.</p>
          <p>
            Built with Python · PySide6 · Faster-Whisper · SQLite
          </p>
        </div>
      </div>
    </footer>
  );
}
