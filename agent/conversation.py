from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from telephony.interface import TelephonyInterface

SYSTEM_PROMPT = """You are a phone intake agent answering an incoming call on behalf of \
a call-recipient. Your job is to politely gather the following information from the caller \
before ending the call:
- who is calling (name, and company if any)
- the reason for the call, and whether it is a sales/marketing solicitation
- whether the caller has an existing relationship with the person they're calling
- if the caller is soliciting, ask if the recipient would like to be added to the caller's \
do-not-call list, and note the response

Keep responses brief, as in a real phone conversation. Once you have gathered what you need \
(or the caller has nothing more to add), end the call by replying with exactly the token \
[END_CALL] as your entire message."""

END_CALL_TOKEN = "[END_CALL]"


class ConversationAgent:
    """Drives a live call turn-by-turn against a TelephonyInterface."""

    def __init__(self, model: BaseChatModel, max_turns: int = 20):
        self._model = model
        self._max_turns = max_turns

    def run_call(self, channel: TelephonyInterface) -> list[tuple[str, str]]:
        """Runs the call to completion, returning the transcript as (speaker, text) turns."""
        channel.answer()
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        transcript: list[tuple[str, str]] = []

        for _ in range(self._max_turns):
            caller_turn = channel.receive()
            if caller_turn is None:
                break
            messages.append(HumanMessage(content=caller_turn))
            transcript.append(("caller", caller_turn))

            response: AIMessage = self._model.invoke(messages)
            reply_text = response.content if isinstance(response.content, str) else str(response.content)
            messages.append(response)

            if reply_text.strip() == END_CALL_TOKEN:
                break

            channel.send(reply_text)
            transcript.append(("agent", reply_text))

        channel.hangup()
        return transcript


def transcript_to_text(transcript: list[tuple[str, str]]) -> str:
    return "\n".join(f"{speaker}: {text}" for speaker, text in transcript)
