from datetime import datetime, timezone

from domain.entities.contact import Interaction
from domain.exceptions.contact import ContactNotFoundError
from domain.repositories.contact import ContactRepository, InteractionRepository
from application.dtos.contact import InteractionLoggedResponse, LogInteractionCommand


class LogInteractionUseCase:

    def __init__(
        self,
        contact_repo: ContactRepository,
        interaction_repo: InteractionRepository,
    ) -> None:
        self._contact_repo = contact_repo
        self._interaction_repo = interaction_repo

    def execute(self, command: LogInteractionCommand) -> InteractionLoggedResponse:
        contact = self._contact_repo.get_by_id(command.contact_id)
        if contact is None:
            raise ContactNotFoundError(command.contact_id)

        interaction = Interaction(
            contact_id=command.contact_id,
            channel=command.channel,
            summary=command.summary,
            timestamp=command.timestamp or datetime.now(timezone.utc),
        )
        self._interaction_repo.save(interaction)
        return InteractionLoggedResponse(
            interaction_id=interaction.id,
            contact_id=interaction.contact_id,
        )
