"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import downloadConfig from "@/config/download";

const faqs = [
  {
    q: "Does Live Transcript send my audio to the cloud?",
    a: "No. All audio processing happens entirely on your computer using a locally downloaded speech model. No audio, text, or usage data is ever transmitted to any server.",
  },
  {
    q: "What languages are supported?",
    a: "Live Transcript uses Faster-Whisper which supports dozens of languages including English, Spanish, French, German, Portuguese, Hindi, and many more. Language detection is automatic.",
  },
  {
    q: "Why is the executable 383 MB?",
    a: "The executable bundles the complete Python runtime, PySide6 UI framework, the CTranslate2 inference engine, and all required native libraries so that no separate installation is needed. The speech recognition model (~150 MB) is downloaded separately on first launch.",
  },
  {
    q: "My antivirus flagged the executable. Is it safe?",
    a: "This is a common false-positive for unsigned executables built with PyInstaller. The source code is available on GitHub so you can inspect it yourself. You may need to add an exception in your antivirus software. Code signing is planned for a future release.",
  },
  {
    q: "Does it work with virtual meetings (Zoom, Teams, Meet)?",
    a: "Yes. Live Transcript captures your system's audio output, so it transcribes anything your speakers produce — including audio from Zoom, Microsoft Teams, Google Meet, or any other application.",
  },
  {
    q: "Can I edit and save the transcript?",
    a: "Yes. You can click anywhere in the transcript to correct recognition errors, then save your changes. All sessions are stored in a local SQLite database and accessible from the History tab.",
  },
  {
    q: "Is an internet connection required?",
    a: "Only on the very first launch, to download the speech recognition model (~150 MB). After that, Live Transcript works completely offline.",
  },
  {
    q: "Is the application free?",
    a: "Yes. Live Transcript v0.1.0 is free to download and use. There are no subscriptions, no paywalls, and no feature limits.",
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section
      id="faq"
      className="py-24 lg:py-32 bg-[#0b0e18]"
      aria-labelledby="faq-heading"
    >
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">
            FAQ
          </p>
          <h2
            id="faq-heading"
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
          >
            Frequently asked questions
          </h2>
          <p className="text-gray-400 text-lg">
            Have a question not answered here?{" "}
            <a
              href={`${downloadConfig.REPO_URL}/issues`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
            >
              Get in touch on GitHub.
            </a>
          </p>
        </div>

        <div className="space-y-3" role="list">
          {faqs.map((item, i) => {
            const isOpen = openIndex === i;
            return (
              <div
                key={i}
                className={`rounded-xl border transition-all duration-200 ${
                  isOpen
                    ? "border-indigo-700/50 bg-[#161b27]"
                    : "border-white/8 bg-[#161b27]/60 hover:border-white/15"
                }`}
                role="listitem"
              >
                <button
                  className="w-full flex items-center justify-between gap-4 px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 rounded-xl"
                  onClick={() => setOpenIndex(isOpen ? null : i)}
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${i}`}
                  id={`faq-question-${i}`}
                >
                  <span className="text-white font-medium text-sm leading-snug">
                    {item.q}
                  </span>
                  <ChevronDown
                    className={`w-4 h-4 text-gray-500 shrink-0 transition-transform duration-200 ${
                      isOpen ? "rotate-180 text-indigo-400" : ""
                    }`}
                    aria-hidden="true"
                  />
                </button>
                {isOpen && (
                  <div
                    id={`faq-answer-${i}`}
                    role="region"
                    aria-labelledby={`faq-question-${i}`}
                    className="px-6 pb-5 text-sm text-gray-400 leading-relaxed border-t border-white/5 pt-4"
                  >
                    {item.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
