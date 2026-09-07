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

**Delegating also means one voice without having to prove they are one app.**
The webhook and the bot token are separate credentials, and no local check can
say whether they belong to the same Slack app -- a webhook URL carries a
per-integration id, not an app id. Preferring the token sidesteps the question
entirely: whatever the webhook is, it is not what speaks in normal operation.
`--check-config` reports what is configured and usable, and explicitly declines
to guess the rest.

**This is for conditions where the fleet is stuck or waiting on the owner**, not
for progress. `ops.md` §3 fixes the set; adding to it is
how a notification channel becomes a feed nobody reads.

**A `PermissionRequest` hook also fires this**, and that case is worth stating
because it cannot be handled any other way: an agent blocked on a permission
prompt is *suspended*, so it cannot alert for itself, and a leg runs unattended
where a prompt stops it until the owner happens to look. Two shell shapes can
never be allowlisted -- a `for ... done` loop, which has no prefix to match, and
a heredoc or `>` file write, judged as a write whatever it starts with -- so
`leg.md` forbids both. The hook is the backstop for when one slips
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


def check_config(webhook: str) -> int:
    """Report both credentials, and refuse to guess which app owns the webhook.

    **This used to claim it could tell.** It compared the `B...` segment of the
    webhook URL against `auth.test`'s `bot_id` and called a mismatch "two apps".
    Those are different namespaces and never match, so it reported two apps
    every time, including for one app -- which is what it did on 2026-09-06,
    against a single app that had a bot token and a webhook. The proof was
    already in the channel: the join notice for the SAME app linked
    `/services/B0C020VTXU1` while its bot user was `B0BUXFK302V`.

    A webhook URL carries a per-integration id, not an app id, and re-installing
    an app mints a new one. Nothing in the URL identifies the owner. The only
    places that do are the app's own page on api.slack.com and the author shown
    on a message it posts, and neither is reachable from here.
    """
    tok = bot_token()
    if tok is None:
        print("bot token : NOT CONFIGURED -- see scripts/fleet-post.py's header.\n"
              "            Every post falls back to the webhook, without a thread.")
    else:
        req = urllib.request.Request(
            "https://slack.com/api/auth.test", data=b"{}",
            headers={"Authorization": f"Bearer {tok}",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                info = json.loads(r.read().decode(errors="replace"))
        except Exception as e:
            print(f"bot token : present but unusable ({e})")
            return 1
        if not info.get("ok"):
            print(f"bot token : REJECTED by Slack ({info.get('error')!r}) -- "
                  "revoked, or the app was reinstalled and the token rotated.")
            return 1
        print(f"bot token : ok, posts as @{info.get('user')} "
              f"in team {info.get('team_id')}")

    url = read_url(webhook)
    if url is None:
        print("webhook   : not configured. Fine while the token works -- it is "
              "only the fallback.")
    else:
        print("webhook   : present and well-formed (fallback only)")

    print("\nWhich app owns the webhook cannot be answered from here, and a\n"
          "script that guesses is worse than one that says so. Open\n"
          "api.slack.com/apps and look at the app's Incoming Webhooks page.")
    return 0 if (tok or url) else 2


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
    ap.add_argument("--check-config", action="store_true",
                    help="report which credentials are configured and usable, "
                         "and stop")
    args = ap.parse_args()

    if args.check_config:
        return check_config(args.webhook)

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
