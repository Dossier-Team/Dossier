from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.schemas.extraction import CallExtraction
from src.llm import get_llm

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are analyzing a transcript of a phone call with a suspected scammer. "
     "Extract only information explicitly present in the transcript. "
     "Leave fields as None when the transcript doesn't contain that signal — do not fabricate."),
    ("human", "Transcript:\n{transcript}"),
])


def extract_call_info(transcript: list, schema: type[BaseModel] = CallExtraction) -> BaseModel:
    """Extract structured intel from a call transcript into the given schema.

    The target schema is a parameter (not hardcoded) so extracting into a
    different model later is a call-site change rather than a rewrite here.
    Prompt, model, and output schema are each independently swappable pieces
    composed here via LCEL.
    """

    chain = EXTRACTION_PROMPT | get_llm().with_structured_output(schema)
    return chain.invoke({"transcript": transcript})
