#!/usr/bin/env python3
"""Check the fleet's whole Slack path, end to end, and post nothing doing it.

Every Slack credential the fleet holds fails *silently and healthily*. That is
the reason this exists, and it is not a general worry -- each of the six checks
below is a failure this fleet has already had:

  - On 2026-09-10 the fleet moved every Slack read off the MCP connector, which
    authenticated **as the owner**, onto its own bot token (`fleetslack.py` has
    the why). The connector's death mode was the template for all of them: a
    listener window that could still post its heartbeat but could no longer
    read the channel looked completely healthy and could not be given an
    instruction.
  - A token file that holds a **user** token (`xoxp-`) instead of a bot token
    works -- and reintroduces exactly the owner-identity coupling the move
    removed. `fleetslack.read_token()` refuses it; check 1 says so out loud
    rather than reporting "no token".
  - A scope granted late is a capability that was missing all along.
    `groups:history` was granted only on 2026-09-10, and the very first read it
    allowed turned up a `subtype=bot_add` event that the old prose gate would
    have claimed and acted on. Slack will not tell you what a token *should*
    carry, so `fleetslack.NEEDED_SCOPES` is the only list of that anywhere and
    check 3 is the only thing that reads it.
  - A reinstall rotates the incoming webhook URL. The old URL keeps answering,
    with `no_service`, and `fleet-alert.py` swallows its own failures by
    design -- so the watchdog goes on looking healthy while paging nobody.

Checks run cheapest-and-most-fundamental first, and a check whose prerequisite
FAILed is reported SKIP rather than run: a scope report against a token Slack
has already rejected is noise dressed as a second problem.

**It is read-only, deliberately and completely.** No message is posted, no
reaction added or removed. The webhook is the only thing here that could
possibly emit, and it is probed with an empty JSON body for that reason --
see `check_webhook`.

Usage:
  scripts/fleet-slack-doctor.py
  scripts/fleet-slack-doctor.py --json      the same verdicts, for a script
Exit status: 0 nothing FAILed (WARNs and INCONCLUSIVEs allowed) · 1 at least
one check FAILed · 2 there is no bot token at all, so almost nothing could be
checked.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleetslack as fs  # noqa: E402
from fleetconf import CONF  # noqa: E402

TIMEOUT = 10
WEBHOOK_FILE = CONF.state_dir / "alert-webhook"

# Scopes the fleet was offered and turned down, with what accepting one would
# have bought. Slack's install screen suggests these next to the ones actually
# needed, so an app reinstalled by hand can pick them up without anyone
# deciding to -- and a scope nobody chose is a capability nobody is watching.
DECLINED_SCOPES = {
    "groups:write":         "create, rename and archive private channels. The "
                            "fleet reads one channel and posts to it.",
    "users:read":           "the workspace's whole member directory. The fleet "
                            "needs exactly one user id and has it from fleet.toml.",
    "chat:write.customize": "post under an arbitrary display name and icon -- "
                            "the opposite of the point, which is that a fleet "
                            "post is unmistakably not the owner's.",
}

# Extra scopes that are expected here, so they are not reported as surprises.
# `incoming-webhook` is not a capability the API paths use at all -- it is what
# Slack adds when the owner configures the alert webhook `fleet-alert.py` falls
# back to, so its absence would be the interesting direction, not its presence.
KNOWN_EXTRA_SCOPES = {
    "incoming-webhook": "Slack's own marker for the alert webhook "
                        "(fleet-alert.py's fallback) -- expected",
}

# What makes an extra scope worth a WARN rather than a note. Reads the fleet
# does not use cost it nothing; a write it does not use is standing authority
# to change the workspace, held by an unattended process.
_WRITEISH = ("write", "manage", "admin", "delete", "remove")

OK, WARN, FAIL, SKIP, INCONCL = "OK", "WARN", "FAIL", "SKIP", "INCONCLUSIVE"


class Report:
    """The verdicts, in order, plus the worst one seen."""

    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, name: str, status: str, detail: str,
            fix: str | None = None, **extra) -> str:
        self.checks.append({"n": len(self.checks) + 1, "check": name,
                            "status": status, "detail": detail, "fix": fix,
                            **extra})
        return status

    @property
    def failed(self) -> bool:
        return any(c["status"] == FAIL for c in self.checks)


# --- 1. the token file ------------------------------------------------------

def check_token(rep: Report) -> str | None:
    """Is there a bot token, and is it a *bot* token? Returns it, or None.

    `fleetslack.read_token()` answers None for both "no file" and "a file that
    is not an xoxb- token", which is right for a caller that only wants to use
    it and wrong for a doctor: those are different things to go fix, and the
    second one is the specific bug the 2026-09-10 move exists to remove. So the
    file is also read raw here, purely to tell them apart.
    """
    token = fs.read_token()
    if token:
        rep.add("token", OK,
                f"{len(token)}-char xoxb- token in {fs.TOKEN_FILE}")
        return token

    try:
        raw = fs.TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        rep.add("token", FAIL, f"no token file at {fs.TOKEN_FILE}",
                "Create the app's bot token and save it: see fleet-post.py's "
                "header, step 5 (`umask 077` first -- it is a secret).",
                missing=True)
        return None

    if raw.startswith("xoxp-"):
        rep.add("token", FAIL,
                f"{fs.TOKEN_FILE} holds a USER token (xoxp-), not a bot token",
                "A user token acts AS THE OWNER, which is the coupling this "
                "whole path was built to remove -- every post would be authored "
                "by him and would notify nobody. Take the Bot User OAuth Token "
                "from OAuth & Permissions (it starts xoxb-) and replace it.")
    else:
        head = (raw[:12] + "...") if raw else "(empty)"
        rep.add("token", FAIL,
                f"{fs.TOKEN_FILE} does not hold a Slack token ({head})",
                "Expected a Bot User OAuth Token starting `xoxb-`. A stray "
                "newline is fine; anything else means the wrong string was "
                "saved.")
    return None


# --- 2. who Slack says we are -----------------------------------------------

def check_identity(rep: Report, token: str) -> tuple[list[str], bool]:
    """`auth.test`, and the scope header that rides along with it.

    One call serves this check and the next: `scopes_of` reads
    `x-oauth-scopes` off the response, which is the only place Slack ever
    states what a token carries.
    """
    granted, body = fs.scopes_of(token)
    if not body.get("ok"):
        err = body.get("error", "unknown")
        rep.add("identity", FAIL, f"Slack rejected the token: {fs.explain(err, body)}",
                "Reinstalling the app rotates the token. Copy the current Bot "
                f"User OAuth Token and re-save it to {fs.TOKEN_FILE}.")
        return granted, False

    rep.add("identity", OK,
            f"@{body.get('user')} ({body.get('user_id')}) "
            f"in team {body.get('team')} ({body.get('team_id')})",
            bot_id=body.get("bot_id"), team=body.get("team"),
            user=body.get("user"), user_id=body.get("user_id"))
    return granted, True


# --- 3. scopes --------------------------------------------------------------

def check_scopes(rep: Report, granted: list[str]) -> None:
    """Granted against NEEDED_SCOPES, both directions.

    One check rather than three, so the report stays six lines long: a missing
    scope FAILs it, an extra *write* scope WARNs it, and extra reads are a note
    in the same detail. Slack has no method that says what a token should
    carry, so `fleetslack.NEEDED_SCOPES` is the whole specification.
    """
    have = set(granted)
    missing = [s for s in fs.NEEDED_SCOPES if s not in have]
    extra = sorted(have - set(fs.NEEDED_SCOPES))

    # An extra read is a note. An extra write is standing authority to change
    # the workspace, held by a process that runs unattended for hours.
    writeish = [s for s in extra
                if s not in KNOWN_EXTRA_SCOPES
                and (s in DECLINED_SCOPES or any(w in s for w in _WRITEISH))]
    readish = [s for s in extra if s not in writeish]

    notes = []
    for s in readish:
        why = KNOWN_EXTRA_SCOPES.get(s)
        notes.append(f"{s}" + (f" ({why})" if why else " (granted, unused)"))
    for s in writeish:
        why = DECLINED_SCOPES.get(s)
        notes.append(f"{s} -- " + (f"DELIBERATELY DECLINED: {why}" if why
                                   else "grants writes the fleet never makes"))
    tail = ("\n" + "\n".join(f"    extra: {n}" for n in notes)) if notes else ""

    if missing:
        lost = "; ".join(f"{s} -> cannot {fs.NEEDED_SCOPES[s]}" for s in missing)
        rep.add("scopes", FAIL,
                f"{len(missing)} of {len(fs.NEEDED_SCOPES)} needed scopes "
                f"missing: {lost}{tail}",
                "api.slack.com/apps -> your fleet app -> OAuth & Permissions -> "
                "Bot Token Scopes, add them, then **Reinstall to Workspace** "
                "(adding a scope does nothing until the reinstall) and re-save "
                "the rotated token.",
                missing=missing, granted=sorted(have),
                extra=readish, extra_write=writeish)
        return

    summary = (f"all {len(fs.NEEDED_SCOPES)} needed scopes present"
               + (f"; {len(extra)} extra" if extra else "; none extra"))
    if writeish:
        rep.add("scopes", WARN, summary + tail,
                "Nothing in this repo calls the write scopes listed above. "
                "Remove them at OAuth & Permissions unless the owner added them "
                "on purpose -- an unattended fleet holding write authority it "
                "never exercises is authority nobody is watching.",
                missing=[], granted=sorted(have),
                extra=readish, extra_write=writeish)
    else:
        rep.add("scopes", OK, summary + tail,
                missing=[], granted=sorted(have),
                extra=readish, extra_write=[])


# --- 4. the channel ---------------------------------------------------------

def check_channel(rep: Report, token: str) -> bool:
    chan = CONF.channel
    name = CONF["slack"]["channel_name"]
    r = fs.get(token, "conversations.info", channel=chan)
    if not r.get("ok"):
        err = r.get("error", "unknown")
        rep.add("channel", FAIL,
                f"{name} ({chan}) did not resolve: {fs.explain(err, r)}",
                f"For a PRIVATE channel this is nearly always the app never "
                f"having been invited: type `/invite @<app name>` in {name}. "
                f"If it was invited, check `groups:read` in the scopes above, "
                f"and that fleet.toml's channel id is still the right one.",
                channel=chan)
        return False

    c = r.get("channel", {})
    private, member, archived = (bool(c.get("is_private")),
                                 bool(c.get("is_member")),
                                 bool(c.get("is_archived")))
    shape = ("private" if private else "PUBLIC") + \
            (", archived" if archived else "")
    if archived:
        rep.add("channel", FAIL, f"#{c.get('name')} ({chan}) is archived",
                "Unarchive it in Slack; nothing can be posted to an archived "
                "channel.", channel=chan, is_private=private, is_member=member)
        return False
    if not member:
        rep.add("channel", FAIL,
                f"#{c.get('name')} ({chan}) resolves ({shape}) but the bot is "
                f"NOT a member",
                f"`/invite @<app name>` in {name}. Reading may still work while "
                f"posting fails, which is the half-broken state that looks fine.",
                channel=chan, is_private=private, is_member=False)
        return False

    rep.add("channel", OK,
            f"#{c.get('name')} ({chan}), {shape}, bot is a member",
            channel=chan, is_private=private, is_member=True)
    return True


# --- 5. the read path -------------------------------------------------------

def check_read(rep: Report, token: str) -> None:
    """One message, and whether its reactions came back with it.

    The gate reads reactions straight off the history payload
    (`fleetslack.reactions_of`) rather than calling `reactions.get` per
    message. If Slack ever stopped inlining them the claim watermark would read
    as absent on every message -- every message would look unclaimed, and the
    listener would act on things it had already handled. So the check is not
    "did the read work" but "did the read carry the field the gate depends on".
    """
    # A page rather than one message: the newest message is often unreacted --
    # a `bot_add`, or a line nobody has marked yet -- and one unreacted message
    # is indistinguishable from a Slack that stopped inlining the field. Twenty
    # is what the listener itself reads, so this checks the payload the gate
    # actually sees.
    r = fs.get(token, "conversations.history", channel=CONF.channel, limit=20)
    if not r.get("ok"):
        rep.add("read", FAIL,
                f"conversations.history failed: {fs.explain(r.get('error',''), r)}",
                "The listener has no eyes until this works: it can post its "
                "heartbeat and still not be given an instruction. Check "
                "`groups:history` above.")
        return

    msgs = r.get("messages", [])
    if not msgs:
        rep.add("read", INCONCL,
                "history ok, but the channel is empty -- nothing to check the "
                "inline-reactions path against",
                "Post anything in the channel and re-run; until then the gate's "
                "dependency on inline reactions is untested here.")
        return

    hit = next(((m, fs.reactions_of(m)) for m in msgs if fs.reactions_of(m)),
               None)
    m, names = hit if hit else (msgs[0], [])
    where = f"ts={m.get('ts')}"
    if names:
        rep.add("read", OK,
                f"history ok ({len(msgs)} msgs); reactions come back inline "
                f"({where} carries {', '.join(names)})", reactions=names)
    else:
        # Absence is not evidence either way: an unreacted message and a Slack
        # that stopped inlining reactions look identical from here. Saying OK
        # would be claiming proof this call cannot produce.
        rep.add("read", INCONCL,
                f"history ok, but {where} has no reactions at all, so whether "
                f"they come back inline is untested",
                "Re-run after the fleet has marked something (fleet-post.py "
                "puts robot_face on its own posts), or check a message you know "
                "carries a reaction with `fleet-read.py --json`.",
                reactions=[])


# --- 6. the webhook ---------------------------------------------------------

def check_webhook(rep: Report) -> None:
    """Is the alert webhook still live? Probed with an empty body, on purpose.

    An incoming webhook has no status endpoint and no dry run, so the only way
    to know a URL is still wired to a channel is to send it something. **An
    empty JSON object is the one payload that answers the question without
    emitting anything**: a live webhook parses it, finds no `text`, and replies
    HTTP 400 `invalid_payload` -- having posted nothing, because there was
    nothing to post. A dead or rotated URL never gets that far and answers 404
    `no_service` (or 403), which is the failure worth catching: the old URL goes
    on answering after a reinstall, `fleet-alert.py` swallows its own send
    failures by design, and the watchdog looks healthy while paging nobody.

    Anything with a `text` field would be a real message in the channel. This
    check must never write one -- it runs on demand, often while somebody is
    debugging, and an alarm that cries wolf when tested is an alarm that gets
    muted.
    """
    try:
        url = WEBHOOK_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        rep.add("webhook", WARN, f"no webhook at {WEBHOOK_FILE}",
                "Fine while the bot token works -- fleet-alert.py prefers the "
                "token and the webhook is only the fallback. See "
                "fleet-alert.py's header to add one.")
        return

    if not url.startswith("https://hooks.slack.com/"):
        rep.add("webhook", FAIL,
                f"{WEBHOOK_FILE} does not hold a Slack webhook URL",
                "fleet-alert.py requires an https://hooks.slack.com/... URL and "
                "treats anything else as not configured, so alerts fall through "
                "silently. Re-save it from the app's Incoming Webhooks page.")
        return

    req = urllib.request.Request(
        url, data=b"{}", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode(errors="replace").strip()
        # Not expected: an empty payload should be rejected. Reported rather
        # than explained away, because the one thing it might mean is that this
        # probe put something in the channel.
        rep.add("webhook", WARN,
                f"live, but HTTP {r.status} {body[:60]!r} to an empty payload "
                f"(expected 400 invalid_payload)",
                "Check the channel: if this probe posted anything, Slack's "
                "webhook behaviour has changed and this check needs revisiting.")
        return
    except urllib.error.HTTPError as e:
        code, body = e.code, e.read().decode(errors="replace").strip()
    except Exception as e:
        rep.add("webhook", WARN, f"could not be reached ({e})",
                "A transport failure says nothing about the URL. Re-run; if it "
                "persists, the alert path is unverified.")
        return

    if code == 400 and "invalid_payload" in body:
        rep.add("webhook", OK,
                "live -- 400 invalid_payload to an empty body, nothing posted",
                code=code, body=body[:60])
    elif code in (403, 404, 410) or "no_service" in body or "no_team" in body:
        rep.add("webhook", FAIL,
                f"dead or rotated -- HTTP {code} {body[:60]!r}",
                "A reinstall mints a new webhook URL and the old one keeps "
                "answering like this. Take the current URL from the app's "
                f"Incoming Webhooks page and re-save it:\n      umask 077 && "
                f"printf %s '<url>' > {WEBHOOK_FILE}",
                code=code, body=body[:60])
    else:
        rep.add("webhook", WARN,
                f"unexpected answer to an empty body: HTTP {code} {body[:60]!r}",
                "Neither the live nor the dead signature. Compare against the "
                "app's Incoming Webhooks page by hand.",
                code=code, body=body[:60])


# --- driver -----------------------------------------------------------------

def run(rep: Report) -> int:
    token = check_token(rep)
    no_token = bool(rep.checks[0].get("missing"))

    if token is None:
        for name in ("identity", "scopes", "channel", "read"):
            rep.add(name, SKIP, "no usable bot token")
    else:
        granted, valid = check_identity(rep, token)
        if not valid:
            for name in ("scopes", "channel", "read"):
                rep.add(name, SKIP, "Slack rejected the token")
        else:
            check_scopes(rep, granted)
            if check_channel(rep, token):
                check_read(rep, token)
            else:
                rep.add("read", SKIP, "the channel did not resolve")

    # The webhook is a separate credential, so it is worth checking even with
    # no bot token at all -- that is exactly when it is the only way the owner
    # gets reached.
    check_webhook(rep)

    if no_token:
        return 2
    return 1 if rep.failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine output")
    args = ap.parse_args()

    rep = Report()
    code = run(rep)

    if args.json:
        print(json.dumps({"channel": CONF.channel,
                          "channel_name": CONF["slack"]["channel_name"],
                          "token_file": str(fs.TOKEN_FILE),
                          "webhook_file": str(WEBHOOK_FILE),
                          "checks": rep.checks,
                          "exit": code}, indent=2))
        return code

    print(f"Slack path for {CONF['slack']['channel_name']} ({CONF.channel}) "
          f"— {len(rep.checks)} checks, nothing posted")
    for c in rep.checks:
        print(f"\n{c['n']} {c['check']:<18} {c['status']:<12} {c['detail']}")
        if c["fix"]:
            print(f"    fix: {c['fix']}")

    tally = {}
    for c in rep.checks:
        tally[c["status"]] = tally.get(c["status"], 0) + 1
    print("\n" + ", ".join(f"{n} {s}" for s, n in tally.items()))
    if code == 2:
        print("Nothing could be checked -- there is no bot token. "
              "The fleet is deaf and mute on Slack.")
    elif code == 1:
        print("At least one check FAILed; the fix line under it says where to go.")
    return code


if __name__ == "__main__":
    sys.exit(main())
