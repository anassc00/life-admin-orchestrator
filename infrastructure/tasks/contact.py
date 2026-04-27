from celery import shared_task

from infrastructure.di import (
    get_log_interaction_use_case,
    get_update_contact_record_use_case,
)


@shared_task(name="tasks.contact.process_communication", bind=True, max_retries=3)
def process_communication_task(self, raw_communication: str, channel: str = "email") -> dict:
    """Parse an inbound communication and update/create the contact record."""
    from application.agents.contact_agent import ContactAgentOrchestrator

    agent = ContactAgentOrchestrator(
        update_contact_uc=get_update_contact_record_use_case(),
        log_interaction_uc=get_log_interaction_use_case(),
    )
    result = agent.run(raw_communication=raw_communication, channel=channel)
    return {"contact_id": str(result.get("contact_id")), "error": result.get("error")}
