from .nodes import fetch_article_content, split_content, generate_embeddable_strings
from .state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


def build_learner(name: str):
    builder = StateGraph(
        state_schema=State
    )

    builder.add_node("fetch_article_content", fetch_article_content)
    builder.add_node("split_article_content", split_content)
    builder.add_node("generate_embeddable_strings", generate_embeddable_strings)

    builder.add_edge(START, "fetch_article_content")
    builder.add_edge("fetch_article_content", "split_article_content")
    builder.add_edge("split_article_content", "generate_embeddable_strings")
    builder.add_edge("generate_embeddable_strings", END)

    return builder.compile(
        name=name,
        checkpointer=InMemorySaver()
    )
