#!/usr/bin/env python3
"""Post a blocking-condition alert to #embarch-fleet that actually notifies.

Why this exists: the Slack connector authenticates AS the owner, so every
message the fleet posts is authored by the owner. Slack does not notify you
about your own messages, and a `<@owner>` inside one badges nothing. That
is not a settings problem and no reaction, keyword or `@channel` fixes it --
Slack will only notify the owner about a message somebody else sent.

So alerts go through the app's own identity rather than the owner's. The
mention then behaves normally: phone notification, no Remote Control, no Claude
app.

**Since 2026-09-06 that identity is the bot token, and this file is the
fallback.** `fleet-post.py` posts with `chat.postMessage`, which an incoming
webhook cannot replace: a webhook replies `ok` and never returns the message's
`ts`, so it can never open the thread that carries the technical half. When a
bot token exists this script hands the alert to `fleet-post.py` and the fleet
speaks with ONE voice; the webhook is only used when it does not.

**Two apps is the failure this arrangement is guarding against.** The webhook
and the bot token are separate credentials and nothing makes them the same app
-- on the day the token landed they were not, and the channel had a named bot
posting units and an unnamed one posting alerts. Delegating here means the
mismatch stops being visible in normal operation, and `--verify-identity` says
whether it is still there.

**This is for conditions where the fleet is stuck or waiting on the owner**, not
for progress. `ops.md` §3 fixes the set; adding to it is
how a notification channel becomes a feed nobody reads.

**A `PermissionRequest` hook also fires this**, and that case is worth stating
because it cannot be handled any other way: an agent blocked on a permission
prompt is *suspended*, so it cannot alert for itself, and a leg runs unattended
where a prompt stops it until the owner happens to look. Two shell shapes can
never be allowlisted -- a `for ... done` loop, which has no prefix to match, and
a heredoc or `>` file write, judged as a write whatever it starts with -- so
`supervise.md` forbids both. The hook is the backstop for when one slips
through anyway. It is async and swallows its own failure: a hook that blocks the
tool call it was reporting on would be worse than the prompt.

The webhook URL is a secret, so it lives OUTSIDE every repo, next to the pump
latch in `embarch/.fleet/`. Absent, this script says so and exits 2 rather than
failing silently -- a muted alarm that looks fine is worse than no alarm.

Setup (the owner's, once):
  1. api.slack.com/apps -> Create New App -> From scratch -> pick the workspace
  2. Incoming Webhooks -> On -> Add New Webhook to Workspace -> #embarch-fleet
  3. Save the URL:
       umask 077 && printf %s '<url>' > "$(python3 scripts/fleetconf.py | awk '/STATE_DIR/{print $2}')/alert-webhook"

Usage:
  scripts/fleet-alert.py "leg stopped: budget HOLD, 5-hour at 91%"
  scripts/fleet-alert.py --dry-run "..."      print the payload, send nothing
  scripts/fleet-alert.py --no-mention "..."   post without the @, so it does not notify
Exit status: 0 sent, 1 send failed, 2 not configured.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

WEBHOOK = str(CONF.state_dir / "alert-webhook")
OWNER = CONF.owner
TIMEOUT = 10


def read_url(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as f:
            url = f.read().strip()
    except OSError:
        return None
    return url if url.startswith("https://hooks.slack.com/") else None


def bot_token() -> str | None:
    """The bot token `fleet-post.py` uses, if the owner has configured one."""
    try:
        tok = (CONF.state_dir / "bot-token").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return tok if tok.startswith("xoxb-") else None


def delegate(text: str, no_mention: bool) -> int | None:
    """Hand this alert to fleet-post.py. None means there is no token to use.

    `--no-mention` maps to an ordinary FYI post, and a mention maps to
    `--action`, because those are the same distinction under two names: the
    thing that badges the owner's phone.
    """
    if bot_token() is None:
        return None
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "fleet-post.py"), text]
    if not no_mention:
        cmd += ["--action", "look at the listener window"]
    return subprocess.run(cmd).returncode


def verify_identity(webhook: str) -> int:
    """Say whether the webhook and the bot token are the same Slack app.

    They are separate credentials created in separate places, so nothing keeps
    them together. When they drift the channel gets two bots and the owner has
    to work out which is which -- observed 2026-09-06.
    """
    import re
    tok = bot_token()
    if tok is None:
        print("no bot token; nothing to compare against")
        return 2
    req = urllib.request.Request(
        "https://slack.com/api/auth.test", data=b"{}",
        headers={"Authorization": f"Bearer {tok}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        info = json.loads(r.read().decode(errors="replace"))
    print(f"bot token : team {info.get('team_id')} bot {info.get('bot_id')} "
          f"as @{info.get('user')}")
    url = read_url(webhook)
    if url is None:
        print("webhook   : not configured (fine -- the token is the primary path)")
        return 0
    m = re.match(r"https://hooks\.slack\.com/services/(T[A-Z0-9]+)/(B[A-Z0-9]+)/", url)
    if not m:
        print("webhook   : unrecognised URL shape")
        return 1
    print(f"webhook   : team {m.group(1)} bot {m.group(2)}")
    if m.group(2) == info.get("bot_id"):
        print("\nSAME APP. The fleet has one identity.")
        return 0
    print("\nDIFFERENT APPS. The webhook belongs to an app the bot token does not.\n"
          "Nothing is broken -- the token is preferred and the webhook is only a\n"
          "fallback -- but if that old app is still installed it can still post,\n"
          "and a second unnamed bot in the channel is exactly what this avoids.\n"
          "Either delete the old app, or replace the webhook with one created on\n"
          "the same app as the token.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("message", nargs="?", default="",
                    help="one line, what is blocked and why")
    ap.add_argument("--no-mention", action="store_true",
                    help="omit the owner mention, so the post does not notify")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the payload and the target, send nothing")
    ap.add_argument("--webhook", default=WEBHOOK)
    ap.add_argument("--verify-identity", action="store_true",
                    help="say whether the webhook and the bot token are the "
                         "same Slack app, and stop")
    args = ap.parse_args()

    if args.verify_identity:
        return verify_identity(args.webhook)

    text = args.message.strip()
    if not text:
        print("refusing to send an empty alert", file=sys.stderr)
        return 2

    # One voice when we can have one. The webhook is a different credential from
    # the bot token and may belong to a different app entirely, so preferring
    # the token is also what stops the channel growing a second bot identity.
    if not args.dry_run:
        delegated = delegate(text, no_mention=args.no_mention)
        if delegated is not None:
            return delegated

    if not args.no_mention:
        text = f"<@{OWNER}> {text}"

    payload = {"text": text}

    if args.dry_run:
        print(f"target : {args.webhook}")
        print(f"payload: {json.dumps(payload)}")
        return 0

    url = read_url(args.webhook)
    if url is None:
        print(f"NOT CONFIGURED -- no usable webhook at {args.webhook}.\n"
              "Alerts cannot notify the owner until it exists; see this file's\n"
              "header for the four-line setup. Post to the channel the ordinary\n"
              "way as well, and say in your log entry that the alert did not send.",
              file=sys.stderr)
        return 2

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode(errors="replace").strip()
    except urllib.error.HTTPError as e:
        print(f"send failed: HTTP {e.code} {e.read().decode(errors='replace')[:200]}",
              file=sys.stderr)
        return 1
    except Exception as e:
        print(f"send failed: {e}", file=sys.stderr)
        return 1

    if body != "ok":
        print(f"send failed: Slack replied {body[:200]!r}", file=sys.stderr)
        return 1
    print("alert sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
