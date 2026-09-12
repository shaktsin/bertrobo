"""Stage 2 voice adapters built on standard Raspberry Pi OS audio tools."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import wave
from collections.abc import Callable
from math import isqrt
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

    def __init__(
        self,
        capture_seconds: int = 5,
        capture_device: str | None = None,
        playback_device: str | None = None,
        speech_rms_threshold: int | None = None,
    ) -> None:
        if capture_seconds <= 0:
            raise ValueError("capture_seconds must be positive")
        self.capture_seconds = capture_seconds
        self.capture_device = capture_device or os.environ.get("BERTROBO_CAPTURE_DEVICE")
        self.playback_device = playback_device or os.environ.get("BERTROBO_PLAYBACK_DEVICE")
        self.speech_rms_threshold = speech_rms_threshold or int(
            os.environ.get("BERTROBO_SPEECH_RMS_THRESHOLD", "400")
        )

    def check_available(self) -> None:
        missing = [command for command in ("arecord", "aplay") if shutil.which(command) is None]
        if missing:
            raise ConfigurationError(f"missing Pi audio utility: {', '.join(missing)}")

    def record(self, output_path: Path, capture_seconds: int | None = None) -> None:
        self.check_available()
        seconds = capture_seconds or self.capture_seconds
        if seconds <= 0:
            raise ValueError("capture_seconds must be positive")
        command = ["arecord"]
        if self.capture_device:
            command.extend(["--device", self.capture_device])
        command.extend(
            [
                "--format=S16_LE",
                "--rate=16000",
                "--channels=1",
                "--duration",
                str(seconds),
                "--file-type=wav",
                str(output_path),
            ]
        )
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(error.stderr.strip() or "audio recording failed") from error

    def play(self, audio_path: Path) -> None:
        self.check_available()
        command = self._play_command(audio_path)
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(error.stderr.strip() or "audio playback failed") from error

    def play_until_interrupted(
        self, audio_path: Path, is_interrupt: Callable[[Path], bool]
    ) -> bool:
        """Play audio while checking the microphone for a deliberate interrupt.

        Returns True after stopping playback for an interrupt, otherwise False.
        """
        self.check_available()
        process = subprocess.Popen(
            self._play_command(audio_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            with tempfile.TemporaryDirectory(prefix="bertrobo-interrupt-") as directory:
                root = Path(directory)
                chunk_number = 0
                while process.poll() is None:
                    chunk = root / f"interrupt-{chunk_number}.wav"
                    chunk_number += 1
                    self.record(chunk, capture_seconds=1)
                    if (
                        process.poll() is None
                        and self.has_speech(chunk)
                        and is_interrupt(chunk)
                    ):
                        process.terminate()
                        process.wait(timeout=2)
                        return True

            exit_code = process.wait()
            if exit_code:
                error = process.stderr.read().strip() if process.stderr else ""
                raise RuntimeError(error or "audio playback failed")
            return False
        except BaseException:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=2)
            raise

    def _play_command(self, audio_path: Path) -> list[str]:
        command = ["aplay"]
        if self.playback_device:
            command.extend(["--device", self.playback_device])
        command.append(str(audio_path))
        return command

    def has_speech(self, audio_path: Path) -> bool:
        """Return whether a 16-bit mono WAV contains speech-level sound."""
        with wave.open(str(audio_path), "rb") as recording:
            if recording.getsampwidth() != 2 or recording.getnchannels() != 1:
                raise RuntimeError("expected a 16-bit mono WAV recording")
            frames = recording.readframes(recording.getnframes())

        if not frames:
            return False
        samples = memoryview(frames).cast("h")
        mean_square = sum(sample * sample for sample in samples) // len(samples)
        return isqrt(mean_square) >= self.speech_rms_threshold


class VoiceSession:
    """One spoken turn: record → transcribe → chat → synthesize → play."""

    def __init__(self, chat: ChatSession, audio: AlsaAudio, ai_audio: OpenAIAudioClient) -> None:
        self._chat = chat
        self._audio = audio
        self._ai_audio = ai_audio
        self.reply_interrupted = False

    def take_turn(self) -> tuple[str, str]:
        with tempfile.TemporaryDirectory(prefix="bertrobo-voice-") as directory:
            root = Path(directory)
            recording = root / "input.wav"
            self._audio.record(recording)
            return self._reply_to_recording(recording, root)

    def take_turn_if_speech(self) -> tuple[str, str] | None:
        """Record one hands-free turn, skipping silence before any API request."""
        with tempfile.TemporaryDirectory(prefix="bertrobo-voice-") as directory:
            root = Path(directory)
            recording = root / "input.wav"
            self._audio.record(recording)
            if not self._audio.has_speech(recording):
                return None
            return self._reply_to_recording(recording, root)

    def wait_for_wake_phrase(self, wake_phrase: str) -> bool:
        """Listen for one spoken wake phrase without adding it to chat history."""
        normalized_phrase = self._normalize_phrase(wake_phrase)
        if not normalized_phrase:
            raise ValueError("wake_phrase must contain letters or numbers")

        with tempfile.TemporaryDirectory(prefix="bertrobo-wake-") as directory:
            recording = Path(directory) / "wake.wav"
            self._audio.record(recording)
            if not self._audio.has_speech(recording):
                return False
            transcript = self._ai_audio.transcribe(recording)
            return normalized_phrase in self._normalize_phrase(transcript)

    def say(self, text: str) -> None:
        """Speak a short acknowledgement without changing chat history."""
        with tempfile.TemporaryDirectory(prefix="bertrobo-voice-") as directory:
            reply_audio = Path(directory) / "acknowledgement.wav"
            self._ai_audio.synthesize(text, reply_audio)
            self._audio.play(reply_audio)

    def _reply_to_recording(self, recording: Path, root: Path) -> tuple[str, str]:
        reply_audio = root / "reply.wav"
        transcript = self._ai_audio.transcribe(recording)
        if not transcript:
            raise RuntimeError("I couldn't hear any speech; try again closer to the microphone")
        reply = self._chat.reply(transcript)
        self._ai_audio.synthesize(reply, reply_audio)
        wake_phrase = os.environ.get("BERTROBO_WAKE_PHRASE", "hey bert")
        self.reply_interrupted = self._audio.play_until_interrupted(
            reply_audio, lambda chunk: self._is_wake_phrase(chunk, wake_phrase)
        )
        return transcript, reply

    def _is_wake_phrase(self, audio_path: Path, wake_phrase: str) -> bool:
        transcript = self._ai_audio.transcribe(audio_path)
        return self._normalize_phrase(wake_phrase) in self._normalize_phrase(transcript)

    @staticmethod
    def _normalize_phrase(text: str) -> str:
        return "".join(character for character in text.casefold() if character.isalnum())
