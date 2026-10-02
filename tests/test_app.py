import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_starter_uses_existing_question_flow_once(self):
        result = {"answer": "Test answer", "response": {"status": "unknown", "message": "Test answer", "claims": []}, "chunks": [], "seconds": 0.1}
        with patch.dict("os.environ", {"QUACKQUERY_CORPUS": ""}), patch("src.rag.ask", return_value=result) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.button(key="starter_admissions").click().run()
            self.assertFalse(app.exception)
            service.assert_called_once_with("What are the graduate admission requirements?", corpus="synthetic", history=[])
            self.assertEqual(len(app.chat_message), 2)
            self.assertEqual(len(app.session_state["requests"]), 1)
            app.run()
            self.assertEqual(service.call_count, 1)
            app.button[0].click().run()
            self.assertEqual(len(app.chat_message), 0)
            self.assertEqual(app.button(key="starter_admissions").label, "Explore admissions")

    def test_history_followup_isolation_and_clear(self):
        result = {"answer": "Test answer", "response": {"status": "unknown", "message": "Test answer", "claims": []}, "chunks": [], "seconds": 0.1}
        with patch.dict("os.environ", {"QUACKQUERY_CORPUS": ""}), patch("src.rag.ask", return_value=result) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            self.assertFalse(app.exception)
            app.chat_input[0].set_value("What is tuition?").run()
            self.assertEqual(len(app.chat_message), 2)
            app.chat_input[0].set_value("What about last year?").run()
            self.assertEqual(len(service.call_args.kwargs["history"]), 2)
            self.assertEqual(len(app.chat_message), 2)
            app.button(key="history_synthetic_0").click().run()
            self.assertEqual(app.chat_message[0].markdown[0].value, "What is tuition?")
            self.assertEqual(service.call_count, 2)
            app.button(key="history_synthetic_2").click().run()
            self.assertEqual(app.chat_message[0].markdown[0].value, "What about last year?")
            app.selectbox[0].select("unverified").run()
            self.assertEqual(len(app.chat_message), 0)
            app.selectbox[0].select("synthetic").run()
            self.assertEqual(len(app.chat_message), 2)
            app.button[0].click().run()
            self.assertEqual(len(app.chat_message), 0)

    def test_provider_failure_does_not_create_answer(self):
        with patch("src.rag.ask", side_effect=RuntimeError("Test provider failure")):
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.chat_input[0].set_value("What is tuition?").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.error), 1)
            self.assertEqual(len(app.chat_message), 1)
            self.assertEqual(app.chat_message[0].markdown[0].value, "What is tuition?")
            self.assertEqual(app.session_state["conversations"]["synthetic"], [])

    def test_valid_answer_has_inspectable_evidence(self):
        result = {"answer": "A supported claim.", "response": {"status": "answered", "message": "", "claims": [
            {"text": "A supported claim.", "evidence": [{"source_id": 1, "quote": "The supporting passage."}]}]},
            "chunks": [{"text": "The supporting passage.", "metadata": {"filename": "demo.docx", "document_id": "missing.docx", "locator": "Document text"}}], "seconds": 0.1}
        with patch("src.rag.ask", return_value=result):
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.chat_input[0].set_value("A test question?").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.expander), 1)
            self.assertIn("demo.docx", app.expander[0].label)

    def test_repeated_connection_failures_do_not_lock_session(self):
        import httpx
        from groq import APIConnectionError
        failure = APIConnectionError(request=httpx.Request("POST", "https://api.groq.com/test"))
        with patch("src.rag.ask", side_effect=failure) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            for _ in range(8):
                app.chat_input[0].set_value("What is tuition?").run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["requests"], [])
                self.assertIn("could not connect", app.error[0].value)
            self.assertEqual(service.call_count, 8)
            self.assertEqual(app.session_state["conversations"]["synthetic"], [])

    def test_session_limit_expires_and_preserves_history(self):
        result = {"answer": "Test answer", "response": {"status": "unknown", "message": "Test answer", "claims": []}, "chunks": [], "seconds": 0.1}
        with patch.dict("os.environ", {"QUACKQUERY_REQUESTS_PER_MINUTE": "2"}), patch("src.rag.ask", return_value=result) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.chat_input[0].set_value("First question?").run()
            app.chat_input[0].set_value("Second question?").run()
            app.chat_input[0].set_value("Third question?").run()
            self.assertEqual(service.call_count, 2)
            self.assertIn("2 completed questions", app.warning[0].value)
            self.assertEqual(len(app.session_state["conversations"]["synthetic"]), 4)
            app.session_state["requests"] = [timestamp - 61 for timestamp in app.session_state["requests"]]
            app.chat_input[0].set_value("Third question?").run()
            self.assertEqual(service.call_count, 3)
            self.assertEqual(len(app.session_state["conversations"]["synthetic"]), 6)

    def test_provider_cooldown_honors_retry_after_without_consuming_allowance(self):
        import httpx
        import time
        from groq import RateLimitError
        response = httpx.Response(429, headers={"retry-after": "3"}, request=httpx.Request("POST", "https://api.groq.com/test"))
        failure = RateLimitError("Private provider detail", response=response, body=None)
        result = {"answer": "Test answer", "response": {"status": "unknown", "message": "Test answer", "claims": []}, "chunks": [], "seconds": 0.1}
        with patch("src.rag.ask", side_effect=[failure, result]) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.chat_input[0].set_value("What is tuition?").run()
            self.assertEqual(app.session_state["requests"], [])
            self.assertIn("3 seconds", app.warning[0].value)
            self.assertNotIn("Private provider detail", app.warning[0].value)
            app.chat_input[0].set_value("Retry?").run()
            self.assertEqual(service.call_count, 1)
            app.session_state["provider_retry_at"] = time.monotonic() - 1
            app.chat_input[0].set_value("Retry?").run()
            self.assertFalse(app.exception)
            self.assertEqual(service.call_count, 2)
            self.assertEqual(len(app.session_state["requests"]), 1)

    def test_invalid_citations_do_not_consume_allowance(self):
        result = {"answer": "Cannot verify", "response": {"status": "validation_failed", "message": "Cannot verify", "claims": []}, "chunks": [], "seconds": 0.1}
        with patch("src.rag.ask", return_value=result):
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.chat_input[0].set_value("What is tuition?").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["requests"], [])
