const steps = [
  {
    number: "01",
    title: "Open the App",
    description:
      "Launch Live Transcript on your Windows PC. No installation of Python, models, or drivers needed — everything is bundled in the single executable.",
    detail: "First launch downloads the speech model (~150 MB) once.",
  },
  {
    number: "02",
    title: "Press Record",
    description:
      "Click Start to begin capturing your system audio. Live Transcript listens to whatever your speakers or headphones are playing.",
    detail: "Works with meetings, videos, podcasts, lectures — any system audio.",
  },
  {
    number: "03",
    title: "Read, Edit & Save",
    description:
      "Watch the transcript appear in real time. Correct any mistakes, copy selections, and save the session for later reference in the History tab.",
    detail: "Sessions are stored locally in SQLite — no cloud, no account.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="py-24 lg:py-32 bg-[#0b0e18] relative overflow-hidden"
      aria-labelledby="how-heading"
    >
      {/* Subtle background accent */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
      >
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="text-violet-400 text-sm font-semibold tracking-widest uppercase mb-3">
            How It Works
          </p>
          <h2
            id="how-heading"
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
          >
            Up and running in{" "}
            <span className="gradient-text">three simple steps</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            No accounts, no configuration files, no complexity.
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connector lines (desktop only) */}
          <div
            className="hidden md:block absolute top-10 left-[calc(33.33%+1rem)] right-[calc(33.33%+1rem)] h-px bg-gradient-to-r from-indigo-800/0 via-indigo-700/60 to-indigo-800/0"
            aria-hidden="true"
          />

          {steps.map((step, i) => (
            <div key={step.number} className="flex flex-col items-center text-center group">
              {/* Step number circle */}
              <div
                className={`relative w-20 h-20 rounded-2xl flex items-center justify-center mb-6 border transition-all duration-300 ${
                  i === 0
                    ? "bg-indigo-600/20 border-indigo-600/50 shadow-lg shadow-indigo-900/30 group-hover:shadow-indigo-600/20"
                    : i === 1
                    ? "bg-violet-600/20 border-violet-600/50 shadow-lg shadow-violet-900/30 group-hover:shadow-violet-600/20"
                    : "bg-purple-600/20 border-purple-600/50 shadow-lg shadow-purple-900/30 group-hover:shadow-purple-600/20"
                }`}
              >
                <span
                  className={`font-bold text-2xl font-mono ${
                    i === 0
                      ? "text-indigo-400"
                      : i === 1
                      ? "text-violet-400"
                      : "text-purple-400"
                  }`}
                >
                  {step.number}
                </span>
              </div>

              <h3 className="text-white font-semibold text-lg mb-3">
                {step.title}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed mb-3">
                {step.description}
              </p>
              <p className="text-xs text-gray-600 italic">{step.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
