import {
  Mic,
  Clock,
  BookOpen,
  History,
  WifiOff,
  Keyboard,
} from "lucide-react";

const features = [
  {
    icon: Mic,
    title: "Real-Time Transcription",
    description:
      "Captures your system audio and converts speech to text as it happens — with word-level accuracy powered by Faster-Whisper.",
    accent: "indigo",
  },
  {
    icon: WifiOff,
    title: "100% Offline & Private",
    description:
      "Runs entirely on your machine. No audio is ever uploaded. Your conversations stay on your device.",
    accent: "violet",
  },
  {
    icon: Clock,
    title: "Timestamped Transcripts",
    description:
      "Every transcript line is stamped with the exact time, making it easy to navigate long recordings.",
    accent: "purple",
  },
  {
    icon: History,
    title: "Session History",
    description:
      "All transcription sessions are automatically saved to a local SQLite database. Search, revisit, and export any past session.",
    accent: "indigo",
  },
  {
    icon: BookOpen,
    title: "Vocabulary Manager",
    description:
      "Save words or phrases from any transcript. Build a personal vocabulary list with definitions and context.",
    accent: "violet",
  },
  {
    icon: Keyboard,
    title: "Editable Transcripts",
    description:
      "Correct recognition errors by hand. Copy selected text, edit inline, and save your changes back to the database.",
    accent: "purple",
  },
];

const accentMap: Record<string, string> = {
  indigo:
    "from-indigo-500/10 border-indigo-800/30 group-hover:border-indigo-600/60 text-indigo-400",
  violet:
    "from-violet-500/10 border-violet-800/30 group-hover:border-violet-600/60 text-violet-400",
  purple:
    "from-purple-500/10 border-purple-800/30 group-hover:border-purple-600/60 text-purple-400",
};

export default function Features() {
  return (
    <section
      id="features"
      className="py-24 lg:py-32 bg-[#0f1117]"
      aria-labelledby="features-heading"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Features
          </p>
          <h2
            id="features-heading"
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
          >
            Everything you need to{" "}
            <span className="gradient-text">capture every word</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            A focused set of features built around one goal: turning audio into
            accurate, searchable, editable text.
          </p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature) => {
            const Icon = feature.icon;
            const accent = accentMap[feature.accent];
            return (
              <article
                key={feature.title}
                className={`group relative rounded-2xl border bg-gradient-to-b ${accent} bg-[#161b27] p-6 card-hover`}
              >
                <div
                  className={`inline-flex items-center justify-center w-10 h-10 rounded-xl bg-[#0f1117] border border-current/20 mb-4 ${accent.split(" ").pop()}`}
                  aria-hidden="true"
                >
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-white font-semibold text-base mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
