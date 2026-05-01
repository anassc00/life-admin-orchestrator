"""FinanceAgentOrchestrator — processes raw financial documents via a LangGraph graph.

Node flow:
  extract_data → validate_and_persist → END

The agent is intentionally thin: each node delegates to a use case.
LLM calls are isolated to the extract_data node only.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from application.dtos.finance import CreateInvoiceCommand
from application.use_cases.finance.categorize_expense import CategorizeExpenseUseCase
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase


class FinanceAgentState(TypedDict):
    raw_document: str
    extracted_data: dict[str, Any] | None
    error: str | None


class FinanceAgentOrchestrator:
    def __init__(
        self,
        create_invoice_uc: CreateInvoiceUseCase,
        categorize_expense_uc: CategorizeExpenseUseCase,
    ) -> None:
        self._create_invoice_uc = create_invoice_uc
        self._categorize_expense_uc = categorize_expense_uc
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph: StateGraph = StateGraph(FinanceAgentState)
        graph.add_node("extract_data", self._extract_data)
        graph.add_node("validate_and_persist", self._validate_and_persist)
        graph.add_node("handle_error", self._handle_error)

        graph.set_entry_point("extract_data")
        graph.add_conditional_edges(
            "extract_data",
            lambda s: "handle_error" if s.get("error") else "validate_and_persist",
        )
        graph.add_edge("validate_and_persist", END)
        graph.add_edge("handle_error", END)

        return graph.compile()

    def _extract_data(self, state: FinanceAgentState) -> FinanceAgentState:
        """Invoke LLM to extract structured invoice/expense data from raw document.

        In production this node calls an LLM with structured tool use and
        parses the response via an adapter-layer parser.
        """
        # Placeholder: real implementation uses LangChain / Anthropic tool use.
        return {**state, "extracted_data": None, "error": None}

    def _validate_and_persist(self, state: FinanceAgentState) -> FinanceAgentState:
        try:
            if state.get("extracted_data"):
                data = state["extracted_data"]
                command = CreateInvoiceCommand(**data)
                self._create_invoice_uc.execute(command)
            return {**state, "error": None}
        except Exception as exc:
            return {**state, "error": str(exc)}

    def _handle_error(self, state: FinanceAgentState) -> FinanceAgentState:
        # Log or escalate; future hook for human-review notification.
        return state

    def run(self, raw_document: str) -> FinanceAgentState:
        initial: FinanceAgentState = {
            "raw_document": raw_document,
            "extracted_data": None,
            "error": None,
        }
        return self._graph.invoke(initial)  # type: ignore[return-value]
