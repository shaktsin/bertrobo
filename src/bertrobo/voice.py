"""Stage 2 voice adapters built on standard Raspberry Pi OS audio tools."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol

from .chat import ChatSession, ConfigurationError


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> str: ...


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, output_path: Path) -> None: ...


class OpenAIAudioClient:
    """OpenAI STT/TTS adapter; imports the SDK only when voice is used."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY is not set")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ConfigurationError("OpenAI SDK is missing; reinstall the project") from error
        self._client = OpenAI(api_key=api_key)
        self._stt_model = os.environ.get("BERTROBO_STT_MODEL", "gpt-4o-mini-transcribe")
        self._tts_model = os.environ.get("BERTROBO_TTS_MODEL", "tts-1")
        self._voice = os.environ.get("BERTROBO_TTS_VOICE", "alloy")

    @classmethod
    def from_environment(cls) -> "OpenAIAudioClient":
        return cls(os.environ.get("OPENAI_API_KEY", ""))

    def transcribe(self, audio_path: Path) -> str:
        try:
            with audio_path.open("rb") as audio_file:
                result = self._client.audio.transcriptions.create(
                    model=self._stt_model, file=audio_file, language="en"
                )
            return result.text.strip()
        except Exception as error:
            raise RuntimeError(str(error)) from error

    def synthesize(self, text: str, output_path: Path) -> None:
        try:
            with self._client.audio.speech.with_streaming_response.create(
                model=self._tts_model,
                voice=self._voice,
                input=text[:4096],
                response_format="wav",
            ) as response:
                response.stream_to_file(output_path)
        except Exception as error:
            raise RuntimeError(str(error)) from error


class AlsaAudio:
    """Record and play WAV audio using Pi OS's arecord and aplay utilities."""

    def __init__(self, capture_seconds: int = 5) -> None:
        if capture_seconds <= 0:
            raise ValueError("capture_seconds must be positive")
        self.capture_seconds = capture_seconds

    def check_available(self) -> None:
        missing = [command for command in ("arecord", "aplay") if shutil.which(command) is None]
        if missing:
            raise ConfigurationError(f"missing Pi audio utility: {', '.join(missing)}")

    def record(self, output_path: Path) -> None:
        self.check_available()
        try:
            subprocess.run(
                ["arecord", "--format=S16_LE", "--rate=16000", "--channels=1", "--duration", str(self.capture_seconds), "--file-type=wav", str(output_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(error.stderr.strip() or "audio recording failed") from error

    def play(self, audio_path: Path) -> None:
        self.check_available()
        try:
            subprocess.run(["aplay", str(audio_path)], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(error.stderr.strip() or "audio playback failed") from error


class VoiceSession:
    """One spoken turn: record → transcribe → chat → synthesize → play."""

    def __init__(self, chat: ChatSession, audio: AlsaAudio, ai_audio: OpenAIAudioClient) -> None:
        self._chat = chat
        self._audio = audio
        self._ai_audio = ai_audio

    def take_turn(self) -> tuple[str, str]:
        with tempfile.TemporaryDirectory(prefix="bertrobo-voice-") as directory:
            root = Path(directory)
            recording = root / "input.wav"
            reply_audio = root / "reply.wav"
            self._audio.record(recording)
            transcript = self._ai_audio.transcribe(recording)
            if not transcript:
                raise RuntimeError("I couldn't hear any speech; try again closer to the microphone")
            reply = self._chat.reply(transcript)
            self._ai_audio.synthesize(reply, reply_audio)
            self._audio.play(reply_audio)
            return transcript, reply
