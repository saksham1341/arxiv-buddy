from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import State
from . import nodes


def build_orchestrator(name: str, searcher_agent, learner_agent):
    builder = StateGraph(State)

    builder.add_node("start_node", nodes.start_node)
    builder.add_node("message_history_coverage_checker", nodes.message_history_coverage_checker)
    builder.add_node("kb_context_fetcher", nodes.kb_context_fetcher)
    builder.add_node("kb_context_coverage_checker", nodes.kb_context_coverage_checker)
    builder.add_node("new_topic_researcher" ,nodes.new_query_researcher_factory(searcher_agent=searcher_agent, learner_agent=learner_agent))
    builder.add_node("end_node", nodes.end_node)

    builder.add_edge(START, "start_node")
    builder.add_edge("start_node", "message_history_coverage_checker")
    builder.add_conditional_edges("message_history_coverage_checker", (lambda state: state.is_message_history_enough), {
        True: "end_node",
        False: "kb_context_fetcher"
    })
    builder.add_edge("kb_context_fetcher", "kb_context_coverage_checker")
    builder.add_conditional_edges("kb_context_coverage_checker", (lambda state: state.is_kb_context_enough), {
        True: "end_node",
        False: "new_topic_researcher"
    })
    builder.add_edge("new_topic_researcher", "kb_context_fetcher")
    builder.add_edge("end_node", END)

    return builder.compile(
        name=name,
        checkpointer=InMemorySaver()
    )
