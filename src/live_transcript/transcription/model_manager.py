"""Model management utility for Faster-Whisper models: checking local presence and disk space."""

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Dict, Optional

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("transcription.model_manager")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    size_mb: int
    required_free_mb: int
    display_name: str
    description: str


MODEL_SPECS: Dict[str, ModelSpec] = {
    "tiny": ModelSpec(
        name="tiny",
        size_mb=75,
        required_free_mb=300,
        display_name="Tiny (39M)",
        description="Fastest (<0.3s latency), lowest RAM (~300 MB). Best for quick tests and low-end hardware.",
    ),
    "base": ModelSpec(
        name="base",
        size_mb=145,
        required_free_mb=500,
        display_name="Base (74M) - Recommended",
        description="Default recommendation. Fast (<0.7s latency), ~500 MB RAM, excellent English accuracy.",
    ),
    "small": ModelSpec(
        name="small",
        size_mb=480,
        required_free_mb=1200,
        display_name="Small (244M)",
        description="High accuracy (~1.5s latency), ~1 GB RAM. Recommended for multilingual transcription.",
    ),
    "medium": ModelSpec(
        name="medium",
        size_mb=1500,
        required_free_mb=3000,
        display_name="Medium (769M)",
        description="Highest accuracy (~3.5s latency), ~2.5 GB RAM. Handles heavy accents and background noise.",
    ),
}


class ModelManager:
    """Manages Whisper model verification, disk space requirements, and download status."""

    @staticmethod
    def get_spec(model_name: str) -> ModelSpec:
        """Get specification for a model, defaulting to 'base' if unrecognized."""
        return MODEL_SPECS.get(model_name.lower(), MODEL_SPECS["base"])

    @staticmethod
    def check_disk_space(target_dir: Path, model_name: str) -> tuple[bool, int, int]:
        """Check whether target volume has sufficient free disk space.
        
        Returns:
            (has_enough_space: bool, free_mb: int, required_mb: int)
        """
        spec = ModelManager.get_spec(model_name)
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            total, used, free = shutil.disk_usage(target_dir)
            free_mb = int(free / (1024 * 1024))
            has_enough = free_mb >= spec.required_free_mb
            return (has_enough, free_mb, spec.required_free_mb)
        except Exception as exc:
            logger.warning("Failed to query disk usage on %s: %s", target_dir, exc)
            # Default to assuming space is sufficient if query fails
            return (True, 9999, spec.required_free_mb)

    @staticmethod
    def is_model_downloaded(models_dir: Path, model_name: str) -> bool:
        """Check whether the model files are already downloaded locally."""
        if not models_dir.exists():
            return False

        # Check standard huggingface hub repository pattern
        expected_dirs = [
            models_dir / f"models--Systran--faster-whisper-{model_name}",
            models_dir / model_name,
        ]

        # Look for model.bin or model.safetensors and config.json inside snapshot directories
        for exp_dir in expected_dirs:
            if exp_dir.is_dir():
                # Scan directory and subdirectories for model.bin or config.json
                has_model = any(exp_dir.glob("**/model.bin")) or any(exp_dir.glob("**/model.safetensors"))
                has_config = any(exp_dir.glob("**/config.json"))
                if has_model or has_config:
                    return True

        # Check if files reside directly in models_dir
        if (models_dir / "model.bin").exists() and (models_dir / "config.json").exists():
            return True

        # Try faster_whisper local check if possible
        try:
            import faster_whisper
            faster_whisper.download_model(model_name, output_dir=str(models_dir), local_files_only=True)
            return True
        except Exception:
            return False
