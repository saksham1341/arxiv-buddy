from .nodes import fetch_article_content, semantically_split_content, generate_embeddable_strings
from .state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


builder = StateGraph(
    state_schema=State
)

builder.add_node("fetch_article_content", fetch_article_content)
builder.add_node("semantically_split_content", semantically_split_content)
builder.add_node("generate_embeddable_strings", generate_embeddable_strings)

builder.add_edge(START, "fetch_article_content")
builder.add_edge("fetch_article_content", "semantically_split_content")
builder.add_edge("semantically_split_content", "generate_embeddable_strings")
builder.add_edge("generate_embeddable_strings", END)

agent = builder.compile(
    checkpointer=InMemorySaver()
)
