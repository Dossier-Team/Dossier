from pydantic import BaseModel, Field


class Impersonation(BaseModel):
    """Brand identity and how the impersonation was constructed."""

    brand_claimed: str | None = Field(
        default=None,
        description="Company, agency, or brand the caller claimed to represent"
                    " (e.g. 'Microsoft', 'Social Security Administration', 'Amazon').",
    )
    impersonation_details: str | None = Field(
        default=None,
        description="How the impersonation was constructed "
                    "(i.e. claimed department, employee name/ID, spoofed caller ID, fake case/reference number, etc.)",
    )


class ContactMethods(BaseModel):
    """Callback numbers and transfer chain behind the call."""

    callback_numbers: list[str] = Field(
        default_factory=list,
        description="Phone numbers the caller gave for callback,"
                    " transfer, or 'verification', in the order mentioned.",
    )
    transfer_chain_notes: str | None = Field(
        default=None,
        description="Notes on transfers to other people/departments during the call"
                    " (e.g. escalation to a 'supervisor' or 'fraud department').",
    )


class Payment(BaseModel):
    """Payment method demanded and its account-level details."""

    payment_rail_type: str | None = Field(
        default=None,
        description="Type of payment demanded:"
                    " gift_card, wire_transfer, cryptocurrency, payment_app, cash, check, or other.",
    )
    payment_rail_detail: str | None = Field(
        default=None,
        description="Specific account details: wallet address, routing/account number,"
                    " gift card brand and code, payment app handle, mailing address for cash, etc.",
    )
    amount_requested: str | None = Field(
        default=None,
        description="Dollar amount(s) requested, as stated.",
    )


class RemoteAccess(BaseModel):
    """Remote access or other software the caller pushed."""

    remote_access_tool: str | None = Field(
        default=None,
        description=
        "Remote access software the caller tried to get installed"
        " (AnyDesk, TeamViewer, etc.) and what it was framed as being for.",
    )


class PersonalDataExposure(BaseModel):
    """Personal data the scammer already held — feeds the breach-weaponization product."""

    personal_data_recited: list[str] = Field(
        default_factory=list,
        description="Specific pieces of the victim's personal data the scammer already"
                    " had and read back (partial SSN, account number, DOB, address, recent purchase, etc.)"
                    "; signals which breach is currently being worked by phone.",
    )


class Targeting(BaseModel):
    """Lead provenance and who the caller thought they were reaching."""

    lead_list_provenance: str | None = Field(
        default=None,
        description="Any hint of where the caller got this number/lead"
                    " (i.e. mention of a list, a prior 'sign-up', a specific service the victim uses, etc.)",
    )
    target_profile_notes: str | None = Field(
        default=None,
        description="Who the caller seemed to think they were calling"
                    " (e.g. Medicare enrollee, subscriber of a specific service, elderly person living alone).",
    )


class OperationSignals(BaseModel):
    """Scale/structure signals and coercion tactics."""

    operation_structure_notes: str | None = Field(
        default=None,
        description="Signals about the scale/structure of the operation:"
                    " multiple speakers, background call-center noise, scripted hand-offs,"
                    " non-native accents inconsistent with claimed origin, etc.",
    )
    pressure_tactics: list[str] = Field(
        default_factory=list,
        description="Urgency/coercion tactics used, e.g. 'threatened arrest',"
                    " 'account will be closed today', 'claimed legal action pending'.",
    )


class Script(BaseModel):
    """For tracking how live scripts evolve week to week."""

    script_summary: str | None = Field(
        default=None,
        description="Brief summary of the scam narrative/script used,"
                    " for tracking how scripts evolve week to week.",
    )


class CallExtraction(BaseModel):
    """Structured extraction target for LLM-based transcript analysis of scam calls.

    Composed of smaller domain models so each layer (impersonation, payment,
    breach signal, etc.) can be extracted, stored, or reused independently.
    Leave fields as None/[] when the transcript doesn't contain that signal —
    do not fabricate.
    """

    impersonation: Impersonation = Field(default_factory=Impersonation)
    contact_methods: ContactMethods = Field(default_factory=ContactMethods)
    payment: Payment = Field(default_factory=Payment)
    remote_access: RemoteAccess = Field(default_factory=RemoteAccess)
    personal_data_exposure: PersonalDataExposure = Field(default_factory=PersonalDataExposure)
    targeting: Targeting = Field(default_factory=Targeting)
    operation_signals: OperationSignals = Field(default_factory=OperationSignals)
    script: Script = Field(default_factory=Script)