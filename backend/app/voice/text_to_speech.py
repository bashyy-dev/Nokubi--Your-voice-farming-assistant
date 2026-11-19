import httpx

from app.core.config import get_settings


def synthesize_speech(text: str, language: str) -> bytes:
    \"\"\"Generate MP3 audio with ElevenLabs. Voice IDs are configured per language.\"\"\"
    settings = get_settings()

    if not settings.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured.")

    if language == "ha-NG":
        voice_id = settings.elevenlabs_ha_voice_id
    elif language == "en-NG":
        voice_id = settings.elevenlabs_en_voice_id
    else:
        raise ValueError("Unsupported language. Use ha-NG or en-NG.")

    if not voice_id:
        raise RuntimeError(f"No ElevenLabs voice ID configured for {language}.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": settings.elevenlabs_model_id,
    }

    try:
        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            params={"output_format": "mp3_44100_128"},
            timeout=60.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError("ElevenLabs text-to-speech request failed.") from exc

    return response.content
