from app.core.config import get_settings
from app.voice.audio_utils import normalize_audio_to_wav
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from app.assistant.service import answer_question


def process_voice_question(audio_bytes: bytes, language: str) -> dict:
    \"\"\"Run the complete voice pipeline and return transcript, answer and audio.\"\"\"
    settings = get_settings()
    max_bytes = settings.max_audio_size_mb * 1024 * 1024

    if len(audio_bytes) > max_bytes:
        raise ValueError(
            f"Audio is too large. Maximum upload size is {settings.max_audio_size_mb} MB."
        )

    wav_bytes, _sample_rate = normalize_audio_to_wav(audio_bytes)
    transcript = transcribe_audio(wav_bytes, language)

    # This is the key integration: voice calls the SAME assistant used by text chat.
    answer = answer_question(transcript, language)
    if not answer or not answer.strip():
        raise RuntimeError("The assistant returned an empty answer.")

    audio = synthesize_speech(answer, language)

    return {
        "transcript": transcript,
        "answer": answer,
        "audio": audio,
        "audio_mime_type": "audio/mpeg",
    }
