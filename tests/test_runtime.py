import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auto_url_fixer import runtime


class RuntimeTests(unittest.TestCase):
    def test_runtime_paths_use_localappdata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"LOCALAPPDATA": temp_dir}, clear=False):
                runtime_dir = runtime.get_runtime_dir()
                pid_file = runtime.get_pid_file()
                stop_file = runtime.get_stop_file()

        self.assertEqual(runtime_dir, Path(temp_dir) / "AutoURLFixer")
        self.assertEqual(pid_file, runtime_dir / "auto_url_fixer.pid")
        self.assertEqual(stop_file, runtime_dir / "stop.flag")

    def test_request_and_clear_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"LOCALAPPDATA": temp_dir}, clear=False):
                runtime.request_stop()
                self.assertTrue(runtime.stop_requested())

                runtime.clear_stop_request()
                self.assertFalse(runtime.stop_requested())


if __name__ == "__main__":
    unittest.main()
