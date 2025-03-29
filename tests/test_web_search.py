from time import perf_counter
from typing import Iterator, Dict
from dataclasses import dataclass

import pytest
from langchain_core.runnables import Runnable

from prompts.multi_task import (
    multi_task_orchestrator_prompt,
    multi_task_orchestrator_parser,
)
from prompts.single_task import (
    single_task_orchestrator_prompt,
    single_task_orchestrator_parser,
)
from llms.openai import openai_regular_model, openai_lite_model
from chains.web_search import (
    StepMetrics,
    get_simple_chain_response_stream,
    get_single_web_search_chain_response_stream,
    get_multi_web_search_chain_response_stream,
)
from chains.types import ChainConfig, ChainInputs


@dataclass
class BenchmarkMetrics:
    """Tracks detailed performance metrics for benchmarking."""

    step_times: Dict[str, float]
    total_time: float
    ttfb_orchestration: float


@pytest.fixture
def chain_config_regular_lite():
    return ChainConfig(
        orchestrator_llm=openai_regular_model,
        summarizer_llm=openai_lite_model,
        track_metrics=True,
    )


@pytest.fixture
def chain_config_regular_regular():
    return ChainConfig(
        orchestrator_llm=openai_regular_model,
        summarizer_llm=openai_regular_model,
        track_metrics=True,
    )


@pytest.fixture
def chain_inputs():
    return ChainInputs(
        user_query="What's current weather in Beijing and Wuhan?",
        chat_history="",
    )


@pytest.mark.benchmark(
    group="chains-ttfb-invocation",
    min_rounds=10,
    max_time=0.5,
    warmup=False,
    timer=perf_counter,
)
def test_multi_web_search_chain_benchmark_regular_lite(
    benchmark, chain_config_regular_lite, chain_inputs
):
    def run_benchmarked_chain():
        metrics: StepMetrics = StepMetrics(enabled=True)
        result_iterator: Iterator[str] = get_multi_web_search_chain_response_stream(
            config=chain_config_regular_lite, inputs=chain_inputs
        )
        # Only consume first item to measure TTFB since invocation
        next(result_iterator, None)
        return metrics.step_times.get("ttfb_invocation", 0)

    benchmark(run_benchmarked_chain)


@pytest.mark.benchmark(
    group="chains-ttfb-invocation",
    min_rounds=10,
    max_time=0.5,
    warmup=False,
    timer=perf_counter,
)
def test_single_web_search_chain_benchmark_regular_lite(
    benchmark, chain_config_regular_lite, chain_inputs
):
    def run_benchmarked_chain():
        metrics: StepMetrics = StepMetrics(enabled=True)
        result_iterator: Iterator[str] = get_single_web_search_chain_response_stream(
            config=chain_config_regular_lite, inputs=chain_inputs
        )
        # Only consume first item to measure TTFB since invocation
        next(result_iterator, None)
        return metrics.step_times.get("ttfb_invocation", 0)

    benchmark(run_benchmarked_chain)


@pytest.mark.benchmark(
    group="chains-ttfb-invocation",
    min_rounds=10,
    max_time=0.5,
    warmup=False,
    timer=perf_counter,
)
def test_simple_chain_benchmark_regular_lite(
    benchmark, chain_config_regular_lite, chain_inputs
):
    def run_benchmarked_chain():
        metrics: StepMetrics = StepMetrics(enabled=True)
        result_iterator: Iterator[str] = get_simple_chain_response_stream(
            config=chain_config_regular_lite, inputs=chain_inputs
        )
        # Only consume first item to measure TTFB since invocation
        next(result_iterator, None)
        return metrics.step_times.get("ttfb_invocation", 0)

    benchmark(run_benchmarked_chain)


@pytest.mark.benchmark(
    group="chains-orchestration",
    min_rounds=10,
    max_time=0.5,
    warmup=False,
    timer=perf_counter,
)
def test_multi_web_search_orchestration_benchmark_regular(benchmark, chain_inputs):
    def run_benchmarked_orchestration():
        orchestrator_llm: Runnable = openai_regular_model
        orchestrator_chain: Runnable = (
            multi_task_orchestrator_prompt
            | orchestrator_llm
            | multi_task_orchestrator_parser
        )
        orchestrator_chain.invoke(
            {
                "user_query": chain_inputs.user_query,
                "chat_history": chain_inputs.chat_history,
            }
        )

    benchmark(run_benchmarked_orchestration)


@pytest.mark.benchmark(
    group="chains-orchestration",
    min_rounds=10,
    max_time=0.5,
    warmup=False,
    timer=perf_counter,
)
def test_single_web_search_orchestration_benchmark_regular(benchmark, chain_inputs):
    def run_benchmarked_orchestration():
        orchestrator_llm: Runnable = openai_regular_model
        orchestrator_chain: Runnable = (
            single_task_orchestrator_prompt
            | orchestrator_llm
            | single_task_orchestrator_parser
        )
        orchestrator_chain.invoke(
            {
                "user_query": chain_inputs.user_query,
                "chat_history": chain_inputs.chat_history,
            }
        )

    benchmark(run_benchmarked_orchestration)
