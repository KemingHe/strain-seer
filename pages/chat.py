from typing import Iterator, Callable

from components.page_ui import setup_page
from components.chat_ui import setup_simple_chat
from factories.response_stream import prepare_chain_response_stream
from chains.web_search import get_multi_web_search_chain_response_stream
from llms.openai import openai_lite_model, openai_regular_model
from chains.types import ChainConfig, ChainInputs

setup_page(
    page_title="(Multi-Task) Web Search Chatbot",
    page_description="This chatbot can perform multi-topic web search and provide relevant information to the user.",
)

# Configure the chain
config = ChainConfig(
    orchestrator_llm=openai_regular_model,
    summarizer_llm=openai_lite_model,
    track_metrics=True,
)

# Prepare the response stream with configuration
response_stream: Callable[[ChainInputs], Iterator[str]] = prepare_chain_response_stream(
    config=config,
    get_chain_response_stream=get_multi_web_search_chain_response_stream,
)

# Setup chat UI with prepared response stream
setup_simple_chat(response_stream)
