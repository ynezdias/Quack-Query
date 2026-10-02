"""Safe service diagnostics and per-session request accounting."""
import logging
import math
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from groq import (
    APIConnectionError, APIStatusError, APITimeoutError, AuthenticationError,
    BadRequestError, NotFoundError, PermissionDeniedError, RateLimitError,
)


class ConfigurationError(RuntimeError):
    """Required answer-provider configuration is missing."""


class IndexUnavailableError(RuntimeError):
    """A selected document collection needs to be indexed."""


def request_limit():
    """Allow normal exploration; keep a bounded, configurable session allowance."""
    try:
        value = int(os.getenv("QUACKQUERY_REQUESTS_PER_MINUTE", "30"))
        if not 1 <= value <= 600:
            raise ValueError("Outside supported range")
        return value
    except ValueError:
        logging.warning("Invalid QUACKQUERY_REQUESTS_PER_MINUTE; using 30")
        return 30


def recent_requests(timestamps, now):
    return [timestamp for timestamp in timestamps if 0 <= now - timestamp < 60]


def retry_after(error, default=60):
    """Respect provider Retry-After headers, without exposing provider bodies."""
    response = getattr(error, "response", None)
    value = response.headers.get("retry-after") if response is not None else None
    if value:
        try:
            seconds = float(value)
        except ValueError:
            try:
                seconds = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                return default
        if math.isfinite(seconds):
            return max(1, math.ceil(seconds))
    return default


def service_error_message(error):
    """Describe actionable failure categories; never render raw API exceptions."""
    if isinstance(error, ConfigurationError):
        return "The AI service needs a Groq API key. Set GROQ_API_KEY in .env and restart QuackQuery."
    if isinstance(error, IndexUnavailableError):
        return "This knowledge base is not ready. Restart with run.ps1 to rebuild its document index."
    if isinstance(error, AuthenticationError):
        return "Groq rejected the API key. Update GROQ_API_KEY in .env and restart QuackQuery."
    if isinstance(error, PermissionDeniedError):
        return "The Groq account does not have permission to use this model. Check the account and GROQ_MODEL setting."
    if isinstance(error, APITimeoutError):
        return "The AI service took too long to respond. Try again; this failed request did not use your session allowance."
    if isinstance(error, APIConnectionError):
        return "QuackQuery could not connect to the AI service. Check internet access and restart with run.ps1 outside a restricted runner. This failed request did not use your session allowance."
    if isinstance(error, RateLimitError):
        return "Groq is temporarily limiting requests. Your conversation is preserved; retry after the countdown."
    if isinstance(error, NotFoundError):
        return "The configured AI model is unavailable. Update GROQ_MODEL in .env to a model enabled for your Groq account."
    if isinstance(error, BadRequestError):
        return "The AI provider could not process this request. Try a shorter question or check that GROQ_MODEL supports structured answers."
    if isinstance(error, APIStatusError):
        return "The AI provider is temporarily unavailable. Try again shortly; this failed request did not use your session allowance."
    return "The answer service is unavailable. Please try again shortly. This failed request did not use your session allowance."
