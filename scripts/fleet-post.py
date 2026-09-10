#!/usr/bin/env python3
"""Post to #embarch-fleet as the FLEET, with the technical half in a thread.

Why this replaces posting through the Slack connector: the connector
authenticates **as the owner**, so every message the fleet wrote was authored by
the owner. Two costs, and the second is the one that was never fixable by
formatting. A channel where the fleet and the owner are the same author reads as
one person talking to themselves, and `<@owner>` inside an owner-authored
message badges nothing -- Slack only notifies you about a message somebody else
sent. `fleet-alert.py` routed around the second with an incoming webhook, which
posts under the app's identity; this generalises that to every post.

**A webhook could not have been the answer, and that is why this uses a bot
token instead.** An incoming webhook replies `ok` and nothing else -- it never
returns the `ts` of the message it just created, and a thread reply needs its
parent's `ts`. So a webhook can post a summary or a detail but can never attach
one to the other. `chat.postMessage` returns the `ts`, which is the whole
mechanism here: post the plain line, keep the `ts`, reply the technical block
into its thread.

**The shape every fleet post now takes:**

  - **The message is one or two plain sentences** -- what happened, in words an
    engineer reading a phone at a red light can act on. No SHAs, no file paths,
    no gate output, no counts of things nobody asked about.
  - **The technical half goes in `--detail`**, posted as a thread reply. It is
    there when you want it and folded away when you do not, which is as close to
    an expandable section as Slack has.
  - **`--action` is the only thing that notifies.** It prefixes the owner
    mention and marks the post as a request, so the channel answers "is this
    asking me for something" without being read. Everything else is FYI and
    stays silent. `ops.md` §3 fixes the set of things allowed to use it; adding
    to that set is how a notification channel becomes a feed nobody reads.

**Degrading rather than failing.** With no bot token, an `--action` post falls
back to `fleet-alert.py`'s webhook so the owner is still reached, prints that
the detail could not be threaded, and exits 3 -- a caller that ignores it still
notified somebody. An FYI post with no token exits 2 and says so, the same way
`fleet-alert.py` does: a muted channel that looks fine is worse than a loud one.

**The read side moved here too, on 2026-09-10.** This file was for a while the
only thing holding the bot token, while every read went through the connector as
the owner; `fleetslack.py` now owns the transport for both directions and
`fleet-read.py` is the eyes. Nothing in the fleet touches the owner's personal
OAuth any more, and `fleet-slack-doctor.py` is what says so out loud.

Setup (the owner's, once -- same app as the webhook):
  1. api.slack.com/apps -> your fleet app -> OAuth & Permissions
  2. Bot Token Scopes: the set in `fleetslack.NEEDED_SCOPES` -- `chat:write`,
     `reactions:write`, `reactions:read`, `groups:history`, `groups:read`,
     `files:read`, `files:write`. Each one's cost if absent is in that dict.
  3. Install to Workspace, copy the Bot User OAuth Token (starts `xoxb-`)
  4. In Slack, invite the app to the channel:  /invite @<your app name>
  5. Save it next to the webhook:
       umask 077 && printf %s 'xoxb-...' > "$(python3 scripts/fleetconf.py | awk '/STATE_DIR/{print $2}')/bot-token"

Usage:
  scripts/fleet-post.py "leg 27 finished, 4 of 4 landed"
  scripts/fleet-post.py "leg 27 finished, 3 landed, 1 blocked" --detail "$(cat notes.md)"
  scripts/fleet-post.py "the watchdog needs re-arming before the fleet restarts" \
      --action "type /fleet-watch in a new window"
  scripts/fleet-post.py "..." --thread-ts <ts>          reply inside a thread
  scripts/fleet-post.py "..." --react crystal_ball      mark a dream post
                                                       (robot_face is automatic)
  scripts/fleet-post.py --dry-run "..."                 print, send nothing
Exit status: 0 sent · 1 send failed · 2 not configured · 3 sent by fallback,
without the thread.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse  # noqa: E402
import subprocess  # noqa: E402

import fleetslack as fs  # noqa: E402
from fleetslack import TOKEN_FILE, call, read_token  # noqa: E402


def fallback(text: str, action: str | None) -> int:
    """No bot token. Reach the owner through the webhook, or say we could not."""
    here = Path(__file__).resolve().parent
    if action is None:
        print(f"NOT CONFIGURED -- no bot token at {TOKEN_FILE}.\n"
              "Nothing was posted. See this file's header for the five-line\n"
              "setup. Until it exists, say in your log entry that the channel\n"
              "did not get this.", file=sys.stderr)
        return 2
    rc = subprocess.run(
        [sys.executable, str(here / "fleet-alert.py"), f"{text} -- {action}"]
    ).returncode
    print(f"NOT CONFIGURED -- no bot token at {TOKEN_FILE}.\n"
          "Sent through the alert webhook instead, so the owner was reached,\n"
          "but any --detail was DROPPED: a webhook cannot open a thread.\n"
          "See this file's header for the five-line setup.", file=sys.stderr)
    return 3 if rc == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("message", help="one or two plain sentences, no jargon")
    ap.add_argument("--detail", help="the technical half; posted as a thread reply")
    ap.add_argument("--action", metavar="WHAT",
                    help="what the owner must do. This is the ONLY thing that "
                         "notifies; ops.md §3 fixes the set")
    ap.add_argument("--thread-ts", metavar="TS",
                    help="reply inside this message's thread instead of posting "
                         "to the channel; --detail goes in the same thread")
    ap.add_argument("--react", metavar="EMOJI",
                    help="reaction to add to the post, e.g. crystal_ball")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be sent, send nothing")
    args = ap.parse_args()

    text = args.message.strip()
    if not text:
        print("refusing to post an empty message", file=sys.stderr)
        return 2

    # The marker is words, not an emoji: a phone's notification preview shows
    # the text and often drops the emoji, and this channel already gives
    # robot_face and crystal_ball meanings a third convention would muddle.
    if args.action:
        text = f"<@{CONF.owner}> *NEEDS YOU:* {text}\n> {args.action.strip()}"
    else:
        text = f"FYI — {text}"

    if args.dry_run:
        print(f"channel: {CONF['slack']['channel_name']} ({CONF['slack']['channel']})")
        print(f"thread : {args.thread_ts or '(top level)'}")
        print(f"post   : {text}")
        print(f"thread : {(args.detail or '(none)')[:400]}")
        print(f"react  : {args.react or '(none)'}")
        print(f"notifies: {'YES' if args.action else 'no'}")
        return 0

    token = read_token()
    if token is None:
        return fallback(args.message.strip(), args.action)

    r = call(token, "chat.postMessage", channel=CONF["slack"]["channel"],
             text=text, thread_ts=args.thread_ts)
    if not r.get("ok"):
        print(f"post failed: {fs.explain(r.get('error', ''), r)}", file=sys.stderr)
        return 1

    ts = r["ts"]
    print(f"posted {ts}")

    # A failed thread reply or reaction is reported but does not fail the run:
    # the message the owner needed is already in the channel, and returning
    # non-zero here would make a caller re-post it.
    if args.detail and args.detail.strip():
        d = call(token, "chat.postMessage", channel=CONF["slack"]["channel"],
                 thread_ts=args.thread_ts or ts, text=args.detail.strip())
        print("threaded detail" if d.get("ok")
              else f"detail failed: {fs.explain(d.get('error', ''), d)}")

    # `robot_face` goes on unconditionally, and it is not decoration. The
    # listener's STEP 1 skips any message carrying it, which is what stops the
    # fleet reading its own unit line as a fresh instruction from the owner --
    # caught on 2026-09-03, on the first real tick, before it did. Posting as
    # the app makes authorship the primary discriminator and this the second,
    # and a gate whose failure is "the fleet obeys itself" is worth two. Adding
    # it here rather than in a prompt means no caller can forget.
    for emoji in ("robot_face", args.react):
        if not emoji:
            continue
        k = call(token, "reactions.add", channel=CONF["slack"]["channel"],
                 timestamp=ts, name=emoji.lstrip(":").rstrip(":"))
        print(f"reacted {emoji}" if k.get("ok")
              else f"reaction {emoji} failed: {fs.explain(k.get('error', ''), k)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
