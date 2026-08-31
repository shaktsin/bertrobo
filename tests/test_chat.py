from bertrobo.chat import ChatMessage, ChatSession


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
