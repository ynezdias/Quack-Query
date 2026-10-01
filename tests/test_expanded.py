import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from src.ingest import prepare_corpus, discover_documents
from src.knowledge import ROOT
from src.evaluate_expanded import retrieval_metrics, summarize


class ExpandedTests(unittest.TestCase):
    def test_dataset_sources_and_user_coverage(self):
        cases = json.loads((ROOT / "eval/expanded_questions.json").read_text())
        self.assertEqual(len(cases), 75)
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        self.assertEqual({c["user_question_number"] for c in cases if "user_question_number" in c}, set(range(1, 56)))
        names = {corpus: {p.name for p in discover_documents(corpus)} for corpus in ("synthetic", "verified")}
        for case in cases:
            self.assertTrue(set(case["expected_sources"]) <= names[case["corpus"]])
            self.assertTrue(case["reference_answer"])
            self.assertIn(case["expected_status"], ("answered", "clarify", "unknown"))

    def test_unknown_not_counted_as_retrieval_success(self):
        empty = retrieval_metrics([], [])
        self.assertIsNone(empty["all_sources"])
        one = retrieval_metrics(["a", "b"], [{"metadata": {"filename": "a"}}])
        self.assertEqual(one["source_recall"], .5)
        self.assertFalse(one["all_sources"])
        self.assertEqual(summarize([empty, one])["all_sources"]["count"], 1)

    def test_reviewed_provenance_and_corpus_isolation(self):
        _, _, metadata, inventory = prepare_corpus("verified")
        self.assertEqual(len(inventory), 5)
        self.assertTrue(all(m["source_type"] == "verified_official_summary" for m in metadata))
        self.assertFalse(any("verified/" in p.relative_to(ROOT / "data").as_posix() for p in discover_documents("synthetic")))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / "verified"
            folder.mkdir()
            document = folder / "sample.txt"
            document.write_text("A reviewed fact.")
            record = {"content_hash": hashlib.sha256(document.read_bytes()).hexdigest(), "source_url": "https://evil.example/fake"}
            registry = folder / "sources.json"
            registry.write_text(json.dumps({document.name: record}))
            with self.assertRaises(ValueError):
                prepare_corpus("verified", root)
            record["source_url"] = "https://www.stevens.edu/application-requirements"
            registry.write_text(json.dumps({document.name: record}))
            document.write_text("An unreviewed change.")
            with self.assertRaises(ValueError):
                prepare_corpus("verified", root)

    def test_runner_writes_checkpoint(self):
        from unittest.mock import patch
        from src.evaluate_expanded import run
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.json"
            with patch("src.evaluate_expanded.retrieve_chunks", return_value=[]), patch("src.evaluate_expanded.read_manifest", return_value={"synthetic": {}}):
                run(ids="S052", output=output)
            report = json.loads(output.read_text())
            self.assertEqual(report["completed_cases"], 1)
            self.assertEqual(len(report["results"]), 2)
            self.assertEqual(report["summary"]["synthetic"]["hybrid"]["source_recall"]["count"], 0)

    def test_reviewed_corpus_ui_displays_source_link(self):
        from unittest.mock import patch
        from streamlit.testing.v1 import AppTest
        result = {"answer": "A supported claim.", "response": {"status": "answered", "message": "", "claims": [
            {"text": "A supported claim.", "evidence": [{"source_id": 1, "quote": "The supporting passage."}]}]},
            "chunks": [{"text": "The supporting passage.", "metadata": {"filename": "summary.txt", "document_id": "verified/summary.txt", "locator": "Reviewed source summary", "source_type": "verified_official_summary", "source_url": "https://www.stevens.edu/application-requirements", "verified_at": "2026-09-17"}}], "seconds": .1}
        with patch.dict("os.environ", {"QUACKQUERY_CORPUS": ""}), patch("src.rag.ask", return_value=result) as service:
            app = AppTest.from_file("app.py", default_timeout=30).run()
            app.selectbox[0].select("verified").run()
            app.chat_input[0].set_value("What is the application fee?").run()
            self.assertFalse(app.exception)
            self.assertEqual(service.call_args.kwargs["corpus"], "verified")
            self.assertEqual(len(app.get("link_button")), 1)
