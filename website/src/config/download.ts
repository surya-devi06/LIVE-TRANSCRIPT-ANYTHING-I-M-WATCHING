// Download & Project configuration
// ─────────────────────────────────────────────────────────────
// The live website downloads the Windows installer directly.
//
// When publishing to GitHub / Vercel, upload the installer
// to GitHub Releases and update DOWNLOAD_URL with the release link.
// ─────────────────────────────────────────────────────────────

export interface DownloadConfigType {
  VERSION: string;
  DOWNLOAD_URL: string;
  FILE_SIZE: string;
  OS: string;
  REPO_URL: string;
  RELEASE_NOTES_URL: string;
  CONTACT_EMAIL: string;
}

const downloadConfig: DownloadConfigType = {
  /** Semantic version of the current release */
  VERSION: "0.1.0",

  /**
   * Direct download URL for the Windows installer from GitHub Releases.
   */
  DOWNLOAD_URL: "https://github.com/surya-devi06/LIVE-TRANSCRIPT-ANYTHING-I-M-WATCHING/releases/download/v0.1.0/LiveTranscript_Installer.exe",

  /** Human-readable file size shown across the site */
  FILE_SIZE: "366 MB",

  /** Supported operating system label */
  OS: "Windows 10 / 11 (64-bit)",

  /** GitHub repository */
  REPO_URL: "https://github.com/surya-devi06/LIVE-TRANSCRIPT-ANYTHING-I-M-WATCHING",

  /** Release notes link */
  RELEASE_NOTES_URL: "https://github.com/surya-devi06/LIVE-TRANSCRIPT-ANYTHING-I-M-WATCHING/releases",

  /** Contact email */
  CONTACT_EMAIL: "support@livetranscript.local",
};

export default downloadConfig;
