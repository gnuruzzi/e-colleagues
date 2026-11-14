#!/usr/bin/env python3
"""Start one tech-lead session per issue, each in its own worktree and terminal window.

Standard library only.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib

DEFAULTS = {
    "default_host": None,
    "hosts": {
        "antigravity": {"start": "agy --agent tech-lead"},
        "codex": {"start": "codex --profile e-colleagues"},
        "opencode": {"start": "opencode --agent tech-lead"},
        "claude": {"start": "claude --agent tech-lead"},
    },
    "launcher": {
        "start": ["workmux", "add", "{name}", "--background",
                  "--agent", "{agent}", "--prompt", "{prompt}"],
        "base_flag": "--base",
        "status": ["workmux", "status", "--json"],
        "capture": ["workmux", "capture", "{name}", "--lines", "200"],
    },
}
PROMPT = "Use the ec-fleet skill. Your assignment: issue {ref}."

HOST_KEYS = {"start": str, "prompt": str}
LAUNCHER_KEYS = {"start": list, "status": list, "capture": list, "base_flag": str}


class ConfigError(Exception):
    pass


def safe_name(ref: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")
    if not name:
        raise ValueError(f"nothing usable for a worktree name in {ref!r}")
    return f"issue-{name}" if name.isdigit() else name


def _check(table: object, allowed: dict, where: str) -> dict:
    if not isinstance(table, dict):
        raise ConfigError(f"{where}: expected a table")
    for key, value in table.items():
        dotted = f"{where}.{key}" if where else key
        if key not in allowed:
            raise ConfigError(f"{dotted}: unknown key (allowed: {', '.join(sorted(allowed))})")
        if not isinstance(value, allowed[key]):
            raise ConfigError(f"{dotted}: expected {allowed[key].__name__}")
        if allowed[key] is list and not all(isinstance(i, str) for i in value):
            raise ConfigError(f"{dotted}: expected a list of strings")
    return table


def config_path(path: pathlib.Path | None) -> pathlib.Path:
    if path:
        return path
    if os.environ.get("EC_FLEET_CONFIG"):
        return pathlib.Path(os.environ["EC_FLEET_CONFIG"])
    base = os.environ.get("XDG_CONFIG_HOME") or str(pathlib.Path.home() / ".config")
    return pathlib.Path(base) / "e-colleagues" / "fleet.toml"


def load_config(path: pathlib.Path | None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    p = config_path(path)
    if not p.exists():
        return cfg
    try:
        data = tomllib.loads(p.read_text())
    except (tomllib.TOMLDecodeError, OSError) as e:
        raise ConfigError(f"{p}: {e}")
    _check(data, {"default_host": str, "hosts": dict, "launcher": dict}, "")
    cfg["launcher"].update(_check(data.get("launcher", {}), LAUNCHER_KEYS, "launcher"))
    for host, table in data.get("hosts", {}).items():
        _check(table, HOST_KEYS, f"hosts.{host}")
        merged = {**cfg["hosts"].get(host, {}), **table}
        if "start" not in merged:
            raise ConfigError(f"hosts.{host}: a host that is not built in needs a start")
        cfg["hosts"][host] = merged
    if "default_host" in data:
        cfg["default_host"] = data["default_host"]
    return cfg


def fill(argv: list[str], values: dict[str, str]) -> list[str]:
    # One pass, so a placeholder typed inside a value is never expanded.
    pattern = re.compile(r"\{(%s)\}" % "|".join(values))
    return [pattern.sub(lambda m: values[m.group(1)], item) for item in argv]


def run_launcher(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def start_argv(cfg: dict, ref: str, name: str | None, host: str | None,
               base: str | None) -> tuple[list[str], str]:
    host = host or cfg["default_host"]
    hosts = cfg["hosts"]
    if not host:
        raise ConfigError(f"no host chosen: pass --host ({', '.join(sorted(hosts))}) "
                          "or set default_host in the config")
    if host not in hosts:
        raise ConfigError(f"unknown host {host!r}; known: {', '.join(sorted(hosts))}")
    if name is None:
        name = safe_name(ref)
    elif not name or name.startswith("-") or re.search(r"\s", name):
        raise ConfigError(f"--name {name!r} must be non-empty, not start with '-', "
                          "and contain no whitespace")
    prompt = hosts[host].get("prompt", PROMPT).replace("{ref}", ref)
    argv = fill(cfg["launcher"]["start"],
                {"name": name, "agent": hosts[host]["start"], "prompt": prompt})
    if base:
        argv += [cfg["launcher"]["base_flag"], base]
    return argv, name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=pathlib.Path)
    sub = ap.add_subparsers(dest="command", required=True)
    st = sub.add_parser("start", help="start a tech-lead on an issue")
    st.add_argument("ref")
    st.add_argument("--name")
    st.add_argument("--host")
    st.add_argument("--base")
    st.add_argument("--dry-run", action="store_true",
                    help="print the launcher argv as JSON and run nothing")
    a = ap.parse_args()

    try:
        cfg = load_config(a.config)
        argv, name = start_argv(cfg, a.ref, a.name, a.host, a.base)
    except (ConfigError, ValueError) as e:
        print(f"fleet: {e}", file=sys.stderr)
        return 2
    if a.dry_run:
        print(json.dumps(argv))
        return 0
    try:
        r = run_launcher(argv)
    except FileNotFoundError:
        print(f"fleet: launcher not found: {argv[0]}", file=sys.stderr)
        return 127
    if r.returncode:
        sys.stderr.write(r.stderr or r.stdout)
        return r.returncode
    print(f"started {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
