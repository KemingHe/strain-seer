from dataclasses import dataclass

from langchain_core.runnables import Runnable


@dataclass(frozen=True)
class ChainConfig:
    orchestrator_llm: Runnable
    summarizer_llm: Runnable
    track_metrics: bool = True


@dataclass(frozen=True)
class ChainInputs:
    user_query: str
    chat_history: str
