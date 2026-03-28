from .nodes import fetch_article_content, split_content, generate_embeddable_strings
from .state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


def build_learner():
    builder = StateGraph(
        state_schema=State
    )

    builder.add_node("fac", fetch_article_content)
    builder.add_node("sc", split_content)
    builder.add_node("ges", generate_embeddable_strings)

    builder.add_edge(START, "fac")
    builder.add_edge("fac", "sc")
    builder.add_edge("sc", "ges")
    builder.add_edge("ges", END)

    return builder.compile(
        checkpointer=InMemorySaver()
    )
