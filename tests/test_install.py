import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("installer", Path(__file__).resolve().parents[1] / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
ENDPOINT = "https://example.com/mcp"


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.destination = Path(self.scratch.name) / "email-warmup"
        self.available = patch.object(installer.shutil, "which", return_value="/agent")
        self.location = patch.object(installer, "skill_destination", return_value=self.destination)
        self.available.start()
        self.location.start()
        self.addCleanup(patch.stopall)

    def install(self, agent="codex"):
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install(agent, ENDPOINT)

    def test_fresh_install_registers_client_and_copies_complete_skill(self):
        for agent in ["codex", "claude"]:
            with self.subTest(agent=agent), patch.object(installer, "inspect_server", return_value=None), patch.object(installer.subprocess, "run") as run:
                target = Path(self.scratch.name) / agent / "email-warmup"
                with patch.object(installer, "skill_destination", return_value=target):
                    self.install(agent)
                self.assertTrue(installer.same_skill(target))
                args = run.call_args.args[0]
                self.assertEqual(args[:3], [agent, "mcp", "add"])
                self.assertIn(ENDPOINT, args)
                if agent == "claude":
                    self.assertEqual(args[3:7], ["--scope", "user", "--transport", "http"])

    def test_identical_installation_does_not_change_config_or_skill(self):
        installer.shutil.copytree(installer.SOURCE, self.destination)
        before = {p: p.stat().st_mtime_ns for p in self.destination.rglob("*") if p.is_file()}
        with patch.object(installer, "inspect_server", return_value=ENDPOINT), patch.object(installer.subprocess, "run") as run:
            self.install()
        run.assert_not_called()
        self.assertEqual(before, {p: p.stat().st_mtime_ns for p in before})

    def test_existing_different_server_is_preserved(self):
        with patch.object(installer, "inspect_server", return_value="https://other.example/mcp"), patch.object(installer.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "points elsewhere"):
                self.install()
        run.assert_not_called()
        self.assertFalse(self.destination.exists())

    def test_customized_skill_stops_before_any_configuration_change(self):
        installer.shutil.copytree(installer.SOURCE, self.destination)
        customized = self.destination / "references" / "setup.md"
        customized.write_text("Customer customizations")
        with patch.object(installer, "inspect_server") as inspect:
            with self.assertRaisesRegex(RuntimeError, "differs"):
                self.install()
        inspect.assert_not_called()
        self.assertEqual(customized.read_text(), "Customer customizations")

    def test_symlink_skill_is_not_followed_or_replaced(self):
        self.destination.symlink_to(installer.SOURCE, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "differs"):
            self.install()
        self.assertTrue(self.destination.is_symlink())

    def test_registration_failure_does_not_claim_or_install_skill(self):
        with patch.object(installer, "inspect_server", return_value=None), patch.object(installer.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "agent")):
            with self.assertRaises(subprocess.CalledProcessError):
                self.install()
        self.assertFalse(self.destination.exists())

    def test_unsafe_endpoints_stop_before_client_access(self):
        for endpoint in ["http://example.com/mcp", "https://user:secret@example.com/mcp", "https://example.com/mcp?token=secret", "https://example.com/mcp#secret", "https://example.com:wrong/mcp", "http://localhost.evil/mcp", "--url", "https://example.com/mcp\n"]:
            with self.subTest(endpoint=endpoint), patch.object(installer, "inspect_server") as inspect:
                with self.assertRaises(ValueError):
                    installer.install("codex", endpoint)
                inspect.assert_not_called()

    def test_https_and_loopback_endpoints_are_preserved_exactly(self):
        for endpoint in [ENDPOINT, "https://example.com/mcp/", "http://localhost:3050/mcp", "http://127.0.0.1:3050/mcp", "http://[::1]:3050/mcp"]:
            installer.validate_endpoint(endpoint)

    def test_native_client_missing_and_unexpected_errors_are_distinguished(self):
        for agent, message in [("codex", "Error: No MCP server named 'email-warmup' found."), ("claude", "No MCP server found with name: email-warmup")]:
            with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", message)):
                self.assertIsNone(installer.inspect_server(agent))
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "Configuration cannot be read")):
            with self.assertRaisesRegex(RuntimeError, "Could not inspect"):
                installer.inspect_server("codex")

    def test_native_client_responses_and_disabled_server(self):
        response = {"enabled": True, "transport": {"type": "streamable_http", "url": ENDPOINT}}
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(response), "")):
            self.assertEqual(installer.inspect_server("codex"), ENDPOINT)
        response["enabled"] = False
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(response), "")):
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                installer.inspect_server("codex")
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, f"  Type: http\n  URL: {ENDPOINT}\n", "")):
            self.assertEqual(installer.inspect_server("claude"), ENDPOINT)

    def test_incomplete_existing_config_is_not_treated_as_missing(self):
        response = {"enabled": True, "transport": {"type": "streamable_http"}}
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(response), "")):
            with self.assertRaisesRegex(RuntimeError, "recognized"):
                installer.inspect_server("codex")


if __name__ == "__main__":
    unittest.main()
