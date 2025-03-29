import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from llms.openai import openai_lite_model, openai_regular_model
from components.chat_ui import init_chat_history, is_valid_query
from chains.types import ChainInputs, ChainConfig
from chains.web_search import (
    get_simple_chain_response_stream,
    get_single_web_search_chain_response_stream,
    get_multi_web_search_chain_response_stream,
)
from components.page_ui import setup_page

setup_page(
    app_layout="wide",
    page_title="Chat Comparison",
    page_description="This page demonstrates the difference between a basic chatbot, a single-task web search chatbot, and a multi-task web search chatbot.",
)

init_chat_history("simple_chat_history")
simple_chat_history = st.session_state.simple_chat_history

init_chat_history("single_web_search_chat_history")
single_web_search_chat_history = st.session_state.single_web_search_chat_history

init_chat_history("multi_web_search_chat_history")
multi_web_search_chat_history = st.session_state.multi_web_search_chat_history

# Configure the chain
config = ChainConfig(
    orchestrator_llm=openai_regular_model,
    summarizer_llm=openai_lite_model,
    track_metrics=True,
)

demo_container = st.container()
with demo_container:
    user_query = st.chat_input("I have a question about...")
    if is_valid_query(user_query):
        # Add user message to chat histories
        simple_chat_history.append(HumanMessage(user_query))
        single_web_search_chat_history.append(HumanMessage(user_query))
        multi_web_search_chat_history.append(HumanMessage(user_query))

        # Create columns for displaying streaming responses
        simple_res_col, single_web_res_col, multi_web_res_col = st.columns(3)

        with simple_res_col:
            st.header("Basic Chat")
            with st.chat_message("human"):
                st.markdown(user_query)
            with st.chat_message("ai"):
                simple_response = st.write_stream(
                    get_simple_chain_response_stream(
                        config=config,
                        inputs=ChainInputs(
                            user_query=user_query,
                            chat_history=simple_chat_history,
                        ),
                    )
                )
                simple_chat_history.append(AIMessage(simple_response))

        with single_web_res_col:
            st.header("(Single-Task) Web Search Chat")
            with st.chat_message("human"):
                st.markdown(user_query)
            with st.chat_message("ai"):
                web_response = st.write_stream(
                    get_single_web_search_chain_response_stream(
                        config=config,
                        inputs=ChainInputs(
                            user_query=user_query,
                            chat_history=simple_chat_history,
                        ),
                    )
                )
                single_web_search_chat_history.append(AIMessage(web_response))

        with multi_web_res_col:
            st.header("(Multi-Task) Web Search Chat")
            with st.chat_message("human"):
                st.markdown(user_query)
            with st.chat_message("ai"):
                multi_web_response = st.write_stream(
                    get_multi_web_search_chain_response_stream(
                        config=config,
                        inputs=ChainInputs(
                            user_query=user_query,
                            chat_history=simple_chat_history,
                        ),
                    )
                )
                multi_web_search_chat_history.append(AIMessage(multi_web_response))
