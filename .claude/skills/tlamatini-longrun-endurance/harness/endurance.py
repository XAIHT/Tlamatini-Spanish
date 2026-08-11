# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Long-run endurance matrix: does a legitimate long job finish?

Usage:
    python endurance.py --tree english --port 8000
    python endurance.py --tree spanish --port 8010
    (--durations 20 for a smoke test, --max-windows N for on-screen consoles)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime

# ── Where things are ────────────────────────────────────────────────────────
TREES = {
    "english": r"C:\Development\Tlamatini",
    "spanish": r"C:\Development\Tlamatini-Spanish",
}
AGENTS = ("executer", "pythonxer")
DEFAULT_DURATIONS = (180, 300, 480)          # 3 min, 5 min, 8 min
SLACK_SECONDS = 90                           # grace after the longest scenario
MAX_VISIBLE_WINDOWS = 4                      # consoles on screen at once, per tree


# ── The scenario scripts ────────────────────────────────────────────────────
def _python_script(seconds, waits_input, press_key):
    """The body Pythonxer will run."""
    lines = [
        "import sys, time",
        "print('SCENARIO START', flush=True)",
    ]
    if waits_input:
        lines += [
            "print('WAITING FOR INPUT (no console -> EOF is expected)', flush=True)",
            "try:",
            "    _ = input('type something: ')",
            "except EOFError:",
            "    print('EOF - no interactive stdin', flush=True)",
        ]
    lines += [
        "time.sleep(%d)" % seconds,
        "print('SCENARIO SLEPT %d SECONDS', flush=True)" % seconds,
    ]
    if press_key:
        lines += [
            "try:",
            "    _ = input('press a key to finish: ')",
            "except EOFError:",
            "    print('EOF on press-a-key', flush=True)",
        ]
    lines += ["print('SCENARIO DONE', flush=True)", "sys.exit(0)"]
    return "\n".join(lines)


def _bat_script(seconds, waits_input, press_key):
    """The body Executer will run (a .bat)."""
    out = ["@echo SCENARIO START"]
    if waits_input:
        out += ["@set /p DUMMY=type something: "]
    # timeout /t needs a console; ping is the portable idle sleep on Windows
    out += ["@ping -n %d 127.0.0.1 > nul" % (seconds + 1),
            "@echo SCENARIO SLEPT %d SECONDS" % seconds]
    if press_key:
        out += ["@set /p DUMMY=press a key to finish: "]
    out += ["@echo SCENARIO DONE", "@exit /b 0"]
    return "\n".join(out)


def build_matrix(durations):
    combos = []
    for agent in AGENTS:
        for secs in durations:
            for terminal in (False, True):
                for waits_input in (False, True):
                    for press_key in (False, True):
                        combos.append({
                            "agent": agent,
                            "seconds": secs,
                            "terminal": terminal,
                            "waits_input": waits_input,
                            "press_key": press_key,
                            "id": "%s_%ds_%s_%s_%s" % (
                                agent, secs,
                                "term" if terminal else "headless",
                                "input" if waits_input else "noinput",
                                "key" if press_key else "nokey"),
                        })
    return combos


# ── Spawning one scenario as a REAL pool agent ──────────────────────────────
def spawn_scenario(tree_root, workdir, combo):
    """Copy the real agent into an isolated runtime dir and run it."""
    agent = combo["agent"]
    src = os.path.join(tree_root, "Tlamatini", "agent", "agents", agent)
    dst = os.path.join(workdir, combo["id"])
    if os.path.isdir(dst):
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)

    if agent == "pythonxer":
        body = _python_script(combo["seconds"], combo["waits_input"],
                              combo["press_key"])
        cfg = {
            "script": body,
            "execute_forked_window": combo["terminal"],
            "ruff_blocking": False,
            "source_agents": [], "target_agents": [],
        }
    else:
        body = _bat_script(combo["seconds"], combo["waits_input"],
                           combo["press_key"])
        cfg = {
            "script": body,
            "execute_forked_window": combo["terminal"],
            "non_blocking": False,
            "source_agents": [], "target_agents": [],
        }

    # config.yaml written by hand (no yaml dep needed for these scalars)
    with open(os.path.join(dst, "config.yaml"), "w", encoding="utf-8") as fh:
        fh.write("script: |\n")
        for ln in body.splitlines():
            fh.write("  %s\n" % ln)
        for k, v in cfg.items():
            if k == "script":
                continue
            if isinstance(v, bool):
                fh.write("%s: %s\n" % (k, "true" if v else "false"))
            elif isinstance(v, list):
                fh.write("%s: []\n" % k)
            else:
                fh.write("%s: %r\n" % (k, v))

    env = os.environ.copy()
    env["TLAMATINI_TEMP"] = os.path.join(tree_root, "Temp")
    # Keep a finished console readable only briefly: this harness is unattended.
    env["FORKED_WINDOW_HOLD_SECONDS"] = "20"

    # stdin=DEVNULL is load-bearing: without it the child inherits this
    # harness's console stdin and a "headless" scenario is not stdin-less.
    proc = subprocess.Popen(
        [sys.executable, "%s.py" % agent],
        cwd=dst, env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc, dst


def read_verdict(rundir, combo):
    """What the agent itself reported, from its own log."""
    log = os.path.join(rundir, "%s.log" % combo["id"])
    if not os.path.isfile(log):
        # the agent names its log after the directory it lives in
        cands = [f for f in os.listdir(rundir) if f.endswith(".log")]
        if not cands:
            return "no-log", ""
        log = os.path.join(rundir, cands[0])
    try:
        with open(log, encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
    except OSError:
        return "unreadable", ""
    tail = txt[-1200:]
    if "EXECUTION SUCCESS" in txt or "RESULT: TRUE" in txt:
        return "SUCCESS", tail
    if "EXECUTION FAILED" in txt or "RESULT: FALSE" in txt:
        return "FAILED", tail
    if "timed out" in txt:
        return "TIMEOUT", tail
    return "unknown", tail


# ── Server health ───────────────────────────────────────────────────────────
def server_alive(port, timeout=6):
    """Is the Django server on *port* actually serving?

    Probes ``/agent/version/`` - an OPEN endpoint - NOT ``/``. The first
    version of this probe asked for ``/``, which is not a route at all, so it
    reported the server dead even when it was perfectly healthy. Any HTTP
    response below 500 (including a redirect or a 403) proves something is
    serving; only a connection error means down.
    """
    for path in ("/agent/version/", "/agent/"):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d%s" % (port, path),
                                        timeout=timeout) as r:
                return r.status < 500
        except urllib.error.HTTPError as exc:
            return exc.code < 500
        except Exception:
            continue
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", choices=sorted(TREES), required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--durations", default="")
    ap.add_argument("--max-windows", type=int, default=MAX_VISIBLE_WINDOWS,
                    dest="max_windows",
                    help="how many forked consoles may be on screen at once")
    args = ap.parse_args()

    durations = DEFAULT_DURATIONS
    if args.durations.strip():
        durations = tuple(int(x) for x in args.durations.split(",") if x.strip())

    tree_root = TREES[args.tree]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workdir = os.path.join(tree_root, "Temp", "endurance_%s_%s" % (args.tree, stamp))
    os.makedirs(workdir, exist_ok=True)

    print("=" * 78)
    print("ENDURANCE MATRIX  tree=%s  port=%d" % (args.tree, args.port))
    print("durations=%s   scenarios=%d" % (durations, len(build_matrix(durations))))
    print("workdir=%s" % workdir)
    print("=" * 78, flush=True)

    health = {"before": server_alive(args.port)}
    print("server on :%d alive BEFORE = %s" % (args.port, health["before"]), flush=True)

    # ── the REAL watchdog, production defaults, watching our own children ──
    sys.path.insert(0, os.path.join(tree_root, "Tlamatini"))
    killed_pids = []
    # Record what was killed: the watchdog kills the SHELL, not the agent,
    # so a scenario is matched by its runtime dir in the command line.
    killed_cmdlines = []
    watchdog = None
    try:
        from agent import command_watchdog
        import psutil

        def _descendants():
            try:
                return [p for p in psutil.Process(os.getpid()).children(recursive=True)]
            except Exception:
                return []

        def _killer(proc, errors):
            try:
                killed_pids.append(int(proc.pid))
                try:
                    # BEFORE the kill - a dead process has no command line.
                    killed_cmdlines.append(" ".join(proc.cmdline() or []).lower())
                except Exception:
                    pass
                proc.kill()
            except Exception as exc:
                errors.append(str(exc))

        watchdog = command_watchdog.CommandWatchdog(
            our_pid=os.getpid(),
            descendant_provider=_descendants,
            killer=_killer,
        )
        print("watchdog: REAL CommandWatchdog, production defaults "
              "(tick=%.0fs grace=%.0fs idle_ticks=%d)"
              % (watchdog.tick_seconds, watchdog.hang_grace_seconds,
                 watchdog.required_idle_ticks), flush=True)
    except Exception as exc:
        print("watchdog: COULD NOT LOAD (%s) - kills will NOT be measured" % exc,
              flush=True)

    # A forked console waiting on a keypress passes by SURVIVING.
    def expectation(c):
        if c["terminal"] and (c["waits_input"] or c["press_key"]):
            return "survive_waiting"
        return "complete"

    # Headless scenarios run all at once; terminal ones in waves of
    # --max-windows, grouped by duration.
    stop = threading.Event()

    def _tick():
        while not stop.is_set():
            if watchdog is not None:
                try:
                    watchdog.scan_and_reap()
                except Exception:
                    pass
            stop.wait(5)

    th = threading.Thread(target=_tick, daemon=True)
    th.start()

    procs = {}
    health["during"] = None
    combos = build_matrix(durations)
    started = time.time()

    def run_batch(batch, label):
        """Spawn one wave, watch it for its own window, snapshot, close it."""
        local = []
        for c in batch:
            try:
                p, d = spawn_scenario(tree_root, workdir, c)
                rec = {"proc": p, "dir": d, "combo": c, "pid": p.pid,
                       "t0": time.time()}
            except Exception as exc:
                rec = {"proc": None, "dir": "", "combo": c, "pid": -1,
                       "t0": time.time(), "spawn_error": str(exc)}
            procs[c["id"]] = rec
            local.append(rec)
            time.sleep(0.15)
        window = max(c["seconds"] for c in batch) + SLACK_SECONDS
        print("[%s] %d scenario(s) up, window %ds" % (label, len(local), window),
              flush=True)
        deadline = time.time() + window
        while time.time() < deadline:
            alive = [r for r in local
                     if r["proc"] is not None and r["proc"].poll() is None]
            if health["during"] is None and time.time() - started > 60:
                health["during"] = server_alive(args.port)
                print("server alive DURING = %s (%d running)"
                      % (health["during"], len(alive)), flush=True)
            if not alive:
                break
            time.sleep(5)
        # Snapshot before touching anything. "Alive" means the agent OR its
        # console: Executer returns once it has launched a forked window.
        live_cmdlines = []
        try:
            import psutil as _ps
            for _p in _ps.process_iter(["cmdline"]):
                try:
                    cl = _p.info.get("cmdline") or []
                    if cl:
                        live_cmdlines.append(" ".join(cl).lower())
                except Exception:
                    pass
        except Exception:
            pass
        for r in local:
            agent_alive = (r["proc"] is not None and r["proc"].poll() is None)
            d = (r.get("dir") or "").lower()
            console_alive = bool(d) and any(d in cl for cl in live_cmdlines)
            r["agent_alive_at_close"] = agent_alive
            r["console_alive_at_close"] = console_alive
            r["alive_at_close"] = agent_alive or console_alive
            r["elapsed"] = time.time() - r["t0"]
        # Close the wave: whole process tree, so no window is left behind.
        for r in local:
            if not r.get("alive_at_close"):
                continue
            try:
                import psutil as _ps
                for ch in _ps.Process(r["proc"].pid).children(recursive=True):
                    try:
                        ch.kill()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                r["proc"].kill()
            except Exception:
                pass
        # A console whose agent already returned is matched by runtime dir.
        try:
            import psutil as _ps
            dirs = [(r.get("dir") or "").lower() for r in local if r.get("dir")]
            for _p in _ps.process_iter(["cmdline"]):
                try:
                    cl = " ".join(_p.info.get("cmdline") or []).lower()
                    if cl and any(d in cl for d in dirs):
                        _p.kill()
                except Exception:
                    pass
        except Exception:
            pass
        exited = sum(1 for r in local if not r.get("alive_at_close"))
        print("[%s] closed: %d exited on their own, %d still waiting (by design)"
              % (label, exited, len(local) - exited), flush=True)

    headless = [c for c in combos if not c["terminal"]]
    if headless:
        run_batch(headless, "headless x%d" % len(headless))

    terminal = [c for c in combos if c["terminal"]]
    for secs in sorted({c["seconds"] for c in terminal}, reverse=True):
        same = [c for c in terminal if c["seconds"] == secs]
        for k in range(0, len(same), args.max_windows):
            wave = same[k:k + args.max_windows]
            run_batch(wave, "terminal %ds wave %d/%d"
                      % (secs, k // args.max_windows + 1,
                         (len(same) + args.max_windows - 1) // args.max_windows))

    stop.set()

    health["after"] = server_alive(args.port)
    print("server alive AFTER = %s" % health["after"], flush=True)

    # ── results ────────────────────────────────────────────────────────────
    rows = []
    for cid, v in procs.items():
        c = v["combo"]
        # measured when this scenario's own wave closed, NOT now -
        # otherwise every early wave looks hours long.
        elapsed = v.get("elapsed", time.time() - v["t0"])
        rc = v["proc"].returncode if v["proc"] is not None else None
        verdict, tail = read_verdict(v["dir"], c) if v["dir"] else ("spawn-error", "")
        # A kill counts against this scenario if the watchdog killed the agent
        # itself OR any shell whose command line names this scenario's dir.
        _d = (v.get("dir") or "").lower()
        was_killed = (v["pid"] in killed_pids
                      or (bool(_d) and any(_d in cl for cl in killed_cmdlines)))
        expected = c["seconds"]
        exp = expectation(c)
        alive_at_close = bool(v.get("alive_at_close"))

        if exp == "survive_waiting":
            # It must STILL BE THERE, unkilled, at the end of the window.
            ok = alive_at_close and not was_killed
            outcome = ("survived-waiting" if ok
                       else ("KILLED" if was_killed else "died-early"))
        else:
            ok = (rc == 0 and not was_killed
                  and elapsed >= expected * 0.9)
            outcome = ("completed" if ok
                       else ("KILLED" if was_killed else "did-not-complete"))

        rows.append({
            "id": cid,
            "agent": c["agent"], "seconds": expected,
            "terminal": c["terminal"], "waits_input": c["waits_input"],
            "press_key": c["press_key"],
            "expectation": exp,
            "elapsed": round(elapsed, 1),
            "returncode": rc,
            "verdict": verdict,
            "watchdog_killed": was_killed,
            "alive_at_close": alive_at_close,
            "agent_alive_at_close": bool(v.get("agent_alive_at_close")),
            "console_alive_at_close": bool(v.get("console_alive_at_close")),
            "outcome": outcome,
            "ok": bool(ok),
            "tail": tail[-400:],
        })

    out = {
        "tree": args.tree, "port": args.port, "stamp": stamp,
        "durations": list(durations), "health": health,
        "watchdog_killed_pids": killed_pids,
        "watchdog_killed_cmdlines": killed_cmdlines,
        "rows": rows,
    }
    dest = os.path.join(workdir, "results.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    ok = sum(1 for r in rows if r["ok"])
    killed = sum(1 for r in rows if r["watchdog_killed"])
    print("\n%s" % ("=" * 78))
    print("RESULT %s: %d/%d survived and finished | watchdog killed %d"
          % (args.tree, ok, len(rows), killed))
    print("server health before/during/after: %s / %s / %s"
          % (health["before"], health["during"], health["after"]))
    print("results -> %s" % dest)
    print("=" * 78, flush=True)
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
