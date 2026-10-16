#!/usr/bin/env python3
"""Install the Email Warmup skill and configure an existing agent CLI."""

import argparse
import filecmp
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


SOURCE = Path(__file__).resolve().parent / "skills" / "email-warmup"
SERVER = "email-warmup"


def validate_endpoint(endpoint):
    try:
        url = urlsplit(endpoint)
        _ = url.port
        valid = (
            bool(url.hostname)
            and url.username is None
            and url.password is None
            and not url.query
            and not url.fragment
            and not any(char.isspace() for char in endpoint)
            and (url.scheme == "https" or (
                url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1", "::1"}
            ))
        )
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("Use the exact HTTPS MCP endpoint from Integrations; HTTP is allowed only on loopback for local development.")


def skill_destination(agent):
    parent = Path.home() / ".agents" if agent == "codex" else Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    return parent / "skills" / SERVER


def same_skill(destination):
    if destination.is_symlink() or not destination.is_dir():
        return False
    source_files = {path.relative_to(SOURCE) for path in SOURCE.rglob("*") if path.is_file()}
    installed_files = {path.relative_to(destination) for path in destination.rglob("*") if path.is_file()}
    if source_files != installed_files or any(path.is_symlink() for path in destination.rglob("*")):
        return False
    return all(filecmp.cmp(SOURCE / path, destination / path, shallow=False) for path in source_files)


def inspect_server(agent):
    command = [agent, "mcp", "get", SERVER] + (["--json"] if agent == "codex" else [])
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    if result.returncode:
        expected = f"No MCP server named '{SERVER}' found." if agent == "codex" else f"No MCP server found with name: {SERVER}"
        if result.returncode == 1 and expected in result.stdout + result.stderr:
            return None
        raise RuntimeError(f"Could not inspect the existing {agent} connection. Check `{agent} mcp get {SERVER}` before retrying.")
    if agent == "codex":
        server = json.loads(result.stdout)
        if not server.get("enabled", False):
            raise RuntimeError("The existing email-warmup connection is disabled. Review it before installing.")
        transport = server.get("transport", {})
        if transport.get("type") != "streamable_http" or not isinstance(transport.get("url"), str) or not transport["url"]:
            raise RuntimeError("The existing Codex connection could not be recognized. Review it before installing.")
        return transport["url"]
    match = re.search(r"^\s*URL:\s*(\S+)\s*$", result.stdout, flags=re.MULTILINE)
    if not match or not re.search(r"^\s*Type:\s*http\s*$", result.stdout, flags=re.MULTILINE):
        raise RuntimeError("The existing Claude Code connection could not be recognized. Review it before installing.")
    return match[1]


def install(agent, endpoint):
    validate_endpoint(endpoint)
    if not shutil.which(agent):
        raise RuntimeError(f"The {agent} CLI is not installed or is not on PATH.")
    if not (SOURCE / "SKILL.md").is_file():
        raise RuntimeError("The bundled skill is missing. Run this installer from a complete package checkout.")
    destination = skill_destination(agent)
    exists = destination.exists() or destination.is_symlink()
    if exists and not same_skill(destination):
        raise RuntimeError(f"The skill at {destination} differs from this package. Review it before replacing anything.")
    existing = inspect_server(agent)
    if existing is not None and existing != endpoint:
        raise RuntimeError("The existing email-warmup server points elsewhere. Review it before replacing anything.")
    if existing is None:
        command = [agent, "mcp", "add"]
        command += [SERVER, "--url", endpoint] if agent == "codex" else ["--scope", "user", "--transport", "http", SERVER, endpoint]
        subprocess.run(command, check=True)
    if not exists:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE, destination)
    print(f"MCP configuration: {agent} / {SERVER}")
    print(f"MCP endpoint: {endpoint}")
    print(f"Skill installed: {destination}")
    print("Configuration and skill are installed. Browser authorization and an authenticated read still need to be verified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["codex", "claude"], required=True)
    parser.add_argument("--endpoint", required=True)
    args = parser.parse_args()
    try:
        install(args.agent, args.endpoint)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
