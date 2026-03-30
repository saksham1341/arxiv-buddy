from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from .state import State
from . import nodes


def build_searcher(name: str):
    builder = StateGraph(State)

    builder.add_node("search_query_generator", nodes.search_query_generator)
    builder.add_node("fetch_articles", nodes.fetch_articles)
    builder.add_node("coverage_decider", nodes.coverage_decider)

    builder.add_edge(START, "search_query_generator")
    builder.add_conditional_edges("search_query_generator", (lambda state: state.attempts_exhausted), {
        True: END,
        False: "fetch_articles"
    })
    builder.add_edge("fetch_articles", "coverage_decider")
    builder.add_conditional_edges("coverage_decider", nodes.should_continue_searching, {
        True: "search_query_generator",
        False: END
    })

    return builder.compile(
        name=name,
        checkpointer=InMemorySaver(),
    )
