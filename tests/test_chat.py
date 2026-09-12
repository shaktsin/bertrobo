from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock
import wave

from bertrobo.chat import ChatMessage, ChatSession
from bertrobo.voice import AlsaAudio, VoiceSession


class FakeClient:
    def __init__(self) -> None:
        self.requests: list[list[ChatMessage]] = []

    def respond(self, messages: list[ChatMessage]) -> str:
        self.requests.append(list(messages))
        return f"reply to: {messages[-1].content}"


def test_session_retains_conversation_context() -> None:
    client = FakeClient()
    session = ChatSession(client)

    assert session.reply("hello") == "reply to: hello"
    assert session.reply("what did I say?") == "reply to: what did I say?"

    assert [message.content for message in client.requests[1]] == [
        "hello",
        "reply to: hello",
        "what did I say?",
    ]


def test_session_bounds_history() -> None:
    client = FakeClient()
    session = ChatSession(client, max_messages=2)

    session.reply("one")
    session.reply("two")

    assert [message.content for message in client.requests[1]] == ["reply to: one", "two"]


class FakeAudio:
    def __init__(self) -> None:
        self.recorded = False
        self.played = False

    def record(self, output_path) -> None:
        self.recorded = True
        output_path.write_bytes(b"wav")

    def play(self, audio_path) -> None:
        self.played = audio_path.exists()

    def has_speech(self, audio_path) -> bool:
        return True

    def play_until_interrupted(self, audio_path, is_interrupt) -> bool:
        self.play(audio_path)
        return False


class FakeAudioAI:
    def transcribe(self, audio_path) -> str:
        assert audio_path.read_bytes() == b"wav"
        return "hello robot"

    def synthesize(self, text: str, output_path) -> None:
        assert text == "reply to: hello robot"
        output_path.write_bytes(b"reply wav")


def test_voice_session_runs_full_turn() -> None:
    mic_and_speaker = FakeAudio()
    voice = VoiceSession(ChatSession(FakeClient()), mic_and_speaker, FakeAudioAI())

    transcript, reply = voice.take_turn()

    assert (transcript, reply) == ("hello robot", "reply to: hello robot")
    assert mic_and_speaker.recorded and mic_and_speaker.played


def test_alsa_audio_uses_explicit_devices() -> None:
    audio = AlsaAudio(capture_device="plughw:3,0", playback_device="plughw:2,0")

    with patch.object(audio, "check_available"), patch("bertrobo.voice.subprocess.run") as run:
        audio.record(Path("/tmp/input.wav"))
        audio.play(Path("/tmp/reply.wav"))

    assert run.call_args_list[0].args[0][:3] == ["arecord", "--device", "plughw:3,0"]
    assert run.call_args_list[1].args[0][:3] == ["aplay", "--device", "plughw:2,0"]


def test_alsa_audio_detects_speech_level_audio(tmp_path) -> None:
    recording = tmp_path / "speech.wav"
    with wave.open(str(recording), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16_000)
        output.writeframes((1_000).to_bytes(2, "little", signed=True) * 16_000)

    assert AlsaAudio(speech_rms_threshold=400).has_speech(recording)
    assert not AlsaAudio(speech_rms_threshold=1_100).has_speech(recording)


def test_voice_session_accepts_a_normalized_wake_phrase() -> None:
    class WakePhraseAI(FakeAudioAI):
        def transcribe(self, audio_path) -> str:
            return "Hey Bert Robo"

    voice = VoiceSession(ChatSession(FakeClient()), FakeAudio(), WakePhraseAI())

    assert voice.wait_for_wake_phrase("hey bert")


def test_alsa_audio_stops_playback_for_an_interrupt() -> None:
    audio = AlsaAudio()
    player = Mock()
    player.poll.return_value = None
    player.wait.return_value = 0

    with (
        patch.object(audio, "check_available"),
        patch.object(audio, "record") as record,
        patch.object(audio, "has_speech", return_value=True),
        patch("bertrobo.voice.subprocess.Popen", return_value=player),
    ):
        assert audio.play_until_interrupted(Path("/tmp/reply.wav"), lambda _: True)

    record.assert_called_once()
    assert record.call_args.kwargs["capture_seconds"] == 1
    player.terminate.assert_called_once()
