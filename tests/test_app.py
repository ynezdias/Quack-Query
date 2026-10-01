import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
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
