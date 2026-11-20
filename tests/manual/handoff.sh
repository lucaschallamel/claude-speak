#!/usr/bin/env bash
# Manual check of the server version handoff (US-030) with real Kokoro and audio. CI does not run it.
#
# Builds scratch copies of this working copy at three versions, all on one scratch data dir (so they
# share one socket), and checks server.log:
#   1. an old server mid-reply finishes it, exits, and the newer client's server speaks;
#   2. an older client keeps using the newer server (no /quit);
#   3. a server built with a 4 s DRAIN_CAP is stopped mid-reply and hands over.
# The installed plugin and its server are untouched: the scratch data dir has its own socket.
#
# Usage: tests/manual/handoff.sh   (MODELS=<dir with kokoro-v1.0.onnx> to use another model dir)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODELS="${MODELS:-$HOME/.claude/plugins/data/claude-speak-claude-speak/models}"
S="$(mktemp -d)"
D="$S/data"
export CLAUDE_SPEAK_IDLE_TIMEOUT=300
unset CLAUDE_PLUGIN_DATA CLAUDE_SPEAK_DATA
fail=0

[ -f "$MODELS/kokoro-v1.0.onnx" ] || { echo "no model in $MODELS (set MODELS=...)"; exit 2; }
mkdir -p "$D" && ln -s "$MODELS" "$D/models"
copy() {  # copy <name> <version>: this working copy, relabelled
  mkdir -p "$S/$1" && cp -r "$ROOT/scripts" "$ROOT/bin" "$ROOT/.claude-plugin" "$S/$1/"
  sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$2\"/" "$S/$1/.claude-plugin/plugin.json"
}
copy old 900.0.0
copy new 900.0.1
copy capped 900.0.2 && sed -i.bak 's/^DRAIN_CAP = .*/DRAIN_CAP = 4/' "$S/capped/scripts/server.py"
copy newest 900.0.3
cs() { local v=$1; shift; "$S/$v/bin/claude-speak" "$@" --data-dir "$D"; }
expect() {  # expect <description> <regex>: one server.log line must match
  if grep -qE "$2" "$D/server.log"; then echo "PASS  $1"; else echo "FAIL  $1"; fail=1; fi
}
LONG="This is the old voice server reading a longer reply. Every word of it should play before it steps aside, and only then does the newer version start its own server and speak."
cleanup() { pkill -f "server.py --data-dir $D"; rm -rf "$S"; }
trap cleanup EXIT

echo "1. old server mid-reply, newer client speaks (listen: the whole old reply, then the new line)"
cs old say "$LONG"; sleep 3
cs new say "Now the newer version is speaking."
expect "old server quit for a newer version" "quit for a newer version; exiting"
expect "new server listening as 900.0.1" "listening on .*; version 900.0.1"

echo "2. older client after the update"
before=$(grep -c "quitting for a newer version" "$D/server.log")
cs old say "An older client, speaking through the newer server."; sleep 4
after=$(grep -c "quitting for a newer version" "$D/server.log")
if [ "$before" = "$after" ]; then echo "PASS  newer server kept"; else echo "FAIL  newer server was asked to quit"; fail=1; fi

echo "3. drain cap (listen: a long reply cut after about 4 s)"
cs capped say "Replacing the server first."; sleep 4
cs capped say "$LONG $LONG"; sleep 1
cs newest say "The old server was cut off after four seconds."
expect "capped server stopped its speech" "still draining after 4 s; stopping speech"
expect "newest server listening as 900.0.3" "listening on .*; version 900.0.3"
cs newest status | grep -E "^version:"
sleep 5

[ -s "$D/claude-speak.log" ] && { echo "claude-speak.log:"; cat "$D/claude-speak.log"; }
[ "$fail" = 0 ] && echo "ALL PASS" || echo "SOME CHECKS FAILED (server.log kept: $D/server.log copied to /tmp/handoff-server.log)"
[ "$fail" = 0 ] || cp "$D/server.log" /tmp/handoff-server.log
exit "$fail"
