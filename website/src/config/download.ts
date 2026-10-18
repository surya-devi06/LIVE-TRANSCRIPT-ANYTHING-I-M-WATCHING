// Download & Project configuration
// ─────────────────────────────────────────────────────────────
// The live website downloads the Windows installer directly.
//
// When publishing to GitHub / Vercel, upload the installer
// to GitHub Releases and update DOWNLOAD_URL with the release link.
// ─────────────────────────────────────────────────────────────

const downloadConfig = {
  /** Semantic version of the current release */
  VERSION: "0.1.0",

  /**
   * Direct download URL for the Windows installer.
   * - Locally: served directly from `/LiveTranscript_Installer.exe`
   * - In production: update to your GitHub Release asset URL when published
   */
  DOWNLOAD_URL: "/LiveTranscript_Installer.exe",

  /** Human-readable file size shown across the site */
  FILE_SIZE: "384 MB",

  /** Supported operating system label */
  OS: "Windows 10 / 11 (64-bit)",

  /** GitHub repository */
  REPO_URL: "https://github.com/surya-devi06/LIVE-TRANSCRIPT-ANYTHING-I-M-WATCHING",

  /** Release notes link */
  RELEASE_NOTES_URL: "https://github.com/surya-devi06/LIVE-TRANSCRIPT-ANYTHING-I-M-WATCHING/releases",

  /** Contact email */
  CONTACT_EMAIL: "support@livetranscript.local",
} as const;

export default downloadConfig;
export type DownloadConfig = typeof downloadConfig;
