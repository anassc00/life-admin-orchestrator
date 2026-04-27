from domain.entities.contact import Contact
from domain.exceptions.contact import ContactNotFoundError
from domain.repositories.contact import ContactRepository
from application.dtos.contact import ContactUpdatedResponse, UpdateContactRecordCommand


class UpdateContactRecordUseCase:

    def __init__(self, contact_repo: ContactRepository) -> None:
        self._repo = contact_repo

    def execute(self, command: UpdateContactRecordCommand) -> ContactUpdatedResponse:
        if command.contact_id is not None:
            existing = self._repo.get_by_id(command.contact_id)
            if existing is None:
                raise ContactNotFoundError(command.contact_id)
            contact = existing.model_copy(
                update={
                    "name": command.name,
                    "email": command.email,
                    "phone": command.phone,
                    "company": command.company,
                    "tags": command.tags,
                    "notes": command.notes,
                }
            )
        else:
            contact = Contact(
                name=command.name,
                email=command.email,
                phone=command.phone,
                company=command.company,
                tags=command.tags,
                notes=command.notes,
            )

        self._repo.save(contact)
        return ContactUpdatedResponse(contact_id=contact.id, name=contact.name)
