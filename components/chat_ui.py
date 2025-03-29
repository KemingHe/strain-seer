from typing import List, Callable, Iterator

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from chains.types import ChainInputs


def init_chat_history(history_key: str = "chat_history") -> None:
    if history_key not in st.session_state:
        st.session_state[history_key] = []


def render_chat_messages(messages: List[HumanMessage | AIMessage]) -> None:
    for message in messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("human"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("ai"):
                st.markdown(message.content)
    # Add custom message rendering if needed


def is_valid_query(user_query: str) -> bool:
    return user_query is not None and user_query.strip() != ""


def setup_simple_chat(
    response_stream: Callable[[ChainInputs], Iterator[str]],
) -> None:
    init_chat_history()

    # Alias the chat history from the session state
    chat_history: List[HumanMessage | AIMessage] = st.session_state.chat_history
    render_chat_messages(chat_history)

    # Use the valid user query to get a LangChain response stream
    user_query: str = st.chat_input("I have a question about...")
    if is_valid_query(user_query):
        # Append the user query to the chat history
        chat_history.append(HumanMessage(user_query))

        with st.chat_message("human"):
            st.markdown(user_query)

        with st.chat_message("ai"):
            response_stream = response_stream(
                inputs=ChainInputs(
                    user_query=user_query,
                    chat_history=chat_history,
                ),
            )
            ai_response = st.write_stream(response_stream)

        # Append the full AI response to the chat history
        chat_history.append(AIMessage(ai_response))
