from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import State
from . import nodes


def build_orchestrator(searcher_agent, learner_agent):
    builder = StateGraph(State)

    builder.add_node("start_node", nodes.start_node)
    builder.add_node("mhcc", nodes.message_history_coverage_checker)
    builder.add_node("kbcf", nodes.kb_context_fetcher)
    builder.add_node("kbccc", nodes.kb_context_coverage_checker)
    builder.add_node("nqr" ,nodes.new_query_researcher_factory(searcher_agent=searcher_agent, learner_agent=learner_agent))
    builder.add_node("frg", nodes.final_response_generator)
    builder.add_node("end_node", nodes.end_node)

    builder.add_edge(START, "start_node")
    builder.add_edge("start_node", "mhcc")
    builder.add_conditional_edges("mhcc", (lambda state: state.is_message_history_enough), {
        True: "frg",
        False: "kbcf"
    })
    builder.add_edge("kbcf", "kbccc")
    builder.add_conditional_edges("kbccc", (lambda state: state.is_kb_context_enough), {
        True: "frg",
        False: "nqr"
    })
    builder.add_edge("nqr", "kbcf")
    builder.add_edge("frg", "end_node")
    builder.add_edge("end_node", END)

    return builder.compile(
        checkpointer=InMemorySaver()
    )
