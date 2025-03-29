from pydantic import BaseModel, Field


class SingleSearchTask(BaseModel):
    should_search_web: bool = Field(
        description="Set to true if factual information needs to be searched online"
    )
    should_search_weather: bool = Field(
        description="Set to true if weather information for a specific location is requested"
    )
    web_query: str = Field(
        description="Search query for web results. Must be precise and include key terms. Empty if no search needed"
    )
    web_query_count: int = Field(
        description="Number of web results to fetch (3-10 recommended). Must be 0 if no search needed"
    )
    weather_query: str = Field(
        description="Location name for weather search. Must be specific and unambiguous. Empty if no weather needed"
    )


class WebTextSearchTask(BaseModel):
    query: str = Field(
        description="Specific search query focusing on factual information. Include key terms, entities, and time frame if relevant. Example: 'current CEO of Apple' or 'SpaceX Starship latest launch date'",
        min_length=3,
        max_length=200,
    )
    query_count: int = Field(
        default=3,
        description="Number of web results to fetch. Use 3 for basic facts, 5-10 for complex topics requiring multiple sources",
        ge=3,
        le=10,
    )


class WeatherSearchTask(BaseModel):
    location: str = Field(
        description="Full location name with city and country/state if needed to avoid ambiguity. Example: 'San Francisco, CA' or 'Paris, France'",
        min_length=2,
        max_length=100,
    )


class MultiSearchTask(BaseModel):
    should_search_web: bool = Field(
        description="Set to true if factual or real-time information needs to be searched online"
    )
    web_tasks: list[WebTextSearchTask] = Field(
        default=[],
        description="List of distinct web searches. Must be empty if should_search_web is false. Each task should focus on a single specific topic",
        max_length=5,
    )
    should_search_weather: bool = Field(
        description="Set to true if weather information for a specific location is requested"
    )
    weather_tasks: list[WeatherSearchTask] = Field(
        default=[],
        description="List of locations to get weather information from. Must be empty if should_search_weather is false. Each task should be for a unique location",
        max_length=3,
    )
