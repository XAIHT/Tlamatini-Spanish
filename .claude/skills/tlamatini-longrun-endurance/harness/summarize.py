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
"""Turn the two endurance results.json files into one verdict table."""

import glob
import json
import os
import sys

TREES = {"english": r"C:\Development\Tlamatini",
         "spanish": r"C:\Development\Tlamatini-Spanish"}

# outcome -> how it reads in the table
MARK = {"completed": "PASS  finished",
        "survived-waiting": "PASS  still alive (as required)",
        "KILLED": "FAIL  KILLED BY WATCHDOG",
        "did-not-complete": "FAIL  never finished",
        "died-early": "FAIL  died early"}


def newest(tree_root):
    c = sorted(glob.glob(os.path.join(tree_root, "Temp", "endurance_*",
                                      "results.json")), key=os.path.getmtime)
    return c[-1] if c else None


def axes(r):
    return ("term" if r["terminal"] else "headless",
            "input" if r["waits_input"] else "-",
            "key" if r["press_key"] else "-")


def main():
    loaded = {}
    for tree, root in TREES.items():
        p = newest(root)
        if not p:
            print("!! no results for %s" % tree)
            continue
        loaded[tree] = (p, json.load(open(p, encoding="utf-8")))

    if not loaded:
        return 2

    # ── 1. headline ────────────────────────────────────────────────────────
    killed = [(t, r) for t, (_, d) in loaded.items()
              for r in d["rows"] if r["watchdog_killed"]]
    failed = [(t, r) for t, (_, d) in loaded.items()
              for r in d["rows"] if not r["ok"]]
    print("=" * 96)
    print("ENDURANCE VERDICT")
    print("=" * 96)
    if not killed:
        print("NO legitimate long job was killed by the watchdog, in either tree.")
    else:
        print("!! %d job(s) were KILLED while doing legitimate work:" % len(killed))
        for t, r in killed:
            print("     %-8s %s (%ds, %s)" % (t, r["id"], r["seconds"],
                                              "/".join(axes(r))))
    for tree, (p, d) in loaded.items():
        rows = d["rows"]
        h = d["health"]
        print("  %-8s %2d/%2d pass | server before/during/after: %s / %s / %s"
              % (tree, sum(1 for r in rows if r["ok"]), len(rows),
                 h.get("before"), h.get("during"), h.get("after")))

    # ── 2. the matrix ──────────────────────────────────────────────────────
    print("\n" + "=" * 96)
    print("FULL MATRIX")
    print("=" * 96)
    print("%-8s %-10s %5s %-9s %-6s %-4s %-32s %8s"
          % ("tree", "agent", "secs", "console", "input", "key", "outcome", "elapsed"))
    print("-" * 96)
    for tree in sorted(loaded):
        rows = sorted(loaded[tree][1]["rows"],
                      key=lambda r: (r["agent"], r["seconds"], r["terminal"],
                                     r["waits_input"], r["press_key"]))
        for r in rows:
            con, inp, key = axes(r)
            print("%-8s %-10s %5d %-9s %-6s %-4s %-32s %8.1f"
                  % (tree, r["agent"], r["seconds"], con, inp, key,
                     MARK.get(r["outcome"], r["outcome"]), r["elapsed"]))

    # ── 3. by duration - the axis she asked about ──────────────────────────
    print("\n" + "=" * 96)
    print("BY DURATION  (did the 3 / 5 / 8 minute jobs survive?)")
    print("=" * 96)
    print("%-8s %6s %8s %8s %8s" % ("tree", "secs", "pass", "fail", "killed"))
    for tree in sorted(loaded):
        rows = loaded[tree][1]["rows"]
        for secs in sorted({r["seconds"] for r in rows}):
            sub = [r for r in rows if r["seconds"] == secs]
            print("%-8s %6d %8d %8d %8d"
                  % (tree, secs, sum(1 for r in sub if r["ok"]),
                     sum(1 for r in sub if not r["ok"]),
                     sum(1 for r in sub if r["watchdog_killed"])))

    # ── 4. proposals, derived from what actually happened ──────────────────
    print("\n" + "=" * 96)
    print("FIXING PROPOSALS (derived from the rows above)")
    print("=" * 96)
    if killed:
        head = [r for _, r in killed if not r["terminal"]]
        term = [r for _, r in killed if r["terminal"]]
        if head:
            worst = min(r["seconds"] for r in head)
            print("1. HEADLESS IDLE JOBS ARE BEING REAPED (shortest killed: %ds)."
                  % worst)
            print("   The watchdog kills on age>=hang_grace AND idle_ticks>=4, and an")
            print("   idle job is indistinguishable from a hang. Two honest fixes:")
            print("     a) raise command_watchdog_hang_grace_seconds above the longest")
            print("        legitimate job (>= %ds here), or" % (worst + 120))
            print("     b) let a long-running child carry an explicit long-run marker,")
            print("        the way a forked console carries the keep-console marker.")
            print("   Do NOT make the job busy-loop to dodge it - that deletes the")
            print("   only scenario that tests this.")
        if term:
            print("2. A FORKED CONSOLE WAS KILLED - this is a REGRESSION.")
            print("   is_protected_foreground_console exempts a console three ways")
            print("   (owns a window / parent owns one / keep-console marker). If one")
            print("   still died, check that executer.py and pythonxer.py both still")
            print("   pass TLAMATINI_KEEP_CONSOLE_ALIVE in the wrapper argv.")
    else:
        print("Nothing to fix on the kill axis: zero legitimate jobs were reaped,")
        print("including the idle headless ones at the longest duration.")
    other = [(t, r) for t, r in failed if not r["watchdog_killed"]]
    if other:
        print("\nNon-kill failures to investigate (%d):" % len(other))
        for t, r in other[:12]:
            print("   %-8s %-42s %s rc=%s" % (t, r["id"], r["outcome"],
                                              r["returncode"]))
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
