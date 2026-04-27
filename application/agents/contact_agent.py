"""ContactAgentOrchestrator — processes inbound communications and updates CRM records.

Node flow:
  parse_communication → update_contact → log_interaction → END
"""
from typing import Any, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from application.dtos.contact import LogInteractionCommand, UpdateContactRecordCommand
from application.use_cases.contact.log_interaction import LogInteractionUseCase
from application.use_cases.contact.update_contact_record import UpdateContactRecordUseCase


class ContactAgentState(TypedDict):
    raw_communication: str
    parsed_contact: dict[str, Any] | None
    contact_id: UUID | None
    channel: str
    error: str | None


class ContactAgentOrchestrator:

    def __init__(
        self,
        update_contact_uc: UpdateContactRecordUseCase,
        log_interaction_uc: LogInteractionUseCase,
    ) -> None:
        self._update_contact_uc = update_contact_uc
        self._log_interaction_uc = log_interaction_uc
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph: StateGraph = StateGraph(ContactAgentState)
        graph.add_node("parse_communication", self._parse_communication)
        graph.add_node("update_contact", self._update_contact)
        graph.add_node("log_interaction", self._log_interaction)

        graph.set_entry_point("parse_communication")
        graph.add_edge("parse_communication", "update_contact")
        graph.add_edge("update_contact", "log_interaction")
        graph.add_edge("log_interaction", END)

        return graph.compile()

    def _parse_communication(self, state: ContactAgentState) -> ContactAgentState:
        # Placeholder: LLM extracts contact name, email, and interaction summary.
        return {**state, "parsed_contact": None, "error": None}

    def _update_contact(self, state: ContactAgentState) -> ContactAgentState:
        if state.get("parsed_contact"):
            command = UpdateContactRecordCommand(**state["parsed_contact"])
            result = self._update_contact_uc.execute(command)
            return {**state, "contact_id": result.contact_id}
        return state

    def _log_interaction(self, state: ContactAgentState) -> ContactAgentState:
        if state.get("contact_id"):
            self._log_interaction_uc.execute(
                LogInteractionCommand(
                    contact_id=state["contact_id"],  # type: ignore[arg-type]
                    channel=state.get("channel", "unknown"),
                    summary=state.get("raw_communication", ""),
                )
            )
        return state

    def run(self, raw_communication: str, channel: str = "email") -> ContactAgentState:
        initial: ContactAgentState = {
            "raw_communication": raw_communication,
            "parsed_contact": None,
            "contact_id": None,
            "channel": channel,
            "error": None,
        }
        return self._graph.invoke(initial)  # type: ignore[return-value]
