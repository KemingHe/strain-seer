# Structured Chain Alternatives in LangChain

(From GitHub Copilot Chat) Yes, you can create a structured chain instead of using structured LLMs. Here are two approaches:

## 1. Using LCEL (LangChain Expression Language) with Pydantic Parser

```python
from langchain_core.output_parsers import PydanticOutputParser

# ...existing code...

# Replace the structured_llm definition with this chain
orchestrator_parser = PydanticOutputParser(pydantic_object=SearchTask)
orchestrator_chain = (
    orchastrator_prompt 
    | openai_regular_model 
    | orchestrator_parser
)

def get_response_stream(
    user_query: str,
    chat_history: str,
) -> Iterator[str]:
    search_task = orchestrator_chain.invoke({
        "chat_history": chat_history,
        "user_query": user_query,
    })
    # ...rest of the code remains the same...
```

## 2. Using RunnableSequence for More Complex Chains

For more complex scenarios where you need multiple structured outputs:

```python
from langchain_core.runnables import RunnableSequence
from typing import Dict, Any

class SearchResult(BaseModel):
    results: list[str]
    metadata: Dict[str, Any]

def create_orchestrator_chain() -> RunnableSequence:
    parser = PydanticOutputParser(pydantic_object=SearchTask)
    
    return RunnableSequence(
        first = orchastrator_prompt | openai_regular_model | parser,
        second = lambda x: SearchResult(
            results=simple_search(x.query, x.count) if x.shoud_run else [],
            metadata={"searched": x.shoud_run}
        )
    )

# Usage in get_response_stream:
orchestrator_chain = create_orchestrator_chain()
search_results = orchestrator_chain.invoke({
    "chat_history": chat_history,
    "user_query": user_query,
})
```

## Best Practices

1. **LCEL Approach**: Use LCEL with `PydanticOutputParser` for simple structured outputs. This is the most maintainable and readable approach.

2. **RunnableSequence**: For complex workflows where you need:
   - Multiple structured outputs
   - Conditional branching
   - Error handling
   - Custom transformations

3. **Composability**: Break down complex chains into smaller, reusable components:

```python
class QueryAnalysis(BaseModel):
    intent: str
    complexity: int
    required_tools: list[str]

def create_modular_chain():
    analysis_chain = (
        analysis_prompt 
        | openai_regular_model 
        | PydanticOutputParser(pydantic_object=QueryAnalysis)
    )
    
    search_chain = (
        search_prompt 
        | openai_regular_model 
        | PydanticOutputParser(pydantic_object=SearchTask)
    )
    
    return RunnableSequence(
        first=analysis_chain,
        second=lambda x: search_chain if x.complexity > 3 else None
    )
```

The LCEL approach with `PydanticOutputParser` is generally the most maintainable solution unless you have specific requirements that necessitate more complex chains.
