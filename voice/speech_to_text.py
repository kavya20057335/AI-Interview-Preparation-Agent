"""
Voice input / speech-to-text helper for Version 7.

The Streamlit UI records microphone audio with st.audio_input().
This module accepts the resulting audio bytes and sends them to
SpeechRecognition when that optional dependency is installed.

The module does not affect the core NLP evaluator.
"""

import io

try:
    import speech_recognition as sr
except ImportError:
    sr = None


def speech_to_text_available():
    """Return True when SpeechRecognition is installed."""
    return sr is not None


def get_supported_audio_types():
    """Return common audio MIME types accepted by the UI."""
    return ["audio/wav", "audio/webm", "audio/ogg", "audio/mp4"]


def transcribe_audio_bytes(audio_bytes, language="en-IN"):
    """
    Convert recorded audio bytes to text.

    SpeechRecognition's Google recognizer is used when available.
    If the local package or recognizer cannot process the recording,
    an empty string is returned so the Streamlit app can offer a
    text fallback.

    This function intentionally keeps speech recognition separate
    from the project's NLP scoring pipeline.
    """
    if sr is None or not audio_bytes:
        return ""

    recognizer = sr.Recognizer()

    try:
        # Streamlit browser recordings are commonly WAV-compatible.
        # AudioData can be built directly from raw PCM only when the
        # format is known, so first try the AudioFile interface.
        audio_stream = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_stream) as source:
            audio = recognizer.record(source)

        try:
            return recognizer.recognize_google(audio, language=language).strip()
        except (sr.UnknownValueError, sr.RequestError):
            return ""
    except Exception:
        return ""


def transcribe_wav_file(path, language="en-IN"):
    """Transcribe a WAV file path when a local file is available."""
    if sr is None:
        return ""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language=language).strip()
    except Exception:
        return ""
