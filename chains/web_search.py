from typing import Iterator, Generator, Optional, Dict
from time import perf_counter
from pprint import pprint
from contextlib import contextmanager
from dataclasses import dataclass, field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from tools.web_search import ddg_text_search
from tools.weather import get_weather_data
from tasks.search import SingleSearchTask, MultiSearchTask
from prompts.single_task import (
    single_task_orchestrator_prompt,
    single_task_orchestrator_parser,
)
from prompts.multi_task import (
    multi_task_orchestrator_prompt,
    multi_task_orchestrator_parser,
)
from prompts.summarizer import summarizer_prompt, simple_summarizer_prompt
from chains.types import ChainConfig, ChainInputs


@dataclass
class StepMetrics:
    step_times: Dict[str, float] = field(default_factory=dict)
    start_time: Optional[float] = None
    enabled: bool = True

    def record_step(self, step_name: str, duration: float) -> None:
        if self.enabled:
            self.step_times[step_name] = duration

    def get_total_time(self) -> float:
        return sum(self.step_times.values())


@contextmanager
def time_block(metrics: StepMetrics, step_name: str) -> Generator[None, None, None]:
    if not metrics.enabled:
        yield
        return

    start: float = perf_counter()
    try:
        yield
    finally:
        duration: float = perf_counter() - start
        metrics.record_step(step_name, duration)


def get_multi_web_search_chain_response_stream(
    config: ChainConfig,
    inputs: ChainInputs,
) -> Iterator[str]:
    orchestrator_llm: Runnable = config.orchestrator_llm
    summarizer_llm: Runnable = config.summarizer_llm
    track_metrics: bool = config.track_metrics
    user_query: str = inputs.user_query
    chat_history: str = inputs.chat_history

    metrics: StepMetrics = StepMetrics(enabled=track_metrics)

    orchestrator_chain: Runnable = (
        multi_task_orchestrator_prompt
        | orchestrator_llm
        | multi_task_orchestrator_parser
    )

    # Orchestration step
    with time_block(metrics, "orchestration"):
        search_task: MultiSearchTask = orchestrator_chain.invoke(
            {
                "user_query": user_query,
                "chat_history": chat_history,
            }
        )
    pprint(f"Search task: {search_task}")
    pprint(
        f"Orchestration step time: {metrics.step_times.get('orchestration', 0):.4f}s"
    )

    # Web search step
    web_search_results: list[str] = []
    with time_block(metrics, "web_search"):
        if search_task.should_search_web:
            for web_task in search_task.web_tasks:
                web_search_results.append(
                    ddg_text_search(
                        query=web_task.query,
                        query_count=web_task.query_count,
                    )
                )
    pprint(f"Web search step time: {metrics.step_times.get('web_search', 0):.4f}s")

    # Weather search step
    weather_search_results: list[str] = []
    with time_block(metrics, "weather_search"):
        if search_task.should_search_weather:
            for weather_task in search_task.weather_tasks:
                weather_search_results.append(
                    get_weather_data(
                        location=weather_task.location,
                    )
                )
    pprint(
        f"Weather search step time: {metrics.step_times.get('weather_search', 0):.4f}s"
    )

    # Summarization step and TTFB tracking
    summarizer_chain: Runnable = summarizer_prompt | summarizer_llm | StrOutputParser()
    chain_start: float = metrics.start_time if track_metrics else None
    summarizer_start: float = perf_counter() if track_metrics else None

    result_stream: Iterator[str] = summarizer_chain.stream(
        {
            "user_query": user_query,
            "chat_history": chat_history,
            "web_search_results": web_search_results,
            "weather_search_results": weather_search_results,
        }
    )

    for chunk in result_stream:
        if track_metrics and summarizer_start:
            ttfb_summarizer = perf_counter() - summarizer_start
            ttfb_invocation = perf_counter() - chain_start if chain_start else 0
            metrics.record_step("ttfb_summarizer", ttfb_summarizer)
            metrics.record_step("ttfb_invocation", ttfb_invocation)
            pprint(f"Time to first byte since summarizer: {ttfb_summarizer:.4f}s")
            pprint(f"Time to first byte since invocation: {ttfb_invocation:.4f}s")
            pprint(f"Total step times: {metrics.get_total_time():.4f}s")
            summarizer_start = None
        yield chunk


def get_single_web_search_chain_response_stream(
    config: ChainConfig,
    inputs: ChainInputs,
) -> Iterator[str]:
    orchestrator_llm: Runnable = config.orchestrator_llm
    summarizer_llm: Runnable = config.summarizer_llm
    track_metrics: bool = config.track_metrics
    user_query: str = inputs.user_query
    chat_history: str = inputs.chat_history

    metrics: StepMetrics = StepMetrics(enabled=track_metrics)

    orchestrator_chain: Runnable = (
        single_task_orchestrator_prompt
        | orchestrator_llm
        | single_task_orchestrator_parser
    )

    # Orchestration step
    with time_block(metrics, "orchestration"):
        search_task: SingleSearchTask = orchestrator_chain.invoke(
            {
                "user_query": user_query,
                "chat_history": chat_history,
            }
        )
    pprint(f"Search task: {search_task}")
    pprint(
        f"Orchestration step time: {metrics.step_times.get('orchestration', 0):.4f}s"
    )

    # Web search step
    web_search_results: str | None = None
    with time_block(metrics, "web_search"):
        if search_task.should_search_web:
            web_search_results = ddg_text_search(
                query=search_task.web_query,
                query_count=search_task.web_query_count,
            )
    pprint(f"Web search step time: {metrics.step_times.get('web_search', 0):.4f}s")

    # Weather search step
    weather_search_results: str | None = None
    with time_block(metrics, "weather_search"):
        if search_task.should_search_weather:
            weather_search_results = get_weather_data(
                location=search_task.weather_query,
            )
    pprint(
        f"Weather search step time: {metrics.step_times.get('weather_search', 0):.4f}s"
    )

    # Summarization step and TTFB tracking
    summarizer_chain: Runnable = summarizer_prompt | summarizer_llm | StrOutputParser()
    chain_start: float = metrics.start_time if track_metrics else None
    summarizer_start: float = perf_counter() if track_metrics else None

    result_stream: Iterator[str] = summarizer_chain.stream(
        {
            "user_query": user_query,
            "chat_history": chat_history,
            "web_search_results": web_search_results,
            "weather_search_results": weather_search_results,
        }
    )

    for chunk in result_stream:
        if track_metrics and summarizer_start:
            ttfb_summarizer = perf_counter() - summarizer_start
            ttfb_invocation = perf_counter() - chain_start if chain_start else 0
            metrics.record_step("ttfb_summarizer", ttfb_summarizer)
            metrics.record_step("ttfb_invocation", ttfb_invocation)
            pprint(f"Time to first byte since summarizer: {ttfb_summarizer:.4f}s")
            pprint(f"Time to first byte since invocation: {ttfb_invocation:.4f}s")
            pprint(f"Total step times: {metrics.get_total_time():.4f}s")
            summarizer_start = None
        yield chunk


def get_simple_chain_response_stream(
    config: ChainConfig,
    inputs: ChainInputs,
) -> Iterator[str]:
    summarizer_llm: Runnable = config.summarizer_llm
    track_metrics: bool = config.track_metrics
    user_query: str = inputs.user_query
    chat_history: str = inputs.chat_history

    metrics: StepMetrics = StepMetrics(enabled=track_metrics)

    # Summarization step and TTFB tracking
    simple_summarizer_chain: Runnable = (
        simple_summarizer_prompt | summarizer_llm | StrOutputParser()
    )
    chain_start: float = metrics.start_time if track_metrics else None
    summarizer_start: float = perf_counter() if track_metrics else None

    result_stream: Iterator[str] = simple_summarizer_chain.stream(
        {
            "user_query": user_query,
            "chat_history": chat_history,
        }
    )

    for chunk in result_stream:
        if track_metrics and summarizer_start:
            ttfb_summarizer = perf_counter() - summarizer_start
            ttfb_invocation = perf_counter() - chain_start if chain_start else 0
            metrics.record_step("ttfb_summarizer", ttfb_summarizer)
            metrics.record_step("ttfb_invocation", ttfb_invocation)
            pprint(f"Time to first byte since summarizer: {ttfb_summarizer:.4f}s")
            pprint(f"Time to first byte since invocation: {ttfb_invocation:.4f}s")
            pprint(f"Total step times: {metrics.get_total_time():.4f}s")
            summarizer_start = None
        yield chunk
