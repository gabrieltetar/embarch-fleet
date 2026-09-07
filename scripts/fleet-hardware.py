#!/usr/bin/env python3
"""Answer "what hardware can the fleet reach right now?" from one buffered file.

Why this exists: a leg that wants to run a `bench` task has, until now, had to
find that out by doing it -- validate a role, read a task file's prose for the
console pins, discover from a failed study that a board is unplugged. Three
costs, all measured:

  * **Every bench task re-derived the bench.** The owner's facts (which board,
    which revision, which COM port and interface, the DUT-side sequence lore)
    lived in the prose of ONE task, `tasks/api/029`. An agent that did not
    happen to read that task did not have them, and two legs re-ran the same
    BLE census five minutes apart to learn the same nothing.
  * **"Is a board attached?" cost a hardware attach to ask.** `validate` takes
    Core's `hw_lock`. Asking it four times at step 0, once per role, is four
    attaches to answer a question whose answer changes when somebody unplugs a
    cable -- rarely, and never mid-leg.
  * **Stated and measured facts were indistinguishable once written down.** A
    hardware ID Core read over JTAG and a PPG revision the owner said out loud
    both ended up as bold prose in a task file. `hardware.json` tags each one,
    because reading the second as the first is this suite's most repeated
    defect (`never-infer-dut-semantics`).

So: `hardware.toml` in this repo holds what only the owner knows, this script
merges it with what Core reports live, and `<state_dir>/hardware.json` is the
buffer everything else reads. The buffer is deliberately OUTSIDE every repo --
it is machine state, not a fact about the suite, and a committed one would be
wrong on any other bench.

Modes:
  fleet-hardware.py                 print the buffer, and how old it is
  fleet-hardware.py --refresh       re-measure and rewrite the buffer
  fleet-hardware.py --check         re-measure and diff against the buffer;
                                    exit 1 if the bench moved, 2 if unreadable
  fleet-hardware.py --json          machine-readable, with any mode

Exit status, for a leg's step 0:
  0  the buffer is present and (for --check) still true
  1  the bench has moved, or a role is unattached, or --refresh could not
     reach Core; the message says which
  2  no buffer and none could be written
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
import tomllib  # noqa: E402

HARDWARE_TOML = Path(__file__).resolve().parent.parent / "hardware.toml"
# The identifying half -- client product names, repo names, and the workspace
# paths that contain them -- lives outside every repo, beside the client-name
# denylist and for the same reason `fleet.toml` gives for that one: a committed
# record of the names you are hiding is the leak it exists to prevent. This
# split was not designed up front; `check-client-names.py` went RED on the
# first version of `hardware.toml` and was right to.
LOCAL_TOML = CONF.state_dir / "hardware-local.toml"
BUFFER = CONF.state_dir / "hardware.json"
# A buffer older than this is reported stale rather than trusted. Chosen
# against what actually changes: a cable, over hours -- not a study, over
# seconds. A leg is four units and well under an hour, so one refresh at step 0
# covers a whole leg.
STALE_AFTER_S = 4 * 3600


def load_facts() -> dict:
    """`hardware.toml`, with the machine-local overlay merged over it.

    One level of merge, per table, which is all the shape needs: the overlay
    supplies `[api]` and the client-named half of `[dut_ble]`. A missing
    overlay is not an error -- the refresh then says it has no API binary
    rather than guessing one.
    """
    with open(HARDWARE_TOML, "rb") as fh:
        facts = tomllib.load(fh)
    try:
        with open(LOCAL_TOML, "rb") as fh:
            local = tomllib.load(fh)
    except OSError:
        facts.setdefault("_notes", []).append(
            f"no local overlay at {LOCAL_TOML}; client-specific values are absent")
        return facts
    for key, val in local.items():
        if isinstance(val, dict) and isinstance(facts.get(key), dict):
            facts[key].update(val)
        else:
            facts[key] = val
    return facts


def api(facts: dict, *args: str) -> tuple[int, dict | None, str]:
    """Run the embarch-api CLI and parse its JSON.

    Shelling out rather than talking HTTP directly is deliberate: base-url
    discovery ("auto", because WSL2's host IP moves on every restart) and the
    bearer token both live in that binary, and a second implementation of
    either is a second thing to keep true.
    """
    cfg = facts.get("api") or {}
    if not cfg.get("binary") or not cfg.get("config"):
        return 1, None, (f"no [api] binary/config -- add them to {LOCAL_TOML}")
    cmd = [cfg["binary"], "--config", cfg["config"], "--json", *args]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, None, f"{args[0]}: {e}"
    # The CLI writes tracing lines to stderr and one JSON object to stdout.
    out = p.stdout.strip()
    if not out:
        return p.returncode, None, (p.stderr.strip().splitlines() or ["no output"])[-1]
    try:
        start, end = out.index("{"), out.rindex("}")
        return p.returncode, json.loads(out[start:end + 1]), ""
    except (ValueError, json.JSONDecodeError) as e:
        return p.returncode, None, f"{args[0]}: unparseable output: {e}"


def suffix_candidates(hardware_id: str, byte_index: list[int]) -> list[str]:
    """The BLE name suffixes an enrolled hardware ID could produce.

    Two, not one, and that is the honest answer rather than a hedge: Core's
    hardware ID and the chip's own `hwinfo_get_device_id()` are known to
    disagree on byte order along at least one path -- dev-bench reads
    `6fcddc36cb781b71` over JTAG and self-reports the 32-bit-word-swapped
    `cb781b716fcddc36`. Until one is confirmed on air, both are live.
    """
    try:
        raw = bytes.fromhex(hardware_id)
    except ValueError:
        return []
    if len(raw) != 8 or any(i >= 8 for i in byte_index):
        return []
    swapped = raw[4:] + raw[:4]
    out = []
    for order in (raw, swapped):
        out.append("".join(f"{order[i]:02X}" for i in byte_index))
    return list(dict.fromkeys(out))


def measure(facts: dict) -> dict:
    """Everything Core will tell us right now, plus the owner's facts beside it."""
    now = time.time()
    snap: dict = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "generated_at_epoch": int(now),
        "core": {"reachable": False},
        "probes": [],
        "roles": [],
        "lore": facts.get("lore", {}),
        "notes": list(facts.get("_notes", [])),
    }

    rc, status, err = api(facts, "status")
    if status is None:
        snap["core"]["error"] = err
        snap["notes"].append(
            "Core did not answer, so NOTHING below is measured -- every role's "
            "attached flag is unknown, not false. A bench task must leave its "
            "task `open` on this, never `blocked`.")
        # The owner's half is still worth writing: it is true when Core is down.
        for role in facts.get("roles", []):
            snap["roles"].append({"stated": role, "measured": None,
                                  "attached": None})
        return snap

    # `status` answers with Core's own probe list; the version numbers this
    # buffer wants are on `versions`, which asks the binary rather than Core.
    # Kept separate on purpose -- a stale MCP/CLI binary against a newer Core
    # is a real state here (`embarch-api-mcp-binary-goes-stale`), and one
    # merged "version" field would hide exactly that.
    snap["core"] = {"reachable": True}
    _, vers, verr = api(facts, "versions")
    snap["versions"] = vers if vers is not None else {"error": verr}
    snap["probes"] = status.get("probes", [])
    attached_serials = {p.get("serial_number") for p in snap["probes"]}

    for role in facts.get("roles", []):
        name = role["role"]
        rc, val, err = api(facts, "validate", "--role", name)
        entry: dict = {"stated": role, "measured": None, "attached": None}
        if val is not None and val.get("ok"):
            entry["measured"] = {
                "hardware_id": val.get("hardware_id"),
                "probe_serial": val.get("probe_serial"),
                "chip": val.get("chip"),
                "confirmed_at_utc_ms": val.get("confirmed_at_utc_ms"),
                "source": "measured over the debug probe by embarch-core /validate",
            }
            entry["attached"] = val.get("probe_serial") in attached_serials
        elif val is not None and val.get("recorded_hardware_id"):
            entry["mismatch"] = {
                "recorded_hardware_id": val.get("recorded_hardware_id"),
                "live_hardware_id": val.get("live_hardware_id"),
                "reason": val.get("reason"),
                "fix_it_url": val.get("fix_it_url"),
            }
            entry["attached"] = True
        else:
            entry["error"] = err or "validate did not report ok"
            entry["attached"] = False
        snap["roles"].append(entry)

    ble = facts.get("dut_ble")
    if ble:
        dut = next((r for r in snap["roles"] if r["stated"]["role"] == "dut"), None)
        hwid = (dut or {}).get("measured", {}).get("hardware_id") if dut else None
        snap["dut_ble"] = dict(ble)
        snap["dut_ble"]["derived_from_hardware_id"] = hwid
        tmpl = ble.get("name_template", "{suffix}")
        snap["dut_ble"]["name_candidates"] = [
            tmpl.format(suffix=s)
            for s in suffix_candidates(hwid or "", ble.get("suffix_from_hardware_id_bytes", []))
        ] if hwid else []
        snap["dut_ble"]["source"] = (
            "STATED -- read off the client firmware's advertising code, not "
            "observed on this board. Confirm by connecting before relying on it.")
    return snap


def write_buffer(snap: dict) -> None:
    """Atomic, because a leg's step 0 may read this while a refresh runs."""
    BUFFER.parent.mkdir(parents=True, exist_ok=True)
    tmp = BUFFER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, BUFFER)


def read_buffer() -> dict | None:
    try:
        return json.loads(BUFFER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def render(snap: dict, stale: int | None) -> str:
    lines = []
    core = snap.get("core", {})
    if core.get("reachable"):
        v = snap.get("versions") or {}
        vtxt = ", ".join(f"{k}={v[k]}" for k in sorted(v) if k != "success") or "versions unknown"
        lines.append(f"Core: reachable  ({vtxt})")
    else:
        lines.append(f"Core: UNREACHABLE -- {core.get('error', 'no reason recorded')}")
    for r in snap.get("roles", []):
        s, m = r["stated"], r.get("measured")
        head = f"  {s['role']:<10} {s.get('board', '?')}"
        if s.get("revision") is not None:
            head += f" rev{s['revision']}"
        if r.get("attached") is None:
            lines.append(head + "   attached: UNKNOWN (Core did not answer)")
        elif r.get("mismatch"):
            mm = r["mismatch"]
            lines.append(head + "   TOPOLOGY MISMATCH: recorded "
                         f"{mm['recorded_hardware_id']} != live {mm['live_hardware_id']}")
        elif m:
            lines.append(head + f"   probe {m['probe_serial']} hw {m['hardware_id']} "
                                f"({m['chip']})  attached: yes")
        else:
            lines.append(head + f"   attached: no -- {r.get('error', '')}")
        for k in ("link_port", "link_port_interface", "console_uart", "console_tx", "console_rx"):
            if s.get(k) is not None:
                lines.append(f"             {k} = {s[k]}   [stated]")
    ble = snap.get("dut_ble")
    if ble:
        cands = ", ".join(ble.get("name_candidates") or []) or "none (no hardware id)"
        lines.append(f"  DUT BLE name candidates: {cands}"
                     f"   [{'confirmed' if ble.get('confirmed_on_air') else 'UNCONFIRMED'}]")
    for n in snap.get("notes", []):
        lines.append(f"  NOTE: {n}")
    if stale is not None:
        age = int(stale / 60)
        lines.append(f"  buffer is {age} min old"
                     + ("  -- STALE, run --refresh" if stale > STALE_AFTER_S else ""))
    return "\n".join(lines)


def comparable(snap: dict) -> dict:
    """The part of a snapshot that says the bench moved, with the clock dropped."""
    return {
        "core_reachable": snap.get("core", {}).get("reachable"),
        "probes": sorted(p.get("serial_number", "") for p in snap.get("probes", [])),
        "roles": {
            r["stated"]["role"]: {
                "attached": r.get("attached"),
                "hardware_id": (r.get("measured") or {}).get("hardware_id"),
                "mismatch": bool(r.get("mismatch")),
            } for r in snap.get("roles", [])
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="re-measure and rewrite the buffer")
    ap.add_argument("--check", action="store_true",
                    help="re-measure and diff against the buffer without rewriting it")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    facts = load_facts()

    if args.refresh:
        snap = measure(facts)
        write_buffer(snap)
        print(json.dumps(snap, indent=2) if args.as_json else render(snap, 0))
        unattached = [r["stated"]["role"] for r in snap["roles"] if r.get("attached") is not True]
        return 1 if (unattached or not snap["core"]["reachable"]) else 0

    if args.check:
        buffered = read_buffer()
        live = measure(facts)
        if buffered is None:
            if args.as_json:
                print(json.dumps({"verdict": "NO_BUFFER", "live": live}, indent=2))
            else:
                print("no buffer at " + str(BUFFER) + " -- run --refresh")
                print(render(live, None))
            return 2
        same = comparable(buffered) == comparable(live)
        if args.as_json:
            print(json.dumps({"verdict": "SAME" if same else "MOVED",
                              "buffered": comparable(buffered),
                              "live": comparable(live)}, indent=2))
        else:
            print(("bench unchanged since the buffer was written"
                   if same else "BENCH MOVED since the buffer was written:"))
            if not same:
                print(render(live, None))
        return 0 if same else 1

    snap = read_buffer()
    if snap is None:
        print(f"no buffer at {BUFFER} -- run --refresh", file=sys.stderr)
        return 2
    age = time.time() - snap.get("generated_at_epoch", 0)
    print(json.dumps(snap, indent=2) if args.as_json else render(snap, age))
    return 0


if __name__ == "__main__":
    sys.exit(main())
