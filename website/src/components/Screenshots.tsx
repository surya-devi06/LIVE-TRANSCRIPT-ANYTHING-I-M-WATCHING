const screens = [
  {
    title: "Live Transcription",
    description: "Words appear as they are spoken, timestamped line by line.",
    ui: <TranscriptionUI />,
  },
  {
    title: "Session History",
    description: "Browse, search, and reopen every past transcription session.",
    ui: <HistoryUI />,
  },
  {
    title: "Vocabulary Manager",
    description: "Save and look up words and phrases from your transcripts.",
    ui: <VocabUI />,
  },
];

export default function Screenshots() {
  return (
    <section
      id="screenshots"
      className="py-24 lg:py-32 bg-[#0f1117]"
      aria-labelledby="screenshots-heading"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Gallery
          </p>
          <h2
            id="screenshots-heading"
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
          >
            See it in action
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            A clean, focused interface designed to stay out of your way.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {screens.map((screen) => (
            <div key={screen.title} className="group">
              {/* Mockup window */}
              <div className="rounded-2xl overflow-hidden border border-white/8 shadow-xl shadow-black/40 bg-[#161b27] mb-4 transition-all duration-300 group-hover:border-indigo-800/50 group-hover:shadow-indigo-900/20">
                {/* Chrome */}
                <div className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2033] border-b border-white/5">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/70" />
                  </div>
                  <span className="text-xs text-gray-600 ml-2 font-mono">{screen.title}</span>
                </div>
                {/* Content */}
                <div className="p-4 h-52 overflow-hidden">{screen.ui}</div>
              </div>
              <h3 className="text-white font-semibold text-sm mb-1">{screen.title}</h3>
              <p className="text-gray-500 text-sm">{screen.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Inline UI simulations ── */

function TranscriptionUI() {
  const lines = [
    { t: "00:00:02", s: "Good morning. Let's get started with today's briefing." },
    { t: "00:00:09", s: "The first item on the agenda is the product launch." },
    { t: "00:00:18", s: "We're targeting a Q1 release date across all platforms." },
    { t: "00:00:31", s: "Any questions before we move to the next topic?" },
  ];
  return (
    <div className="space-y-2.5 font-mono text-xs">
      {lines.map((l, i) => (
        <div key={i} className={`flex gap-2.5 ${i === lines.length - 1 ? "opacity-100" : "opacity-50"}`}>
          <span className="text-gray-700 shrink-0">{l.t}</span>
          <span className={i === lines.length - 1 ? "text-gray-200 border-l-2 border-indigo-500 pl-2" : "text-gray-400"}>{l.s}</span>
        </div>
      ))}
      <div className="flex gap-2.5">
        <span className="text-gray-700 shrink-0">00:00:40</span>
        <span className="inline-block w-1.5 h-3.5 bg-indigo-400 animate-pulse rounded-sm" />
      </div>
    </div>
  );
}

function HistoryUI() {
  const sessions = [
    { name: "Team Standup", date: "Today, 09:15", dur: "14 min", active: true },
    { name: "Product Review", date: "Yesterday, 14:30", dur: "48 min", active: false },
    { name: "Podcast Episode 12", date: "2 days ago", dur: "62 min", active: false },
    { name: "Client Call", date: "3 days ago", dur: "31 min", active: false },
  ];
  return (
    <div className="space-y-1.5">
      {sessions.map((s) => (
        <div
          key={s.name}
          className={`flex items-center justify-between p-2 rounded-lg text-xs ${
            s.active ? "bg-indigo-900/40 border border-indigo-700/40" : "bg-white/3 border border-transparent"
          }`}
        >
          <div>
            <p className={`font-medium ${s.active ? "text-indigo-300" : "text-gray-300"}`}>{s.name}</p>
            <p className="text-gray-600">{s.date}</p>
          </div>
          <span className="text-gray-600 font-mono">{s.dur}</span>
        </div>
      ))}
    </div>
  );
}

function VocabUI() {
  const words = [
    { word: "Briefing", def: "A meeting for giving information or instructions." },
    { word: "Agenda", def: "A list of items to be discussed at a meeting." },
    { word: "Deployment", def: "The action of bringing resources into effective action." },
  ];
  return (
    <div className="space-y-2.5">
      {words.map((w) => (
        <div key={w.word} className="p-2.5 rounded-lg bg-white/3 border border-white/5 text-xs">
          <p className="text-violet-400 font-semibold mb-0.5">{w.word}</p>
          <p className="text-gray-500 leading-snug">{w.def}</p>
        </div>
      ))}
    </div>
  );
}
