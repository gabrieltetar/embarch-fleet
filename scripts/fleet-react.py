#!/usr/bin/env python3
"""Put the watermark on one of the owner's messages: eyes, then check or x.

There is no state file for which messages the listener has handled -- the
reactions **are** the record (`slack.md`). `eyes` claims a message, and it goes
on before any work starts so the owner can see from a phone that it was picked
up; `white_check_mark` closes it; `x` says it failed. `robot_face` is not here:
`fleet-post.py` adds that to the fleet's own posts, so no caller can forget it.

**Why this refuses things.** Claiming a message asserts "I am treating this as
an instruction", so the same gate that decides what is actionable decides what
may be claimed -- `fleetslack.classify`, not a habit. Before 2026-09-10 the
reaction went on through the Slack MCP connector, which would happily mark
anything, and the gate lived only in a cron prompt's prose. That is the shape
that let a `subtype=bot_add` message -- Slack narrating the owner's own app
reinstall, authored by the owner, unreacted -- qualify on every prose test
there was. Marking it would have been the fleet taking an instruction from
Slack's own bookkeeping.

The one deliberate exception: a message already carrying `eyes` is claimed *by
this listener*, so `white_check_mark` and `x` are allowed onto it. That is the
whole point of a watermark -- it has to be able to advance.

Usage:
  scripts/fleet-react.py <ts> eyes
  scripts/fleet-react.py <ts> white_check_mark
  scripts/fleet-react.py <ts> x
  scripts/fleet-react.py <ts> eyes --remove      unclaim (a stop leaves the
                                                 owner's message unreacted)
  scripts/fleet-react.py <ts> eyes --force       skip the gate, and say why
Exit status: 0 done · 1 the call failed · 2 no bot token · 3 the gate refused.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleetslack as fs  # noqa: E402
from fleetconf import CONF  # noqa: E402

WATERMARK = ("eyes", "white_check_mark", "x")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ts", help="the message's Slack timestamp, from fleet-read.py")
    ap.add_argument("emoji", help="eyes | white_check_mark | x")
    ap.add_argument("--remove", action="store_true", help="take it off instead")
    ap.add_argument("--force", metavar="WHY",
                    help="claim something the gate refuses, and record why")
    args = ap.parse_args()

    emoji = args.emoji.strip(":")
    token = fs.read_token()
    if token is None:
        print(f"NOT CONFIGURED -- no bot token at {fs.TOKEN_FILE}", file=sys.stderr)
        return 2

    # Verify against the real message, not against what the caller believes it
    # is. reactions.get is the cheapest read that returns the message object.
    if emoji in WATERMARK and not args.remove and not args.force:
        r = fs.get(token, "reactions.get", channel=CONF.channel,
                   timestamp=args.ts, full="true")
        if not r.get("ok"):
            print(f"cannot verify {args.ts}: {fs.explain(r.get('error',''), r)}",
                  file=sys.stderr)
            return 1
        msg = r.get("message", {})
        ok, why = fs.classify(msg, CONF.owner)
        claimed = "eyes" in fs.reactions_of(msg)
        if not ok and not (claimed and emoji in ("white_check_mark", "x")):
            print(f"REFUSED: {args.ts} is not the fleet's to mark -- {why}.\n"
                  f"Claiming asserts this is an instruction from the owner. If it\n"
                  f"really is, --force '<why>' records the override.", file=sys.stderr)
            return 3

    method = "reactions.remove" if args.remove else "reactions.add"
    k = fs.call(token, method, channel=CONF.channel, timestamp=args.ts, name=emoji)
    if not k.get("ok"):
        print(f"{method} failed: {fs.explain(k.get('error',''), k)}", file=sys.stderr)
        return 1
    verb = "removed" if args.remove else "reacted"
    print(f"{verb} {emoji} on {args.ts}"
          + (f" (forced: {args.force})" if args.force else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
