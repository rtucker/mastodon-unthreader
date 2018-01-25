#!/usr/bin/env python3

import mastoapi
import pathlib

# TODO: make this more OS-agnostic
CONFIG_DIR="~/.config/Mastodon/unthreader/unthreader.cfg"

def open(config_dir):
    p = pathlib.Path(config_dir).expanduser().resolve().absolute()

    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    if not mastoapi.is_configured(p):
        mastoapi.generate_config(p)

    return mastoapi.get_mastodon(p)

if __name__ == "__main__":
    # Rey's thanksgiving thread
    STATUS_ID = "99048822128213347"
    masto = open(CONFIG_DIR)

    status = masto.status(STATUS_ID)

    print("Root toot: %s %s (%s)" % (status.account.username, status.id, status.created_at))
    print("  %s" % status.content.encode('utf-8'))

    context = masto.status_context(status)

    print("Ancestors: %d" % len(context.ancestors))
    for anc in context.ancestors:
        print("Ancestor toot: %s %s (%s)" % (anc.account.username, anc.id, anc.created_at))
        print("  %s" % anc.content.encode('utf-8'))

    print("Descendants: %d" % len(context.descendants))
    for des in context.descendants:
        print("Descendant toot: %s %s (%s)" % (des.account.username, des.id, des.created_at))
        print("  %s" % des.content.encode('utf-8'))
