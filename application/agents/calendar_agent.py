"""CalendarAgentOrchestrator — parses natural-language event requests and schedules appointments.

Node flow:
  parse_event → detect_conflict → schedule → END
"""
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from application.dtos.calendar import DetectConflictQuery, ScheduleAppointmentCommand
from application.use_cases.calendar.detect_conflict import DetectConflictUseCase
from application.use_cases.calendar.schedule_appointment import ScheduleAppointmentUseCase


class CalendarAgentState(TypedDict):
    raw_request: str
    parsed_event: dict[str, Any] | None
    has_conflict: bool
    error: str | None


class CalendarAgentOrchestrator:

    def __init__(
        self,
        detect_conflict_uc: DetectConflictUseCase,
        schedule_appointment_uc: ScheduleAppointmentUseCase,
    ) -> None:
        self._detect_conflict_uc = detect_conflict_uc
        self._schedule_appointment_uc = schedule_appointment_uc
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph: StateGraph = StateGraph(CalendarAgentState)
        graph.add_node("parse_event", self._parse_event)
        graph.add_node("detect_conflict", self._detect_conflict)
        graph.add_node("schedule", self._schedule)
        graph.add_node("handle_conflict", self._handle_conflict)

        graph.set_entry_point("parse_event")
        graph.add_conditional_edges(
            "parse_event",
            lambda s: "handle_conflict" if s.get("error") else "detect_conflict",
        )
        graph.add_conditional_edges(
            "detect_conflict",
            lambda s: "handle_conflict" if s["has_conflict"] else "schedule",
        )
        graph.add_edge("schedule", END)
        graph.add_edge("handle_conflict", END)

        return graph.compile()

    def _parse_event(self, state: CalendarAgentState) -> CalendarAgentState:
        # Placeholder: LLM extracts start_time, end_time, title, etc.
        return {**state, "parsed_event": None, "error": None}

    def _detect_conflict(self, state: CalendarAgentState) -> CalendarAgentState:
        if not state.get("parsed_event"):
            return {**state, "has_conflict": False}
        data = state["parsed_event"]
        query = DetectConflictQuery(
            start_time=data["start_time"],
            end_time=data["end_time"],
        )
        result = self._detect_conflict_uc.execute(query)
        return {**state, "has_conflict": result.has_conflict}

    def _schedule(self, state: CalendarAgentState) -> CalendarAgentState:
        if state.get("parsed_event"):
            command = ScheduleAppointmentCommand(**state["parsed_event"])
            self._schedule_appointment_uc.execute(command)
        return state

    def _handle_conflict(self, state: CalendarAgentState) -> CalendarAgentState:
        return state

    def run(self, raw_request: str) -> CalendarAgentState:
        initial: CalendarAgentState = {
            "raw_request": raw_request,
            "parsed_event": None,
            "has_conflict": False,
            "error": None,
        }
        return self._graph.invoke(initial)  # type: ignore[return-value]
