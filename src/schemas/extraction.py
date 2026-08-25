from pydantic import BaseModel


class CallExtraction(BaseModel):
    """Structured extraction target for LLM-based transcript analysis.

    Fields mirror the ranked elicitation objectives in plan.md ("Agent layer" section):
    brand identity, contact/transfer infrastructure, payment rails, tooling,
    lead-list provenance, and operation structure. Left as None when the
    transcript doesn't contain that signal — do not fabricate.
    """

    brand_claimed: str | None = None
    callback_number: str | None = None
    payment_rail_type: str | None = None
    payment_rail_detail: str | None = None
    remote_access_tool: str | None = None
    lead_list_provenance: str | None = None
    operation_structure_notes: str | None = None
