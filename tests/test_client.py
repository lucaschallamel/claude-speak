"""Tests for the stdlib-only client, scripts/claude_speak.py.

Run: python3 -m unittest discover tests
"""

import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT / "scripts"))

import claude_speak as cs  # noqa: E402

# Settings come from the environment too; keep the developer's own out of the tests.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_OPTION_")}


class TempDataTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.data = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


def lines(text: str) -> list[str]:
    """Spoken lines without edge spaces, which TTS ignores."""
    return [line.strip() for line in text.splitlines()]


class SpeakableTest(unittest.TestCase):
    def test_code_block_is_replaced(self):
        self.assertEqual(lines(cs.speakable("Run this:\n```py\nprint(1)\n```\nDone.")),
                         ["Run this:", "(code block)", "Done."])

    def test_unclosed_code_block_is_replaced(self):
        self.assertEqual(lines(cs.speakable("Here:\n```\nx = 1")), ["Here:", "(code block)"])

    def test_inline_code_keeps_identifier(self):
        self.assertEqual(cs.speakable("Call `load_settings` now."), "Call load_settings now.")

    def test_links_and_urls(self):
        self.assertEqual(cs.speakable("See [the docs](https://x.io) or https://y.io/z."),
                         "See the docs or a link")

    def test_heading_list_quote_emphasis(self):
        self.assertEqual(cs.speakable("## Result\n- **fixed** it\n> quoted"),
                         "Result.\nfixed it\nquoted")

    def test_arrows_and_dashes(self):
        self.assertEqual(cs.speakable("a → b — c"), "a to b, c")

    def test_table_rows_become_sentences(self):
        self.assertEqual(cs.speakable("| a | b |\n|---|---|\n| 1 | 2 |"), "a, b.\n1, 2.")

    def test_long_text_is_cut_at_a_sentence(self):
        text = cs.speakable("Short sentence. " * 400)
        self.assertLessEqual(len(text), cs.MAX_SPOKEN_CHARS + len(" That's the gist."))
        self.assertTrue(text.endswith(". That's the gist."))


class CueTest(unittest.TestCase):
    def test_leading_cue_is_parsed(self):
        m = cs.CUE.match("[happy thumbup] I fixed it.")
        self.assertEqual(m.groups(), ("happy", "thumbup"))
        self.assertEqual("[happy thumbup] I fixed it."[m.end():], "I fixed it.")

    def test_cue_must_lead(self):
        self.assertIsNone(cs.CUE.match("I fixed it [happy thumbup]."))

    def test_unknown_cue_values_are_not_sent(self):
        with mock.patch.dict(os.environ, {"CLAUDE_SPEAK_AVATAR_URL": "http://127.0.0.1:9"}), \
                mock.patch.object(cs.urllib.request, "urlopen") as urlopen:
            cs.send_cue("ecstatic", "backflip")
        urlopen.assert_not_called()

    def test_no_avatar_url_sends_nothing(self):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_SPEAK_AVATAR_URL"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(cs.urllib.request, "urlopen") as urlopen:
            cs.send_cue("happy", "thumbup")
        urlopen.assert_not_called()


class OwnReplyTest(unittest.TestCase):
    def test_status_lines_are_own_replies(self):
        for text in ("🔊 Speaking.", "  claude-speak: saved.", "No change."):
            self.assertTrue(cs.is_own_reply(text), text)

    def test_normal_reply_is_not(self):
        self.assertFalse(cs.is_own_reply("I fixed the test."))


class TranscriptTest(unittest.TestCase):
    def test_last_response_joins_the_turn_and_skips_sidechains(self):
        self.assertEqual(cs.last_response(FIXTURES / "turn.jsonl"),
                         "Looking at it.\n\nFixed the race in token refresh; all tests pass.")

    def test_last_response_skips_own_replies(self):
        self.assertEqual(cs.last_response(FIXTURES / "own_reply.jsonl"),
                         "The cache keys on session id.")

    def test_meta_entries_do_not_end_the_turn(self):
        self.assertEqual(cs.last_response(FIXTURES / "meta_entry.jsonl"), "Working.\n\nDone.")

    def test_current_status_is_latest_text_of_this_turn(self):
        self.assertEqual(cs.current_status(FIXTURES / "turn.jsonl"),
                         ("a3", "Fixed the race in token refresh; all tests pass."))
        self.assertEqual(cs.current_status(FIXTURES / "mid_turn.jsonl"),
                         ("a1", "Reading the module first."))

    def test_current_status_stops_at_the_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.jsonl"
            rows = [{"type": "summary"}, {"type": "assistant", "uuid": "a0",
                                          "message": {"content": [{"type": "text", "text": "Old."}]}},
                    {"type": "user", "uuid": "u1", "message": {"content": "next"}}]
            path.write_text("".join(json.dumps(r) + "\n" for r in rows))
            self.assertEqual(cs.current_status(path), ("", ""))


@mock.patch.dict(os.environ, CLEAN_ENV, clear=True)
class SettingsTest(TempDataTest):
    def test_defaults(self):
        s = cs.load_settings(data=self.data)
        self.assertEqual((s["voice"], s["speed"], s["auto_speak"], s["summarize"]),
                         ("af_heart", 1.1, True, True))

    def test_precedence(self):
        (self.data / "options.json").write_text(json.dumps({"voice": "am_adam", "speed": "1.3"}))
        self.assertEqual(cs.load_settings(data=self.data)["voice"], "am_adam")
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_OPTION_VOICE": "am_echo"}):
            self.assertEqual(cs.load_settings(data=self.data)["voice"], "am_echo")
            cs.save_overrides(self.data, {"voice": "bm_george"})
            self.assertEqual(cs.load_settings(data=self.data)["voice"], "bm_george")
            self.assertEqual(cs.load_settings({"voice": "bf_emma"}, data=self.data)["voice"], "bf_emma")
            self.assertEqual(cs.load_settings(data=self.data, use_saved_overrides=False)["voice"], "am_echo")
        self.assertEqual(cs.load_settings(data=self.data)["speed"], 1.3)

    def test_unresolved_placeholders_are_ignored(self):
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_OPTION_VOICE": "${user_config.voice}"}):
            self.assertEqual(cs.load_settings(data=self.data)["voice"], "af_heart")

    def test_values_are_normalised(self):
        s = cs.load_settings({"speed": "9", "auto_speak": "off", "summarize": "yes"})
        self.assertEqual((s["speed"], s["auto_speak"], s["summarize"]), (2.0, False, True))
        self.assertEqual(cs.load_settings({"speed": "fast"})["speed"], cs.DEFAULTS["speed"])

    def test_overrides_keep_only_overridable_keys_and_none_removes(self):
        (self.data / "overrides.json").write_text(json.dumps({"voice": "am_adam", "summary_model": "opus"}))
        self.assertEqual(cs.load_overrides(self.data), {"voice": "am_adam"})
        cs.save_overrides(self.data, {"voice": None, "speed": 1.5})
        self.assertEqual(cs.load_overrides(self.data), {"speed": 1.5})


class SummaryCacheTest(TempDataTest):
    def test_same_reply_and_model_hits(self):
        cs.save_summary(self.data, "s1", "Final message.", "haiku", "[neutral none] Short.")
        self.assertEqual(cs.cached_summary(self.data, "s1", "Final message.", "haiku"),
                         "[neutral none] Short.")

    def test_whole_turn_ending_with_the_reply_hits(self):
        cs.save_summary(self.data, "s1", "Final message.", "haiku", "Short.")
        self.assertEqual(cs.cached_summary(self.data, "s1", "Earlier.\n\nFinal message.", "haiku"), "Short.")

    def test_misses(self):
        cs.save_summary(self.data, "s1", "Final message.", "haiku", "Short.")
        self.assertIsNone(cs.cached_summary(self.data, "s1", "Other.", "haiku"))
        self.assertIsNone(cs.cached_summary(self.data, "s1", "Final message.", "sonnet"))
        self.assertIsNone(cs.cached_summary(self.data, "s2", "Final message.", "haiku"))

    def test_unsafe_session_ids_are_sanitised(self):
        self.assertEqual(cs._safe_id("../../etc/passwd"), "etcpasswd")
        self.assertIsNone(cs._summary_file(self.data, "../"))


class PrepareTest(unittest.TestCase):
    SETTINGS = {"summarize": True, "summary_model": "haiku"}

    def test_short_text_is_not_summarised(self):
        with mock.patch.object(cs, "summarize") as summarize:
            self.assertEqual(cs.prepare("Done.", self.SETTINGS), "Done.")
        summarize.assert_not_called()

    def test_long_text_is_summarised(self):
        with mock.patch.object(cs, "summarize", return_value="**Fixed** it.") as summarize:
            self.assertEqual(cs.prepare("x" * (cs.SUMMARY_THRESHOLD + 1), self.SETTINGS), "Fixed it.")
        summarize.assert_called_once()

    def test_failed_summary_falls_back_to_text(self):
        with mock.patch.object(cs, "summarize", return_value=None):
            text = "word " * 100
            self.assertEqual(cs.prepare(text, self.SETTINGS), text.strip())

    def test_force_full_skips_summary(self):
        with mock.patch.object(cs, "summarize") as summarize:
            cs.prepare("x" * 500, self.SETTINGS, force_full=True)
        summarize.assert_not_called()


class QuestionTextTest(unittest.TestCase):
    def test_question_is_spoken_with_recommendation(self):
        text = cs.question_text({"questions": [{"question": "Which runner?", "options": [
            {"label": "unittest (Recommended)"}, {"label": "pytest"}]}]})
        self.assertIn("Which runner?", text)
        self.assertIn("unittest", text)

    def test_empty_input(self):
        self.assertEqual(cs.question_text({}), "")


class PromptHushTest(TempDataTest):
    # cmd_hook skips nested and headless runs; tests may run under either.
    ENV = {k: v for k, v in CLEAN_ENV.items()
           if k not in ("CLAUDE_SPEAK_NESTED", "CLAUDE_CODE_ENTRYPOINT")}

    def run_hook(self, event, stub_request=True):
        args = mock.Mock(data_dir=str(self.data))
        with mock.patch.dict(os.environ, self.ENV, clear=True), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(event))), \
                mock.patch.object(cs, "socket_path", return_value=self.data / "none.sock"), \
                mock.patch.object(cs, "request", wraps=None if stub_request else cs.request) as request:
            cs.cmd_hook(args)
        return request

    def test_new_prompt_stops_only_its_session(self):
        request = self.run_hook({"hook_event_name": "UserPromptSubmit", "session_id": "s1"})
        request.assert_called_once_with(self.data, "POST", "/stop", {"session": "s1"}, timeout=1)

    def test_no_server_is_fine(self):
        self.run_hook({"hook_event_name": "UserPromptSubmit", "session_id": "s1"},
                      stub_request=False)  # must not raise

    def test_summary_finished_after_a_new_prompt_is_dropped(self):
        job = {"text": "reply", "settings": {}, "session": "s1", "t": time.time() - 5}
        self.run_hook({"hook_event_name": "UserPromptSubmit", "session_id": "s1"})
        with mock.patch("sys.stdin", io.StringIO(json.dumps(job))), \
                mock.patch.object(cs, "server_health", return_value=None), \
                mock.patch.object(cs, "prepare", return_value="summary"), \
                mock.patch.object(cs, "send_to_server") as send:
            cs.cmd_worker(mock.Mock(data_dir=str(self.data)))
            send.assert_not_called()
            job["t"] = time.time() + 5  # spawned after the prompt, e.g. by /speak
            with mock.patch("sys.stdin", io.StringIO(json.dumps(job))):
                cs.cmd_worker(mock.Mock(data_dir=str(self.data)))
            send.assert_called_once()


class LanesTest(TempDataTest):
    """Priority lanes (US-005): the client picks the lane per hook event."""
    ENV, run_hook = PromptHushTest.ENV, PromptHushTest.run_hook

    def spawned_priority(self, event):
        with mock.patch.object(cs, "spawn_worker") as spawn:
            self.run_hook(event)
        spawn.assert_called_once()
        return spawn.call_args.kwargs.get("priority", "normal")

    def test_a_question_is_urgent(self):
        event = {"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "AskUserQuestion",
                 "tool_input": {"questions": [{"question": "Which one?"}]}}
        self.assertEqual(self.spawned_priority(event), "urgent")

    def test_a_reply_is_normal(self):
        transcript = self.data / "t.jsonl"
        transcript.write_text("")
        event = {"hook_event_name": "Stop", "session_id": "s1", "transcript_path": str(transcript),
                 "last_assistant_message": "Done."}
        self.assertEqual(self.spawned_priority(event), "normal")

    def test_a_status_line_is_low(self):
        with mock.patch.object(cs, "current_status", return_value=("u1", "Checking the tests.")), \
                mock.patch.object(cs, "server_health", return_value={"busy": False}), \
                mock.patch.object(cs, "spawn_worker") as spawn:
            cs.maybe_interject(self.data, "s1", self.data / "t.jsonl", {}, "proj")
        self.assertEqual(spawn.call_args.kwargs["priority"], "low")

    def work(self, priority, age):
        job = {"text": "status", "settings": {}, "session": "s1", "t": time.time() - age,
               "priority": priority}
        with mock.patch("sys.stdin", io.StringIO(json.dumps(job))), \
                mock.patch.object(cs, "server_health", return_value=None), \
                mock.patch.object(cs, "prepare", return_value="Checking."), \
                mock.patch.object(cs, "send_to_server") as send:
            cs.cmd_worker(mock.Mock(data_dir=str(self.data)))
        return send, job

    def test_a_status_line_summarised_too_slowly_is_dropped(self):
        send, _ = self.work("low", cs.STALE_LOW + 1)
        send.assert_not_called()
        for priority in ("normal", "urgent"):  # replies and questions are never stale
            send, _ = self.work(priority, cs.STALE_LOW + 1)
            send.assert_called_once()

    def test_the_worker_sends_the_lane_and_the_hook_time(self):
        send, job = self.work("low", 1)
        send.assert_called_once_with(self.data, "Checking.", {}, "s1", "", "low", job["t"])

    def test_the_speak_body_carries_priority_and_at(self):
        with mock.patch.object(cs, "ensure_server"), \
                mock.patch.object(cs, "request", return_value=(202, b"")) as request:
            cs.send_to_server(self.data, "hi", {"voice": "v", "speed": 1.0}, "s1", "p", "urgent", 7.0)
        request.assert_called_once_with(self.data, "POST", "/speak", {
            "text": "hi", "voice": "v", "speed": 1.0, "session": "s1", "label": "p",
            "priority": "urgent", "at": 7.0})


class AgainTest(TempDataTest):
    def run_again(self, health, status=200, session=None):
        args = mock.Mock(data_dir=str(self.data), session=session)
        with mock.patch.object(cs, "server_health", return_value=health), \
                mock.patch.object(cs, "request", return_value=(status, b"")) as request, \
                mock.patch.object(cs, "ensure_server") as ensure, \
                mock.patch("builtins.print") as out:
            cs.cmd_again(args)
        ensure.assert_not_called()
        return request, out.call_args.args[0]

    def test_no_server_means_nothing_to_replay(self):
        request, said = self.run_again(None)
        request.assert_not_called()
        self.assertEqual(said, "claude-speak: nothing to replay.")

    def test_server_with_nothing_stored(self):
        _, said = self.run_again({"ok": True}, status=404)
        self.assertEqual(said, "claude-speak: nothing to replay.")

    def test_server_gone_since_the_health_check(self):
        args = mock.Mock(data_dir=str(self.data), session=None)
        with mock.patch.object(cs, "server_health", return_value={"ok": True}), \
                mock.patch.object(cs, "request", side_effect=ConnectionRefusedError), \
                mock.patch("builtins.print") as out:
            cs.cmd_again(args)
        out.assert_called_once_with("claude-speak: nothing to replay.")

    def test_replay_posts_the_session(self):
        request, said = self.run_again({"ok": True}, session="s1")
        request.assert_called_once_with(mock.ANY, "POST", "/replay", {"session": "s1"})
        self.assertEqual(said, "claude-speak: replaying.")


class VersionTest(unittest.TestCase):
    def test_version_tuple(self):
        self.assertEqual(cs._version_tuple("0.10.2"), (0, 10, 2))
        self.assertEqual(cs._version_tuple(""), ())
        self.assertEqual(cs._version_tuple("0.5.0-dev"), ())
        self.assertGreater(cs._version_tuple("0.10.0"), cs._version_tuple("0.9.9"))

    def test_only_an_older_server_is_stale(self):
        with mock.patch.object(cs, "VERSION", "0.5.0"):
            self.assertTrue(cs._stale({"version": "0.4.9"}))
            self.assertTrue(cs._stale({}))  # from before /health had a version
            self.assertFalse(cs._stale({"version": "0.5.0"}))
            self.assertFalse(cs._stale({"version": "0.6.0"}))  # an older client keeps a newer server
        with mock.patch.object(cs, "VERSION", ""):
            self.assertFalse(cs._stale({}))  # unreadable client version: never restart

    def test_client_reads_the_plugin_manifest(self):
        self.assertEqual(cs.VERSION, json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"])


OLD_HEALTH = {"ok": True, "version": "0.4.9"}
NEW_HEALTH = {"ok": True, "version": "0.5.0"}


class EnsureServerTest(TempDataTest):
    """ensure_server() replacing an older server (US-030); no real server or uv."""

    OLD = OLD_HEALTH
    NEW = NEW_HEALTH

    def ensure(self, health, quit_status=202):
        started = mock.Mock()
        started.poll.return_value = None
        with mock.patch.object(cs, "VERSION", "0.5.0"), \
                mock.patch.object(cs, "server_health", side_effect=health), \
                mock.patch.object(cs, "request", return_value=(quit_status, b"")) as request, \
                mock.patch.object(cs.shutil, "which", return_value="/usr/bin/uv"), \
                mock.patch.object(cs.subprocess, "Popen", return_value=started) as popen, \
                mock.patch.object(cs.time, "sleep"), \
                mock.patch.object(cs, "log_error") as logged:
            result = cs.ensure_server(self.data)
        return result, request, popen, logged

    def test_same_or_newer_server_is_used_as_it_is(self):
        for health in (self.NEW, {"ok": True, "version": "0.6.0"}):
            result, request, popen, _ = self.ensure([health])
            self.assertEqual(result, health)
            request.assert_not_called()
            popen.assert_not_called()

    def test_older_server_is_asked_to_quit_then_replaced(self):
        # outside the lock, inside it, gone twice after /quit, then the new server answers
        result, request, popen, _ = self.ensure([self.OLD, self.OLD, None, None, self.NEW])
        self.assertEqual(result, self.NEW)
        request.assert_called_once_with(self.data, "POST", "/quit")
        popen.assert_called_once()

    def test_one_slow_health_check_is_not_gone(self):
        # a miss, then the old server answers again, then it has really gone
        result, _, popen, _ = self.ensure([self.OLD, self.OLD, None, self.OLD, None, None, self.NEW])
        self.assertEqual(result, self.NEW)
        popen.assert_called_once()

    def test_quit_that_cannot_be_sent_uses_the_old_server(self):
        started = mock.Mock()
        with mock.patch.object(cs, "VERSION", "0.5.0"), \
                mock.patch.object(cs, "server_health", side_effect=[self.OLD, self.OLD]), \
                mock.patch.object(cs, "request", side_effect=ConnectionRefusedError), \
                mock.patch.object(cs.shutil, "which", return_value="/usr/bin/uv"), \
                mock.patch.object(cs.subprocess, "Popen", return_value=started) as popen:
            self.assertEqual(cs.ensure_server(self.data), self.OLD)
        popen.assert_not_called()

    def test_server_already_quitting_is_waited_for_without_a_second_quit(self):
        quitting = {"ok": True, "version": "0.5.0", "quitting": True}  # a newer client asked
        result, request, popen, _ = self.ensure([quitting, quitting, None, None, self.NEW])
        self.assertEqual(result, self.NEW)
        request.assert_not_called()
        popen.assert_called_once()

    def test_no_uv_keeps_using_the_old_server(self):
        with mock.patch.object(cs, "VERSION", "0.5.0"), \
                mock.patch.object(cs, "server_health", return_value=self.OLD), \
                mock.patch.object(cs.shutil, "which", return_value=None):
            self.assertEqual(cs.ensure_server(self.data), self.OLD)
        with mock.patch.object(cs, "server_health", return_value=None), \
                mock.patch.object(cs.shutil, "which", return_value=None), \
                self.assertRaises(RuntimeError):
            cs.ensure_server(self.data)

    def test_after_an_overrun_queued_workers_do_not_wait_again(self):
        (self.data / "retire-overran").touch()
        result, request, popen, logged = self.ensure([self.OLD, self.OLD])
        self.assertEqual(result, self.OLD)
        request.assert_called_once()  # /quit is still asked, harmlessly
        popen.assert_not_called()
        logged.assert_not_called()

    def test_speech_refused_by_an_exiting_server_is_logged(self):
        with mock.patch.object(cs, "ensure_server"), \
                mock.patch.object(cs, "request", return_value=(503, b"")), \
                mock.patch.object(cs, "log_error") as logged:
            cs.send_to_server(self.data, "hi", {"voice": "v", "speed": 1.0}, "s1")
        self.assertIn("speech dropped", logged.call_args.args[1])

    def test_server_from_before_quit_existed_is_used_at_once(self):
        old = {"ok": True}
        result, request, popen, _ = self.ensure([old, old], quit_status=400)
        self.assertEqual(result, old)
        request.assert_called_once()
        popen.assert_not_called()

    def test_drain_past_the_wait_is_logged_and_nothing_starts(self):
        with mock.patch.object(cs, "RETIRE_WAIT", 0):
            result, _, popen, logged = self.ensure([self.OLD, self.OLD])
        self.assertEqual(result, self.OLD)
        popen.assert_not_called()
        self.assertIn("still draining", logged.call_args.args[1])
        self.assertTrue((self.data / "retire-overran").exists())

    def test_another_worker_replaced_it_while_this_one_waited_for_the_lock(self):
        result, request, popen, _ = self.ensure([self.OLD, self.NEW])
        self.assertEqual(result, self.NEW)
        request.assert_not_called()
        popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
