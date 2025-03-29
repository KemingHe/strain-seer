from typing import Iterator, Callable
from functools import partial

from chains.types import ChainConfig, ChainInputs


def prepare_chain_response_stream(
    config: ChainConfig,
    get_chain_response_stream: Callable[[ChainConfig, ChainInputs], Iterator[str]],
) -> Callable[[ChainInputs], Iterator[str]]:
    """Creates a configured response stream function that only needs inputs."""
    return partial(get_chain_response_stream, config=config)
