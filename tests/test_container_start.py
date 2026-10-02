import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src import container_start


class ContainerStartupTests(unittest.TestCase):
    def test_baked_index_is_copied_before_server_starts(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "index"
            with patch.dict(os.environ, {"QUACKQUERY_INDEX_DIR": str(target), "PORT": "8501"}), patch.object(container_start.shutil, "copytree") as copy, patch.object(container_start.os, "execv") as execute:
                container_start.main()
            copy.assert_called_once_with("/app/chroma_db", target, dirs_exist_ok=True)
            self.assertEqual(execute.call_args.args[1][-2:], ["--port", "8501"])

    def test_existing_index_is_preserved_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "quackquery.json").write_text("{}")
            with patch.dict(os.environ, {"QUACKQUERY_INDEX_DIR": directory}), patch.object(container_start.shutil, "copytree") as copy, patch.object(container_start.os, "execv"):
                container_start.main()
            copy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
