from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from .state import State
from . import nodes


def build_searcher():
    builder = StateGraph(State)

    builder.add_node("search_query_generator", nodes.search_query_generator)
    builder.add_node("fetch_articles", nodes.fetch_articles)
    builder.add_node("relevance_filter", nodes.relevance_filter)
    builder.add_node("coverage_decider", nodes.coverage_decider)

    builder.add_edge(nodes.START, "search_query_generator")
    builder.add_edge("search_query_generator", "fetch_articles")
    builder.add_edge("fetch_articles", "relevance_filter")
    builder.add_edge("relevance_filter", "coverage_decider")
    builder.add_conditional_edges("coverage_decider", nodes.should_continue_searching, {
        True: "search_query_generator",
        False: nodes.END
    })

    return builder.compile(
        checkpointer=InMemorySaver(),
    )
