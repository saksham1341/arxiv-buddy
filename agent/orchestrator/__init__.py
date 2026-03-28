from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import State
from . import nodes


def build_orchestrator(searcher_agent, learner_agent):
    builder = StateGraph(State)

    builder.add_node("start_node", nodes.start_node)
    builder.add_node("message_history_coverage_checker", nodes.message_history_coverage_checker)
    builder.add_node("kb_context_fetcher", nodes.kb_context_fetcher)
    builder.add_node("kb_context_coverage_checker", nodes.kb_context_coverage_checker)
    builder.add_node("new_topic_researcher" ,nodes.new_query_researcher_factory(searcher_agent=searcher_agent, learner_agent=learner_agent))
    builder.add_node("final_response_generator", nodes.final_response_generator)
    builder.add_node("end_node", nodes.end_node)

    builder.add_edge(START, "start_node")
    builder.add_edge("start_node", "message_history_coverage_checker")
    builder.add_conditional_edges("message_history_coverage_checker", (lambda state: state.is_message_history_enough), {
        True: "final_response_generator",
        False: "kb_context_fetcher"
    })
    builder.add_edge("kb_context_fetcher", "kb_context_coverage_checker")
    builder.add_conditional_edges("kb_context_coverage_checker", (lambda state: state.is_kb_context_enough), {
        True: "final_response_generator",
        False: "new_topic_researcher"
    })
    builder.add_edge("new_topic_researcher", "kb_context_fetcher")
    builder.add_edge("final_response_generator", "end_node")
    builder.add_edge("end_node", END)

    return builder.compile(
        checkpointer=InMemorySaver()
    )
