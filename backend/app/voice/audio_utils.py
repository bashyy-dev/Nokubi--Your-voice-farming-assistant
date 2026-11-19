import subprocess
import tempfile
import wave
from pathlib import Path

from app.core.config import get_settings


def normalize_audio_to_wav(audio_bytes: bytes) -> tuple[bytes, int]:
    \"\"\"Convert uploaded audio to 16 kHz mono PCM WAV using FFmpeg.

    Returns (wav_bytes, sample_rate). A temporary file is used because FFmpeg
    works reliably with file inputs across common browser audio formats.
    \"\"\"
    settings = get_settings()
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "input_audio"
        target = Path(temp_dir) / "normalized.wav"
        source.write_bytes(audio_bytes)

        command = [
            settings.ffmpeg_binary,
            "-y",
            "-i", str(source),
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            str(target),
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=45,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "FFmpeg was not found. Install FFmpeg and add it to PATH."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Audio conversion took too long.") from exc

        if completed.returncode != 0 or not target.exists():
            raise ValueError("Audio format could not be processed. Try another recording.")

        wav_bytes = target.read_bytes()

    # Read sample rate from the WAV header so STT config matches the actual file.
    import io
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        sample_rate = wav_file.getframerate()

    return wav_bytes, sample_rate
