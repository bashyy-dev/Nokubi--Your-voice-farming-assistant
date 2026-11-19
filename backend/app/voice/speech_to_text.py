import io
import wave

from google.cloud import speech
from google.api_core.exceptions import GoogleAPIError
from google.oauth2 import service_account

from app.core.config import get_settings


def transcribe_audio(wav_bytes: bytes, language: str) -> str:
    """Transcribe normalized PCM WAV audio using Google Cloud Speech-to-Text."""
    if language not in {"ha-NG", "en-NG"}:
        raise ValueError("Unsupported language. Use ha-NG or en-NG.")

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        frames = wav_file.readframes(wav_file.getnframes())

    if channels != 1:
        raise ValueError("Audio must be mono after normalization.")

    settings = get_settings()
    credentials = None
    if settings.google_application_credentials:
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_application_credentials
        )

    client = speech.SpeechClient(credentials=credentials)
    audio = speech.RecognitionAudio(content=frames)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code=language,
        audio_channel_count=1,
        enable_automatic_punctuation=True,
    )

    try:
        response = client.recognize(config=config, audio=audio)
    except GoogleAPIError as exc:
        raise RuntimeError("Google Speech-to-Text request failed.") from exc

    transcripts = [
        result.alternatives[0].transcript.strip()
        for result in response.results
        if result.alternatives
    ]
    transcript = " ".join(transcripts).strip()

    if not transcript:
        raise ValueError("We could not understand the recording. Please try speaking again.")

    return transcript
