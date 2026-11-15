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
        # Each trust string is for one session and saves nothing. agy keeps trust per exact
        # path; Codex keeps it per repository and asks only in one it has never trusted.
        "antigravity": {"start": "agy --agent tech-lead",
                        "trust": "--settings '{\"trustedWorkspaces\":[\"{worktree}\"]}'"},
        "codex": {"start": "codex --profile e-colleagues",
                  "trust": "-c 'projects={\"{worktree}\"={trust_level=\"trusted\"}}'"},
        # opencode's TUI has no --agent: a config file named in the environment chooses it,
        # and only a private server reads that from this session's environment (E30).
        "opencode": {"start": "env OPENCODE_CONFIG={skill}/opencode-tech-lead.json "
                              "opencode --standalone"},
        "claude": {"start": "claude --agent tech-lead"},
    },
    "launcher": {
        "start": ["workmux", "add", "{name}", "--background",
                  "--agent", "{agent}", "--prompt", "{prompt}"],
        "base_flag": "--base",
        "status": ["workmux", "status", "--json"],
        "capture": ["workmux", "capture", "{name}", "--lines", "200"],
        "where": ["workmux", "add", "{name}", "--dry-run"],
    },
}
PROMPT = "Use the ec-fleet skill. Your assignment: issue {ref}."

HOST_KEYS = {"start": str, "prompt": str, "trust": str}
LAUNCHER_KEYS = {"start": list, "status": list, "capture": list, "where": list, "base_flag": str}
NO_PATH = "could not learn the worktree's path, so the session may open at its host's trust prompt"


class ConfigError(Exception):
    pass


class LauncherError(Exception):
    def __init__(self, argv0: str, e: OSError):
        super().__init__(f"cannot run launcher {argv0}: {e.strerror or e}")
        self.code = 127 if isinstance(e, FileNotFoundError) else 126


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
        if allowed[key] is list and not value:
            raise ConfigError(f"{dotted}: expected a non-empty list")
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
    explicit = path or os.environ.get("EC_FLEET_CONFIG")
    p = config_path(path)
    if not p.exists():
        if explicit:
            raise ConfigError(f"{p}: no such config file")
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
    try:
        return subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    except OSError as e:
        raise LauncherError(argv[0], e)


def check_flag(flag: str, value: str) -> None:
    if not value or value.startswith("-") or re.search(r"\s", value):
        raise ConfigError(f"{flag} {value!r} must be non-empty, not start with '-', "
                          "and contain no whitespace")


def worktree_path(cfg: dict, name: str) -> str | None:
    try:
        r = run_launcher(fill(cfg["launcher"]["where"], {"name": name}))
    except LauncherError:
        return None
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    labelled = [ln for ln in lines if ln.startswith("Worktree:")]
    path = labelled[0][len("Worktree:"):].strip() if labelled else "".join(lines[:1])
    # The path lands inside quotes in the host's command, so one that could end them is refused.
    if r.returncode or not os.path.isabs(path) or re.search(r"['\"\\\x00-\x1f]", path):
        return None
    return path


def start_argv(cfg: dict, ref: str, name: str | None, host: str | None, base: str | None,
               dry_run: bool = False) -> tuple[list[str], str, bool]:
    if not ref.strip():
        raise ConfigError("the reference must not be empty")
    host = host or cfg["default_host"]
    hosts = cfg["hosts"]
    if not host:
        raise ConfigError(f"no host chosen: pass --host ({', '.join(sorted(hosts))}) "
                          "or set default_host in the config")
    if host not in hosts:
        raise ConfigError(f"unknown host {host!r}; known: {', '.join(sorted(hosts))}")
    if name is None:
        name = safe_name(ref)
    else:
        check_flag("--name", name)
    if base is not None:
        check_flag("--base", base)
    prompt = hosts[host].get("prompt", PROMPT).replace("{ref}", ref)
    agent, trust, trusted = hosts[host]["start"], hosts[host].get("trust", ""), True
    if "{skill}" in agent:
        here = str(pathlib.Path(__file__).resolve().parent)
        # The launcher passes this unquoted, so a space or a quote in it would split it.
        if not re.fullmatch(r"[A-Za-z0-9_./@%+=:,~-]+", here):
            raise ConfigError(f"this script's own path, {here!r}, would not survive the "
                              f"launcher; set [hosts.{host}] start in the config")
        agent = agent.replace("{skill}", here)
    if "{worktree}" in trust and not dry_run:
        path = worktree_path(cfg, name)
        trust, trusted = (trust.replace("{worktree}", path), True) if path else ("", False)
    if trust:
        agent += " " + trust
    argv = fill(cfg["launcher"]["start"], {"name": name, "agent": agent, "prompt": prompt})
    if base is not None:
        argv += [cfg["launcher"]["base_flag"], base]
    return argv, name, trusted


RETURN_KEYS = ("status", "task", "changed", "evidence", "findings", "risks", "follow-ups",
               "questions", "knowledge")
KEY_LINE = re.compile(r"^(%s):" % "|".join(RETURN_KEYS))
NON_ALNUM = re.compile(r"^[^0-9A-Za-z]+")
FRAMING = re.compile(r"^[\s\u2500-\u257f]+")
# Hosts frame and bullet their lines, so only letters and digits around it disqualify a heading.
HEADING = re.compile(r"[^0-9A-Za-z]*### RETURN[^0-9A-Za-z]*")
# A host may draw a side panel on the same screen rows, far to the right of the text.
BESIDE = re.compile(r"(?<=\S) {8,}\S.*$")
STATUSES = ("done", "partial", "blocked", "needs-decision")
NO_BLOCK = "no RETURN block on screen"
# Not stopped: at work, or at one of its host's approvals. A block on screen would be an old one.
BUSY = ("working", "waiting")
NO_SCREEN = "could not read its screen"


def last_return(screen: str) -> dict | None:
    lines = [BESIDE.sub("", ln) for ln in screen.splitlines()]
    heads = [i for i, ln in enumerate(lines) if HEADING.fullmatch(ln)]
    if not heads:
        return None
    fields: dict[str, list[str]] = {}
    key = None
    for ln in lines[heads[-1] + 1:]:
        bare = NON_ALNUM.sub("", ln)
        m = KEY_LINE.match(bare)
        # Keys come in a fixed order, so a key that is not later than the field
        # being read is part of that field's text.
        if m and (key is None or RETURN_KEYS.index(m.group(1)) > RETURN_KEYS.index(key)):
            key = m.group(1)
            fields[key] = [bare[m.end():].strip()]
        elif key:
            # A continuation loses only whitespace and box-drawing, so a value
            # that starts with "(" survives.
            text = FRAMING.sub("", ln).strip()
            if text:
                fields[key].append(text)
    status = " ".join(fields.get("status", [])).strip()
    if not {"questions", "knowledge"} <= fields.keys() or status not in STATUSES:
        return None
    return {"status": status, "questions": " ".join(p for p in fields["questions"] if p)}


def _clip(text: str, width: int = 100) -> str:
    return text if len(text) <= width else text[:width - 1] + "\u2026"


def collect_rows(cfg: dict) -> list[dict]:
    launcher = cfg["launcher"]
    r = run_launcher(launcher["status"])
    try:
        agents = json.loads(r.stdout)["agents"]
        if not isinstance(agents, list) or not all(isinstance(a, dict) for a in agents):
            raise TypeError
    except (ValueError, KeyError, TypeError):
        raise ConfigError((r.stderr + r.stdout).strip() or "status printed nothing")
    me = os.environ.get("TMUX_PANE")
    rows = []
    for a in agents:
        row = {"name": a.get("worktree"), "branch": a.get("branch"), "host": a.get("agent_kind"),
               "state": a.get("status"), "updated_ts": a.get("updated_ts"),
               "self": bool(me) and a.get("pane_id") == me,
               "return_status": None, "questions": None, "captured": False}
        name = row["name"]
        usable = isinstance(name, str) and name and not name.startswith("-")
        if row["state"] not in BUSY and not row["self"] and usable:
            c = run_launcher(fill(launcher["capture"], {"name": name}))
            if not c.returncode:
                row["captured"] = True
                got = last_return(c.stdout)
                if got:
                    row["return_status"], row["questions"] = got["status"], got["questions"]
        rows.append(row)
    return rows


def render_table(rows: list[dict]) -> str:
    if not rows:
        return "no sessions"
    table = [("NAME", "STATE", "HOST", "RETURN", "QUESTIONS")]
    for r in rows:
        if r["self"]:
            q = "(this session)"
        elif r["questions"] is not None:
            q = _clip(r["questions"])
        elif r["state"] in BUSY:
            q = ""
        else:
            q = NO_BLOCK if r["captured"] else NO_SCREEN
        cells = ["" if v is None else str(v)
                 for v in (r["name"], r["state"], r["host"], r["return_status"])]
        table.append((*cells, q))
    widths = [max(len(t[i]) for t in table) for i in range(4)]
    return "\n".join(("  ".join(c.ljust(w) for c, w in zip(t, widths)) + "  " + t[4]).rstrip()
                     for t in table)


def overview(cfg: dict, as_json: bool) -> int:
    try:
        rows = collect_rows(cfg)
    except LauncherError as e:
        print(f"fleet: {e}", file=sys.stderr)
        return e.code
    except ConfigError as e:
        print(f"fleet: {e}", file=sys.stderr)
        return 1
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "captured"} for r in rows]))
    else:
        print(render_table(rows))
    return 0


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
                    help="print the launcher argv as JSON and run nothing; "
                         "{worktree} stays unfilled")
    ov = sub.add_parser("overview", help="one table of every session and why it stopped")
    ov.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        cfg = load_config(a.config)
        if a.command == "overview":
            return overview(cfg, a.json)
        argv, name, trusted = start_argv(cfg, a.ref, a.name, a.host, a.base, a.dry_run)
    except (ConfigError, ValueError) as e:
        print(f"fleet: {e}", file=sys.stderr)
        return 2
    if a.dry_run:
        print(json.dumps(argv))
        return 0
    if not trusted:
        print(f"fleet: {NO_PATH}", file=sys.stderr)
    try:
        r = run_launcher(argv)
    except LauncherError as e:
        print(f"fleet: {e}", file=sys.stderr)
        return e.code
    if r.returncode:
        sys.stderr.write(r.stderr or r.stdout or f"fleet: launcher exited with {r.returncode}\n")
        return r.returncode if r.returncode > 0 else 1
    print(f"started {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
