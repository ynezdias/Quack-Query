import unittest
from unittest.mock import patch
from src.rag import validate_response, contextualize, ask
from src.retrieval import bm25, fuse
from collections import Counter


class RagTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [{"text": "Prerequisite: CS 559 or an approved equivalent.", "metadata": {}}]
        self.payload = {"status": "answered", "claims": [{"text": "CS 559 or equivalent is required.", "evidence": [{"source_id": 1, "quote": "CS 559 or an approved equivalent."}]}]}

    def test_valid_evidence(self):
        self.assertEqual(validate_response(self.payload, self.chunks)["status"], "answered")

    def test_fabricated_quote_rejected(self):
        self.payload["claims"][0]["evidence"][0]["quote"] = "There are no prerequisites at all."
        with self.assertRaises(ValueError):
            validate_response(self.payload, self.chunks)

    def test_missing_and_boolean_source_rejected(self):
        for source in (0, 2, True, "1"):
            self.payload["claims"][0]["evidence"][0]["source_id"] = source
            with self.assertRaises(ValueError):
                validate_response(self.payload, self.chunks)

    def test_answer_requires_evidence(self):
        self.payload["claims"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate_response(self.payload, self.chunks)

    def test_nonanswers_cannot_smuggle_claims(self):
        self.payload["status"] = "unknown"
        with self.assertRaises(ValueError):
            validate_response(self.payload, self.chunks)

    def test_followup_and_new_topic(self):
        history = [{"role": "user", "content": "What is tuition for 2026?"},
                   {"role": "assistant", "content": "Untrusted invented answer"}]
        self.assertIn("tuition", contextualize("What about 2025?", history))
        self.assertNotIn("invented", contextualize("What about 2025?", history))
        self.assertEqual(contextualize("Which courses are in Cybersecurity?", history), "Which courses are in Cybersecurity?")

    def test_query_limits_before_service_call(self):
        for question in ("", "x" * 1001):
            with self.assertRaises(ValueError):
                ask(question)

    def test_exact_identifier_lexical_ranking(self):
        records = [("right", "", {}, Counter(["cs", "583", "prerequisite"]), 3),
                   ("wrong", "", {}, Counter(["cs", "541", "prerequisite"]), 3)]
        self.assertEqual(bm25("CS 583 prerequisite", records)[0][0], "right")
        self.assertEqual(fuse(["a", "b"], ["b", "c"])[0], "b")

    def test_chained_followup_retains_anchor(self):
        history = [{"role": "user", "content": "What is tuition in 2026?"},
                   {"role": "user", "content": "What about 2025?"}]
        self.assertIn("tuition", contextualize("And what about fees?", history))

    def test_unrelated_prior_topic_excluded(self):
        history = [{"role": "user", "content": "What are scholarships?"},
                   {"role": "user", "content": "What is tuition?"}]
        self.assertNotIn("scholarships", contextualize("What about last year?", history))

    def test_provider_contract_and_fail_closed(self):
        from src.rag import generate_response
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only", "GROQ_MODEL": "openai/gpt-oss-20b"}), patch("groq.Groq") as factory:
            completion = factory.return_value.chat.completions.create
            completion.return_value.choices[0].message.content = "not JSON"
            self.assertEqual(generate_response("Test question", self.chunks)["status"], "validation_failed")
            self.assertTrue(completion.call_args.kwargs["response_format"]["json_schema"]["strict"])
            self.assertEqual(completion.call_args.kwargs["reasoning_effort"], "low")

    def test_empty_sources_do_not_call_provider(self):
        from src.rag import generate_response
        with patch("groq.Groq") as factory:
            self.assertEqual(generate_response("Test question", [])["status"], "unknown")
            factory.assert_not_called()

    def test_provider_client_is_closed_when_connection_fails(self):
        import httpx
        from groq import APIConnectionError
        from src.rag import generate_response
        error = APIConnectionError(request=httpx.Request("POST", "https://api.groq.com/test"))
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only"}), patch("groq.Groq") as factory:
            factory.return_value.chat.completions.create.side_effect = error
            with self.assertRaises(APIConnectionError):
                generate_response("Test question", self.chunks)
            factory.return_value.close.assert_called_once()

    def test_empty_provider_content_fails_citation_validation(self):
        from src.rag import generate_response
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only"}), patch("groq.Groq") as factory:
            factory.return_value.chat.completions.create.return_value.choices = []
            self.assertEqual(generate_response("Test question", self.chunks)["status"], "validation_failed")
            factory.return_value.close.assert_called_once()

    def test_missing_and_placeholder_keys_fail_before_api_call(self):
        from src.rag import generate_response
        from src.runtime import ConfigurationError
        for key in ("", "  ", "replace-with-your-key"):
            with patch.dict("os.environ", {"GROQ_API_KEY": key}), patch("groq.Groq") as factory:
                with self.assertRaises(ConfigurationError):
                    generate_response("Test question", self.chunks)
                factory.assert_not_called()

    def test_invalid_quote_gets_one_bounded_correction_with_same_sources(self):
        import json
        from types import SimpleNamespace
        from src.rag import generate_response
        invalid = {"status": "answered", "claims": [{"text": "Invented prerequisite", "evidence": [{"source_id": 1, "quote": "CS 999 is the prerequisite."}]}]}
        def completion(payload):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only"}), patch("groq.Groq") as factory:
            create = factory.return_value.chat.completions.create
            create.side_effect = [completion(invalid), completion(self.payload)]
            result = generate_response("Test question", self.chunks)
            self.assertEqual(result["status"], "answered")
            self.assertEqual(create.call_count, 2)
            initial = create.call_args_list[0].kwargs["messages"]
            correction = create.call_args_list[1].kwargs["messages"]
            self.assertEqual(initial[:2], correction[:2])
            self.assertIn("Quotation not found", correction[-1]["content"])
            factory.return_value.close.assert_called_once()

    def test_two_invalid_outputs_never_display_unsupported_claims(self):
        from src.rag import generate_response
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only"}), patch("groq.Groq") as factory:
            create = factory.return_value.chat.completions.create
            create.return_value.choices[0].message.content = "not JSON"
            result = generate_response("Test question", self.chunks)
            self.assertEqual(result["status"], "validation_failed")
            self.assertEqual(result["claims"], [])
            self.assertEqual(create.call_count, 2)
