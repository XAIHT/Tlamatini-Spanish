---
name: tlamatini-longrun-endurance
description: "Verify that a long-running job (3, 5 and 8 minutes) is never killed by Tlamatini's infrastructure, and that Tlamatini keeps serving while it runs. Runs a 48-scenario matrix per tree (Executer + Pythonxer x 3 durations x terminal/headless x waits-input x press-a-key) against both trees on their own ports, with the real CommandWatchdog at production defaults. Invoke for 'endurance test', 'long-run test', '8 minute test', 'run the matrix', or after any change to command_watchdog.py, orphan_reaper.py, executer.py or pythonxer.py."
---

# Long-run endurance matrix

Confirms that a legitimate long job finishes, and that a forked console waiting
on a keypress is never reaped.

## The matrix (per tree)

| axis | values | n |
|---|---|---|
| agent | `executer`, `pythonxer` | 2 |
| duration | 180 s, 300 s, 480 s | 3 |
| terminal | forked console, headless | 2 |
| waits_input | script blocks on `input()` / `set /p` | 2 |
| press_key | "press a key to finish" tail | 2 |

**48 per tree, 96 across both.** English on :8000, Spanish on :8010, in parallel.

## Run it

```bash
python .claude/skills/tlamatini-longrun-endurance/harness/endurance.py --tree english --port 8000
python .claude/skills/tlamatini-longrun-endurance/harness/endurance.py --tree spanish --port 8010
```

Both in visible foreground windows (`Start-Process powershell -NoExit …`,
`dangerouslyDisableSandbox:true`) — half the matrix is about a visible console.

Flags: `--durations 20` for a smoke test, `--max-windows N` for how many
consoles may be on screen at once (default 4 per tree).

## Why the wait is a SLEEP, not a busy loop

A CPU-busy job is the easy case: `_subtree_metrics` sees the CPU and the
watchdog can never reach its kill condition. The job that exercises the
infrastructure is the idle one — a build waiting on a fetch, a script waiting on
a human — because zero CPU and zero I/O is what a hang looks like.

## Two expectations

* **`complete`** — no input wait, or headless (stdin is EOF, so the prompt
  returns at once). Must exit 0 having lasted its duration.
* **`survive_waiting`** — forked console **and** an input wait. Must still be
  alive and unkilled when the measurement window closes. The harness then closes
  it, and that counts as a pass.

## Harness rules

* `stdin=subprocess.DEVNULL` on every spawned scenario. Without it the child
  inherits the harness console's stdin and a "headless" scenario is not
  stdin-less at all.
* Terminal scenarios run in waves of `--max-windows`, grouped by duration.
  Headless ones run all at once.
* "Alive" means the agent **or** its console. Executer returns once it has
  launched a forked window, so testing only the agent process scores a healthy
  waiting console as died-early.
* A watchdog kill lands on the **shell**, not the agent, so attribute kills by
  matching the scenario's runtime dir in the killed command line.

## What is real here

* The agents are the real pool scripts, copied into an isolated runtime dir and
  driven by the same `config.yaml` contract the server uses.
* The watchdog is the real `CommandWatchdog` with production defaults
  (tick 15 s, hang grace 180 s, 4 idle ticks), watching the harness's own
  descendants.
* Both servers run throughout and are health-checked before, during and after.

## Reading the result

`results.json` lands in `<tree>/Temp/endurance_<tree>_<stamp>/`. Per row:
`expectation`, `outcome` (`completed` / `survived-waiting` / `KILLED` /
`did-not-complete` / `died-early`), `watchdog_killed`, `alive_at_close`,
`elapsed` (measured when that scenario's wave closed).

`outcome: KILLED` is the finding that matters: the watchdog reaped a job that
was doing legitimate work.

## Notes

An idle headless job is indistinguishable from a hang by design. The kill
condition is `age >= hang_grace AND idle_ticks >= 4`, so a sleeping job with no
console is reapable from about 240 s unless its launcher declares it
long-running. A forked console is exempt three ways
(`orphan_reaper.is_protected_foreground_console`). Do not make the harness
busy-loop to avoid a kill — that deletes the scenario under test.

English :8000 also owns the MCP helpers :8765 / :50051; those are a separate
axis from `django_port` and collide between two instances, so whichever server
starts second runs without them.
