from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import PydanticOutputParser
from .state import State
from ..llm import heavy_llm
from . import prompts, schemas, utils
import asyncio


async def start_node(state: State, config: RunnableConfig):
    conversation_id = config["configurable"]["thread_id"]  # type: ignore
    
    # notify agent busy
    await config["configurable"]["notifications"]["notify_agent_start"](conversation_id)  # type: ignore

    # notify user message
    await config["configurable"]["notifications"]["notify_user_message"](conversation_id, state.user_message)  # type: ignore

async def message_history_coverage_checker(state: State):
    # check if message history is enough to answer user query
    output_parser = PydanticOutputParser(pydantic_object=schemas.MessageHistoryCoverageCheckerOutput)
    prompt = prompts.MESSAGE_HISTORY_COVERAGE_CHECKER_PROMPT

    chain = prompt | heavy_llm | output_parser

    resp = await chain.ainvoke({
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "TRANSCRIPT": state.message_history,
        "QUERY": state.user_message
    })

    return {
        "is_message_history_enough": resp.is_message_history_enough,
        "kb_queries": resp.kb_queries
    }

async def kb_context_fetcher(state: State, config: RunnableConfig):
    if state.is_message_history_enough or not state.kb_queries:
        return

    conversation_id = config["configurable"]["thread_id"]  # type: ignore
    kb_client = config["configurable"]["kb_client"]  # type: ignore
    arxiv_api_client = config["configurable"]["arxiv_api_client"]  # type: ignore

    # notify
    await config["configurable"]["notifications"]["notify_gathering_context_call"](conversation_id, state.kb_queries)  # type: ignore

    # gather context
    context = await utils.get_context(kb_client=kb_client, arxiv_api_client=arxiv_api_client, q=state.kb_queries)

    return {
        "kb_context": context
    }

async def kb_context_coverage_checker(state: State):
    # check if knowledge base context is enough to answer user query
    output_parser = PydanticOutputParser(pydantic_object=schemas.KBContextCoverageCheckerOutput)
    prompt = prompts.KNOWLEDGE_BASE_CONTEXT_COVERAGE_CHECKER_PROMPT

    chain = prompt | heavy_llm | output_parser

    resp = await chain.ainvoke({
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "CONTEXT": state.kb_context,
        "QUERY": state.user_message
    })

    return {
        "is_kb_context_enough": resp.is_kb_context_enough,
        "new_query_to_research": resp.new_query_to_research
    }

def new_query_researcher_factory(searcher_agent, learner_agent):
    async def new_query_researcher(state: State, config: RunnableConfig):
        if state.is_kb_context_enough or not state.new_query_to_research:
            return

        conversation_id = config["configurable"]["thread_id"]  # type: ignore
        arxiv_api_client = config["configurable"]["arxiv_api_client"]  # type: ignore
        kb_client = config["configurable"]["kb_client"]  # type: ignore
        
        # notify searcher
        await config["configurable"]["notifications"]["notify_searcher_call"](conversation_id, state.new_query_to_research)  # type: ignore

        # get article ids to learn
        related_articles = await utils.find_relevant_articles_to_learn(arxiv_api_client, searcher_agent, conversation_id, state.new_query_to_research)
        article_ids = list(related_articles.keys())
        
        # notify learner
        await config["configurable"]["notifications"]["notify_learner_call"](conversation_id, article_ids)  # type: ignore

        # learn
        await asyncio.gather(*[utils.learn_article(kb_client, learner_agent, conversation_id, k) for k in article_ids])
    
    return new_query_researcher

async def final_response_generator(state: State):
    # generate the final response
    output_parser = PydanticOutputParser(pydantic_object=schemas.FinalResponseOutput)
    prompt = prompts.FINAL_RESPONSE_GENERATOR_PROMPT

    chain = prompt | heavy_llm | output_parser

    resp = await chain.ainvoke({
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "TRANSCRIPT": state.message_history,
        "CONTEXT": state.kb_context,
        "QUERY": state.user_message
    })

    return {
        "ai_message": resp.response
    }

async def end_node(state: State, config: RunnableConfig):
    conversation_id = config["configurable"]["thread_id"]  # type: ignore

    # notify ai message
    await config["configurable"]["notifications"]["notify_ai_message"](conversation_id, state.ai_response)  # type: ignore
    
    # notify agent free
    await config["configurable"]["notifications"]["notify_agent_finished"](conversation_id)  # type: ignore
