from uuid import UUID

from ninja import Router

from adapters.api.contact.schemas import (
    ContactUpdatedResponseSchema,
    InteractionLoggedResponseSchema,
    LogInteractionRequest,
    UpdateContactRecordRequest,
)
from infrastructure.di import (
    get_log_interaction_use_case,
    get_update_contact_record_use_case,
)

router = Router(tags=["Contacts"])


@router.post("/", response=ContactUpdatedResponseSchema)
def create_contact(request, payload: UpdateContactRecordRequest):
    uc = get_update_contact_record_use_case()
    return uc.execute(payload.to_command(contact_id=None)).model_dump()


@router.put("/{contact_id}", response=ContactUpdatedResponseSchema)
def update_contact(request, contact_id: UUID, payload: UpdateContactRecordRequest):
    uc = get_update_contact_record_use_case()
    return uc.execute(payload.to_command(contact_id=contact_id)).model_dump()


@router.post("/{contact_id}/interactions", response=InteractionLoggedResponseSchema)
def log_interaction(request, contact_id: UUID, payload: LogInteractionRequest):
    uc = get_log_interaction_use_case()
    return uc.execute(payload.to_command(contact_id)).model_dump()
