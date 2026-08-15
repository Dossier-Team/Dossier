from langchain_core.tools import tool


@tool
def end_call() -> str:
    """End the current phone call.

    Call this once you have gathered what you need from the caller, or the
    caller has nothing more to add.
    """
    return "call ended"
