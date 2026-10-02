import sys
import unittest
from unittest.mock import patch
from src import serve
from src.embeddings import MODEL_NAME


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.inventory = [{"filename": "example.docx", "content_hash": "fingerprint"}]
        self.snapshot = {"synthetic": {"embedding_model": MODEL_NAME, "documents": self.inventory,
                                       "collection": "existing", "chunks": 1}}

    def test_ready_index_is_not_rebuilt(self):
        with patch.object(serve, "read_manifest", return_value=self.snapshot), patch.object(serve, "prepare_corpus", return_value=([], [], [], self.inventory)), patch("chromadb.PersistentClient") as client, patch.object(serve, "ingest_documents") as ingest:
            client.return_value.get_collection.return_value.count.return_value = 1
            serve.ensure_index("synthetic")
            ingest.assert_not_called()

    def test_missing_collection_is_rebuilt_even_when_manifest_matches(self):
        from chromadb.errors import InvalidCollectionException
        with patch.object(serve, "read_manifest", return_value=self.snapshot), patch.object(serve, "prepare_corpus", return_value=([], [], [], self.inventory)), patch("chromadb.PersistentClient") as client, patch.object(serve, "ingest_documents") as ingest:
            client.return_value.get_collection.side_effect = InvalidCollectionException("Missing collection")
            serve.ensure_index("synthetic")
            ingest.assert_called_once_with("synthetic")

    def test_partial_collection_is_rebuilt(self):
        with patch.object(serve, "read_manifest", return_value=self.snapshot), patch.object(serve, "prepare_corpus", return_value=([], [], [], self.inventory)), patch("chromadb.PersistentClient") as client, patch.object(serve, "ingest_documents") as ingest:
            client.return_value.get_collection.return_value.count.return_value = 0
            serve.ensure_index("synthetic")
            ingest.assert_called_once_with("synthetic")

    def test_startup_uses_current_virtual_environment_and_project_directory(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-only", "QUACKQUERY_CORPUS": "synthetic"}), patch.object(sys, "argv", ["serve", "--host", "127.0.0.1", "--port", "8502"]), patch.object(serve, "ensure_index") as ensure, patch.object(serve.subprocess, "run") as run:
            run.return_value.returncode = 0
            self.assertEqual(serve.main(), 0)
            ensure.assert_called_once_with("synthetic")
            command = run.call_args.args[0]
            self.assertEqual(command[0], sys.executable)
            self.assertIn("--server.port=8502", command)
            self.assertEqual(run.call_args.kwargs["cwd"], str(serve.ROOT))

    def test_missing_key_stops_before_indexing_or_starting_server(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": ""}), patch.object(sys, "argv", ["serve"]), patch.object(serve, "ensure_index") as ensure, patch.object(serve.subprocess, "run") as run:
            with self.assertRaises(SystemExit):
                serve.main()
            ensure.assert_not_called()
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
