from uuid import UUID


class ContactNotFoundError(Exception):
    def __init__(self, contact_id: UUID) -> None:
        super().__init__(f"Contact {contact_id} not found")
        self.contact_id = contact_id
