from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.contact import Contact, Interaction


class ContactRepository(ABC):
    @abstractmethod
    def get_by_id(self, contact_id: UUID) -> Contact | None: ...

    @abstractmethod
    def save(self, contact: Contact) -> None: ...

    @abstractmethod
    def list_all(self) -> list[Contact]: ...

    @abstractmethod
    def search(self, query: str) -> list[Contact]: ...


class InteractionRepository(ABC):
    @abstractmethod
    def save(self, interaction: Interaction) -> None: ...

    @abstractmethod
    def list_by_contact(self, contact_id: UUID) -> list[Interaction]: ...
