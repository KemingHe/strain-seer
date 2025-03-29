from os import getenv
from warnings import warn

from dotenv import load_dotenv


def validate_env(env_name: str) -> str:
    """
    Validate that an environment variable exists and is not empty

    Args:
        env_name: Name of the environment variable to validate

    Returns:
        The validated environment variable value

    Raises:
        ValueError: If the environment variable is missing or invalid
    """
    value = getenv(env_name)

    if not isinstance(value, str):
        raise ValueError(f"Environment variable {env_name} must be a string")

    if not value or value.strip() == "":
        raise ValueError(f"Environment variable {env_name} cannot be empty")

    return value


# Verify .env file is correctly loaded
if not load_dotenv():
    warn("No .env file found, assuming environment variables are injected")

# OpenAI configuration
OPENAI_API_KEY = validate_env("OPENAI_API_KEY")
OPENAI_LITE_MODEL_ID = validate_env("OPENAI_LITE_MODEL_ID")
OPENAI_REGULAR_MODEL_ID = validate_env("OPENAI_REGULAR_MODEL_ID")

# Pinecone configuration
PINECONE_API_KEY = validate_env("PINECONE_API_KEY")
PINECONE_INDEX_NAME = validate_env("PINECONE_INDEX_NAME")

# WeatherAPI configuration
WEATHERAPI_API_KEY = validate_env("WEATHERAPI_API_KEY")
