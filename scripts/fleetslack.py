#!/usr/bin/env python3
"""Slack, as the fleet's own identity. One transport, one gate, no connector.

Every Slack call the fleet makes goes through here, over the **bot token** in
`{state_dir}/bot-token`. Until 2026-09-10 only the *posting* half did:
`fleet-post.py` had the token, while every *read* -- the listener's STEP 1, a
leg's stop poll, the announcement window's thread check -- went through the
Slack MCP connector, which authenticates **as the owner**. That split was the
last thing in the fleet standing on the owner's personal OAuth, and it cost the
listener its eyes the moment that connector dropped: a window armed with a
heartbeat that could post but not read is a dispatcher that cannot be given an
instruction, and it looks entirely healthy.

**The read is what makes the gate honest, and that is the real reason to move.**
The connector handed back rendered prose. The API hands back the message object,
and the message object carries `subtype` -- which is the field that says whether
a human wrote this or Slack did. The old gate could only ask the four questions
prose can answer (author, reactions, an app-attribution suffix, "is not a
channel-join event"), and on 2026-09-10, minutes after the bot was granted
`groups:history`, the very first read turned up this:

    subtype: bot_add    user: U0AGQGSHM2P    reactions: none
    "added an integration to this channel: EmbArch Fleet"

Authored by the owner, unreacted, no attribution suffix, and not a
`channel_join` -- so it passed all four tests and would have been claimed with
`eyes` and acted on. It was Slack narrating the owner's own reinstall.

**So the gate allowlists the human forms rather than denying the event ones**,
which is the only direction that closes. A plain human message has no `subtype`
at all; a handful of subtypes are still human (`file_share` above all -- the
owner dropping a log or a photo is a real inbox route, and the whole reason
`files:read` was granted); everything else is Slack narrating something, and
that set is open-ended, so enumerating it would go stale on Slack's schedule
rather than ours.

Read `{fleet_repo}/slack.md` for the control-plane design this serves.

Not a CLI. `fleet-read.py`, `fleet-react.py`, `fleet-post.py` and
`fleet-slack-doctor.py` are the four entry points.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

TOKEN_FILE = CONF.state_dir / "bot-token"
API = "https://slack.com/api/"
TIMEOUT = 10

# The scopes the fleet's own paths need, and what stops working without each.
# `fleet-slack-doctor.py` reports against this; it is the only list anywhere of
# what the app is installed for, since Slack will not tell you what a token
# *should* have -- only what it has.
NEEDED_SCOPES = {
    "chat:write":      "post at all (fleet-post.py)",
    "reactions:write": "claim a message: eyes / white_check_mark / x",
    "reactions:read":  "read the watermark back",
    "groups:history":  "read the private channel and its threads",
    "groups:read":     "confirm the bot is actually in the channel",
    "files:read":      "read a log or photo the owner drops in",
    "files:write":     "attach a CSV or report instead of pasting it",
}

# Reactions that mean "this message is already spoken for". `robot_face` is the
# fleet's own mark, added by fleet-post.py to everything it sends; the other
# three are the listener's watermark. See slack.md.
CLAIM_REACTIONS = ("eyes", "white_check_mark", "x", "robot_face")

# Subtypes a *person* produces. Everything not here -- and `subtype` absent is
# the common case, a plain message -- is Slack narrating an event.
#   file_share       the owner dropped a file, with or without a comment
#   thread_broadcast a thread reply he also sent to the channel
#   me_message       /me
HUMAN_SUBTYPES = frozenset({"file_share", "thread_broadcast", "me_message"})

# Slack's own error strings, in the terms of the thing the reader has to go fix.
_HINTS = {
    "invalid_auth":      f"the token in {TOKEN_FILE} is not valid. A reinstall can "
                         f"rotate it -- re-save it (umask 077).",
    "account_inactive":  "the app was uninstalled from the workspace.",
    "not_in_channel":    "the app was never invited to the channel -- "
                         "`/invite @<app>` in it.",
    "channel_not_found": "for a PRIVATE channel this is usually the same thing as "
                         "not_in_channel, or `groups:history` is missing.",
    "missing_scope":     "the bot token lacks a scope; the response says which. "
                         "Add it at api.slack.com/apps -> OAuth & Permissions, "
                         "then Reinstall.",
    "is_archived":       "the channel is archived.",
    "msg_too_long":      "Slack's per-message limit; put the bulk in --detail.",
    "ratelimited":       "back off and let the next tick retry; do not loop.",
    "already_reacted":   "that reaction is already there -- which for a claim "
                         "means somebody claimed it first.",
    "no_reaction":       "there was no such reaction to remove.",
}


def explain(err: str, resp: dict | None = None) -> str:
    """Slack's error, plus what to actually do about it."""
    hint = _HINTS.get(err, "")
    if err == "missing_scope" and resp and resp.get("needed"):
        hint = f"needs one of: {resp['needed']}. " + hint
    return f"Slack said {err!r}" + (f" -- {hint}" if hint else "")


def read_token() -> str | None:
    """The bot token, or None. A file that is not a bot token is not a token."""
    try:
        tok = TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    # `xoxb-` is the bot prefix. A user token (`xoxp-`) would act as the owner,
    # which is the exact coupling this module exists to remove, so it is refused
    # here rather than silently reintroducing it.
    return tok if tok.startswith("xoxb-") else None


def _open(req) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode(errors="replace"))
    except urllib.error.HTTPError as e:          # Slack answers 200 for API
        body = e.read().decode(errors="replace")  # errors, so this is transport
        return {"ok": False, "error": f"http_{e.code}", "body": body[:200]}
    except Exception as e:
        return {"ok": False, "error": f"transport: {e}"}


def call(token: str, method: str, **payload) -> dict:
    """POST a write method."""
    return _open(urllib.request.Request(
        API + method, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Authorization": f"Bearer {token}"}))


def get(token: str, method: str, **params) -> dict:
    """GET a read method. Slack wants reads as query strings, not JSON."""
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return _open(urllib.request.Request(
        API + method + ("?" + q if q else ""),
        headers={"Authorization": f"Bearer {token}"}))


def scopes_of(token: str) -> tuple[list[str], dict]:
    """What the token actually carries, from the response header Slack sets.

    There is no API method for this -- `auth.test` says who you are, never what
    you may do -- so the header on any successful call is the only source.
    """
    req = urllib.request.Request(API + "auth.test",
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.headers.get("x-oauth-scopes", "")
            body = json.loads(r.read().decode(errors="replace"))
        return [s.strip() for s in raw.split(",") if s.strip()], body
    except Exception as e:
        return [], {"ok": False, "error": f"transport: {e}"}


def reactions_of(msg: dict) -> list[str]:
    return [r.get("name", "") for r in msg.get("reactions", []) or []]


def classify(msg: dict, owner: str | None = None) -> tuple[bool, str]:
    """Is this message an instruction to the fleet? Returns (actionable, why).

    The five tests, in the order that fails cheapest. `why` is written to be
    printed next to a skipped message, because a gate whose refusals are
    invisible is one nobody can debug -- the five hours of 2026-09-03 were spent
    believing a queue was empty.
    """
    owner = owner or CONF.owner

    sub = msg.get("subtype")
    if sub is not None and sub not in HUMAN_SUBTYPES:
        return False, f"event, not a message (subtype={sub})"

    # The fleet posts as the app, so its own output is not authored by the owner
    # at all. `bot_id` is the second, independent kill: `bot_add` carries the
    # owner as `user` AND a `bot_id`, and either test alone stops it.
    if msg.get("bot_id"):
        return False, "written by an app, not a person"
    if msg.get("user") != owner:
        return False, f"not from the owner (user={msg.get('user')})"

    hit = [r for r in reactions_of(msg) if r in CLAIM_REACTIONS]
    if hit:
        return False, f"already marked: {', '.join(hit)}"

    # A message the owner sent *through* a Claude app carries an attribution
    # suffix; that is the fleet's own words coming back around.
    if msg.get("text", "").rstrip().endswith("Claude") and "Sent using" in msg.get("text", ""):
        return False, "app attribution suffix -- the fleet's own output"

    return True, "actionable"
