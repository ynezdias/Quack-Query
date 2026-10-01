import unittest
from unittest.mock import patch
from src.embeddings import get_encoder


class EncoderLoadingTests(unittest.TestCase):
    def tearDown(self):
        get_encoder.cache_clear()

    def test_cached_model_load_never_checks_network(self):
        get_encoder.cache_clear()
        with patch("sentence_transformers.SentenceTransformer") as factory:
            first = get_encoder()
            self.assertIs(get_encoder(), first)
            factory.assert_called_once()
            self.assertTrue(factory.call_args.kwargs["local_files_only"])

    def test_first_install_can_download_missing_model(self):
        get_encoder.cache_clear()
        with patch("sentence_transformers.SentenceTransformer", side_effect=[OSError("Not cached"), object()]) as factory:
            get_encoder()
            self.assertEqual(factory.call_count, 2)
            self.assertTrue(factory.call_args_list[0].kwargs["local_files_only"])
            self.assertNotIn("local_files_only", factory.call_args_list[1].kwargs)
