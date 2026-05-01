from application.dtos.calendar import ConflictDetectionResponse, DetectConflictQuery
from domain.repositories.calendar import AppointmentRepository


class DetectConflictUseCase:
    def __init__(self, appointment_repo: AppointmentRepository) -> None:
        self._repo = appointment_repo

    def execute(self, query: DetectConflictQuery) -> ConflictDetectionResponse:
        candidates = self._repo.list_by_range(query.start_time, query.end_time)

        conflicts = [
            a
            for a in candidates
            if a.id != query.exclude_id
            and a.start_time < query.end_time
            and a.end_time > query.start_time
        ]

        return ConflictDetectionResponse(
            has_conflict=bool(conflicts),
            conflicting_ids=[a.id for a in conflicts],
        )
