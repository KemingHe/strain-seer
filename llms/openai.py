from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables import Runnable

from config.envs import (
    OPENAI_API_KEY,
    OPENAI_LITE_MODEL_ID,
    OPENAI_REGULAR_MODEL_ID,
)

openai_embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
openai_lite_model: Runnable = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_LITE_MODEL_ID,
    temperature=0,
)
openai_regular_model: Runnable = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_REGULAR_MODEL_ID,
    temperature=0,
)
