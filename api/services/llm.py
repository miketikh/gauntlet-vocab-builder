"""
LLM Service for AI-powered vocabulary recommendations.

This module provides a singleton pattern for accessing LangChain's ChatOpenAI
instance with configuration from environment variables.
"""

import os
from typing import Optional
from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from openai import OpenAIError, AuthenticationError, RateLimitError, APITimeoutError

from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """Settings for LLM configuration."""

    openai_api_key: str
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3
    llm_timeout: int = 30  # seconds
    llm_max_retries: int = 3

    # Optional: For OpenRouter support
    openai_api_base: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_llm_settings() -> LLMSettings:
    """
    Get LLM settings from environment variables.
    Cached to avoid repeated environment variable reads.
    """
    return LLMSettings()


# Singleton instance
_llm_instance: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """
    Get or create the singleton ChatOpenAI instance.

    Returns:
        ChatOpenAI: Configured LangChain ChatOpenAI instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_llm_settings()

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )

        # Initialize ChatOpenAI with settings
        kwargs = {
            "model": settings.llm_model,
            "temperature": settings.llm_temperature,
            "openai_api_key": settings.openai_api_key,
            "timeout": settings.llm_timeout,
            "max_retries": settings.llm_max_retries,
        }

        # Add base URL if specified (for OpenRouter support)
        if settings.openai_api_base:
            kwargs["openai_api_base"] = settings.openai_api_base

        _llm_instance = ChatOpenAI(**kwargs)

    return _llm_instance


def reset_llm() -> None:
    """
    Reset the singleton LLM instance and clear cached settings.
    Useful for testing or switching configurations.
    """
    global _llm_instance
    _llm_instance = None
    # Clear the settings cache so new environment variables are loaded
    get_llm_settings.cache_clear()


async def test_llm_connection() -> dict:
    """
    Test the LLM connection with a simple prompt.

    Returns:
        dict: Result containing success status, response, and metadata

    Example:
        {
            "success": True,
            "response": "Hello! I'm working correctly.",
            "model": "gpt-4o-mini",
            "tokens_used": 25,
            "error": None
        }
    """
    try:
        llm = get_llm()
        settings = get_llm_settings()

        # Simple test prompt
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Reply with 'Connection successful!' if you receive this message.")
        ]

        # Invoke the LLM
        response = await llm.ainvoke(messages)

        # Extract token usage if available
        tokens_used = None
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            tokens_used = usage.get("total_tokens")

        return {
            "success": True,
            "response": response.content,
            "model": settings.llm_model,
            "tokens_used": tokens_used,
            "error": None
        }

    except AuthenticationError as e:
        return {
            "success": False,
            "response": None,
            "model": None,
            "tokens_used": None,
            "error": f"Authentication failed: {str(e)}. Check your OPENAI_API_KEY."
        }

    except RateLimitError as e:
        return {
            "success": False,
            "response": None,
            "model": None,
            "tokens_used": None,
            "error": f"Rate limit exceeded: {str(e)}. Please try again later."
        }

    except APITimeoutError as e:
        return {
            "success": False,
            "response": None,
            "model": None,
            "tokens_used": None,
            "error": f"Request timed out: {str(e)}. The API is taking too long to respond."
        }

    except OpenAIError as e:
        return {
            "success": False,
            "response": None,
            "model": None,
            "tokens_used": None,
            "error": f"OpenAI API error: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "response": None,
            "model": None,
            "tokens_used": None,
            "error": f"Unexpected error: {str(e)}"
        }


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> float:
    """
    Estimate the cost of an LLM request based on token usage.

    Pricing as of November 2024:
    - gpt-4o-mini: $0.150 per 1M input tokens, $0.600 per 1M output tokens
    - gpt-4: $30.00 per 1M input tokens, $60.00 per 1M output tokens

    Args:
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        model: Model name

    Returns:
        float: Estimated cost in USD
    """
    # Pricing per million tokens (as of Nov 2024)
    pricing = {
        "gpt-4o-mini": {
            "input": 0.150,  # per 1M tokens
            "output": 0.600,  # per 1M tokens
        },
        "gpt-4": {
            "input": 30.00,
            "output": 60.00,
        },
        "gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00,
        },
    }

    # Default to gpt-4o-mini if model not found
    model_pricing = pricing.get(model, pricing["gpt-4o-mini"])

    # Calculate cost
    input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]

    return input_cost + output_cost


class TokenTracker:
    """
    Simple token usage tracker for monitoring LLM costs.
    """

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0

    def add_usage(self, prompt_tokens: int, completion_tokens: int):
        """Add token usage to the tracker."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_requests += 1

    def get_stats(self, model: str = "gpt-4o-mini") -> dict:
        """
        Get usage statistics and estimated cost.

        Returns:
            dict: Usage statistics including total tokens and estimated cost
        """
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        estimated_cost = estimate_cost(
            self.total_prompt_tokens,
            self.total_completion_tokens,
            model
        )

        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
        }

    def reset(self):
        """Reset all counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0


# Global token tracker instance
token_tracker = TokenTracker()
