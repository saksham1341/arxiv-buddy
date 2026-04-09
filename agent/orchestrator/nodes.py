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

async def message_history_coverage_checker(state: State, config: RunnableConfig):
    conversation_id = config["configurable"]["thread_id"]  # type: ignore
    output_parser = PydanticOutputParser(pydantic_object=schemas.MessageHistoryCoverageCheckerOutput)
    prompt = prompts.MESSAGE_HISTORY_COVERAGE_CHECKER_PROMPT
    chain = prompt | heavy_llm | output_parser

    resp: schemas.MessageHistoryCoverageCheckerOutput = await chain.ainvoke({
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "TRANSCRIPT": state.message_history,
        "QUERY": state.user_message,
        "CURRENT_CONVERSATION_TITLE": state.current_conversation_title
    })

    # update conversation title change if any
    if resp.new_conversation_title is not None:
        await config["configurable"]["notifications"]["notify_conversation_title_change"](conversation_id, resp.new_conversation_title)  # type: ignore

    updates = {
        # Query understanding
        "is_query_complete": resp.is_query_complete,
        "is_query_resolvable_from_history": resp.is_query_resolvable_from_history,
        "resolved_query": resp.resolved_query,

        # Coverage
        "is_message_history_enough": resp.is_message_history_enough,

        # Retrieval
        "force_new_research": resp.force_new_research,
        "new_query_to_research": resp.new_query_to_research,
        "kb_queries": resp.kb_queries,

        # Final response (only set when appropriate)
        "ai_response": resp.response,

        # New conversation title
        "current_conversation_title": resp.new_conversation_title if resp.new_conversation_title is not None else state.current_conversation_title
    }

    return updates

async def kb_context_fetcher(state: State, config: RunnableConfig):
    if state.is_message_history_enough or not state.kb_queries:
        return

    conversation_id = config["configurable"]["thread_id"]  # type: ignore
    kb_client = config["configurable"]["kb_client"]  # type: ignore
    
    # notify
    await config["configurable"]["notifications"]["notify_gathering_context_call"](conversation_id, state.kb_queries)  # type: ignore

    # gather context
    context = await utils.get_context(kb_client=kb_client, q=state.kb_queries, ids=state.kb_ids)

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
        "QUERY": state.resolved_query
    })

    return {
        "is_kb_context_enough": resp.is_kb_context_enough,
        "new_query_to_research": resp.new_query_to_research,
        "ai_response": resp.response
    }

def new_query_researcher_factory(searcher_agent, learner_agent):
    async def new_query_researcher(state: State, config: RunnableConfig):
        conversation_id = config["configurable"]["thread_id"]  # type: ignore
        arxiv_search_call_semaphore = config["configurable"]["arxiv_search_call_semaphore"]  # type: ignore
        kb_client = config["configurable"]["kb_client"]  # type: ignore
        pdf_parser_pool_executor = config["configurable"]["pdf_parser_pool_executor"]  # type: ignore
        pdf_parser_pool_executor_semaphore = config["configurable"]["pdf_parser_pool_executor_semaphore"]  # type: ignore
        
        # notify searcher
        await config["configurable"]["notifications"]["notify_searcher_call"](conversation_id, state.new_query_to_research)  # type: ignore

        # get article ids to learn
        related_articles = await utils.find_relevant_articles_to_learn(searcher_agent, arxiv_search_call_semaphore, conversation_id, state.new_query_to_research)  # type: ignore
        if len(related_articles) == 0:
            return {
                "query_research_successful": False,
                "ai_response": "I failed to find anything on Arxiv regarding your query."
            }

        article_ids = [article.article_id for article in related_articles]
        
        # notify learner
        await config["configurable"]["notifications"]["notify_learner_call"](conversation_id, article_ids)  # type: ignore

        # learn
        await asyncio.gather(*[utils.learn_article(kb_client, learner_agent, pdf_parser_pool_executor, pdf_parser_pool_executor_semaphore, conversation_id, article) for article in related_articles])

        return {
            "query_research_successful": True,
            "kb_ids": article_ids
        }
    
    return new_query_researcher

async def end_node(state: State, config: RunnableConfig):
    conversation_id = config["configurable"]["thread_id"]  # type: ignore

    # notify ai message
    await config["configurable"]["notifications"]["notify_ai_message"](conversation_id, state.ai_response)  # type: ignore
    
    # notify agent free
    await config["configurable"]["notifications"]["notify_agent_finished"](conversation_id)  # type: ignore
