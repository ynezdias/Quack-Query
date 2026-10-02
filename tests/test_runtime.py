import unittest
from unittest.mock import patch
import httpx
from groq import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from src.runtime import ConfigurationError, recent_requests, request_limit, retry_after, service_error_message


class RuntimeTests(unittest.TestCase):
    def test_limits_are_configurable_and_invalid_values_fall_back(self):
        for value, expected in [("30", 30), ("6", 6), ("0", 30), ("-2", 30), ("invalid", 30), ("601", 30)]:
            with self.subTest(value=value), patch.dict("os.environ", {"QUACKQUERY_REQUESTS_PER_MINUTE": value}):
                self.assertEqual(request_limit(), expected)

    def test_only_current_window_counts(self):
        self.assertEqual(recent_requests([39, 40, 41, 99, 101], 100), [41, 99])

    def test_retry_after_numeric_date_and_invalid_headers(self):
        from datetime import datetime, timezone, timedelta
        from email.utils import format_datetime
        date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=120), usegmt=True)
        for value, expected in [("2.2", 3), ("bad", 60), ("nan", 60), ("-2", 1)]:
            response = httpx.Response(429, headers={"retry-after": value}, request=httpx.Request("POST", "https://api.groq.com/test"))
            error = RateLimitError("Private detail", response=response, body=None)
            self.assertEqual(retry_after(error), expected)
        response = httpx.Response(429, headers={"retry-after": date}, request=httpx.Request("POST", "https://api.groq.com/test"))
        self.assertTrue(119 <= retry_after(RateLimitError("Private detail", response=response, body=None)) <= 120)

    def test_provider_diagnostics_do_not_expose_raw_errors(self):
        request = httpx.Request("POST", "https://api.groq.com/test")
        self.assertIn("could not connect", service_error_message(APIConnectionError(request=request)))
        self.assertIn("too long", service_error_message(APITimeoutError(request=request)))
        response = httpx.Response(401, request=request)
        message = service_error_message(AuthenticationError("secret-test-value", response=response, body=None))
        self.assertIn("API key", message)
        self.assertNotIn("secret-test-value", message)
        self.assertIn("GROQ_API_KEY", service_error_message(ConfigurationError("secret-test-value")))


if __name__ == "__main__":
    unittest.main()
