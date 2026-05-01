from uuid import UUID

from django.db.models import Q

from domain.entities.contact import Contact, Interaction
from domain.repositories.contact import ContactRepository, InteractionRepository
from infrastructure.django_app.models.contact import ContactModel, InteractionModel


class DjangoContactRepository(ContactRepository):
    def get_by_id(self, contact_id: UUID) -> Contact | None:
        try:
            record = ContactModel.objects.get(pk=contact_id)
            return self._to_entity(record)
        except ContactModel.DoesNotExist:
            return None

    def save(self, contact: Contact) -> None:
        ContactModel.objects.update_or_create(
            pk=contact.id,
            defaults=self._to_record(contact),
        )

    def list_all(self) -> list[Contact]:
        return [self._to_entity(r) for r in ContactModel.objects.all()]

    def search(self, query: str) -> list[Contact]:
        return [
            self._to_entity(r)
            for r in ContactModel.objects.filter(
                Q(name__icontains=query) | Q(email__icontains=query) | Q(company__icontains=query)
            )
        ]

    @staticmethod
    def _to_entity(record: ContactModel) -> Contact:
        return Contact(
            id=record.id,
            name=record.name,
            email=record.email,
            phone=record.phone,
            company=record.company,
            tags=list(record.tags),
            notes=record.notes,
        )

    @staticmethod
    def _to_record(contact: Contact) -> dict:
        return {
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "tags": list(contact.tags),
            "notes": contact.notes,
        }


class DjangoInteractionRepository(InteractionRepository):
    def save(self, interaction: Interaction) -> None:
        InteractionModel.objects.update_or_create(
            pk=interaction.id,
            defaults={
                "contact_id": interaction.contact_id,
                "channel": interaction.channel,
                "summary": interaction.summary,
                "timestamp": interaction.timestamp,
            },
        )

    def list_by_contact(self, contact_id: UUID) -> list[Interaction]:
        return [
            Interaction(
                id=r.id,
                contact_id=r.contact_id,
                channel=r.channel,
                summary=r.summary,
                timestamp=r.timestamp,
            )
            for r in InteractionModel.objects.filter(contact_id=contact_id).order_by("-timestamp")
        ]
