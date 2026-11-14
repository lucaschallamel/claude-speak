"""Tests for scripts/server.py with Kokoro stubbed out: no model, no audio, no uv.

Run: python3 -m unittest discover tests
"""

import json
import os
import sys
import tempfile
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# server.py imports numpy and kokoro_onnx at the top; stub them when absent so
# the tests run on a bare python3 like the client's.
for name in ("numpy", "kokoro_onnx"):
    try:
        __import__(name)
    except ImportError:
        stub = types.ModuleType(name)
        stub.Kokoro = object
        stub.ndarray = object
        sys.modules[name] = stub

import claude_speak  # noqa: E402  (stdlib only; its unix-socket HTTP connection)
import server  # noqa: E402


class SplitChunksTest(unittest.TestCase):
    def test_short_text_is_one_chunk(self):
        self.assertEqual(server.split_chunks("One. Two!"), ["One. Two!"])

    def test_long_text_splits_at_sentences_under_the_limit(self):
        sentence = "This is a sentence of moderate length."
        chunks = server.split_chunks(" ".join([sentence] * 20))
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), server.CHUNK_CHARS)
            self.assertTrue(chunk.endswith("."))

    def test_newlines_split_and_blanks_vanish(self):
        self.assertEqual(server.split_chunks("\n  a\n\n b  \n"), ["a b"])

    def test_empty(self):
        self.assertEqual(server.split_chunks("   "), [])


def speaker() -> "server.Speaker":
    """A Speaker with queue state only: no Kokoro, player or playback thread."""
    sp = server.Speaker.__new__(server.Speaker)
    sp.state_lock = threading.Lock()
    sp.wake = threading.Condition(sp.state_lock)
    sp.queue, sp.current, sp.proc, sp.warm_proc = [], None, None, None
    sp.last_seen, sp.busy_until = {}, 0.0
    sp.clips, sp.last_clip = {}, ""
    sp.voices = {"af_heart", "bm_george"}
    return sp


class SpeakerQueueTest(unittest.TestCase):
    def test_newer_speech_from_a_session_replaces_its_queued_speech(self):
        sp = speaker()
        sp.speak("old", "bm_george", 1.0, session="a")
        sp.speak("other", "bm_george", 1.0, session="b")
        sp.speak("new", "bm_george", 1.0, session="a")
        self.assertEqual([(j.session, j.text.split(": ")[-1]) for j in sp.queue],
                         [("b", "other"), ("a", "new")])

    def test_newer_speech_cancels_the_session_s_current_job(self):
        sp = speaker()
        sp.current = server.Job("a", "playing", "bm_george", 1.0)
        sp.speak("new", "bm_george", 1.0, session="a")
        self.assertTrue(sp.current.cancelled)

    def test_label_prefix_only_when_another_session_is_active(self):
        sp = speaker()
        sp.speak("alone", "bm_george", 1.0, session="a", label="claude-speak")
        self.assertEqual(sp.queue[-1].text, "alone")
        sp.speak("hello", "bm_george", 1.0, session="b", label="agent_avatar")
        self.assertEqual(sp.queue[-1].text, "agent avatar: hello")

    def test_stop_clears_everything(self):
        sp = speaker()
        sp.speak("one", "bm_george", 1.0, session="a")
        sp.speak("two", "bm_george", 1.0, session="b")
        jobs = list(sp.queue)
        sp.stop()
        self.assertEqual(sp.queue, [])
        self.assertTrue(all(j.cancelled for j in jobs))

    def test_stop_with_session_leaves_other_sessions(self):
        sp = speaker()
        sp.current = server.Job("a", "playing", "bm_george", 1.0)
        sp.speak("b talks", "bm_george", 1.0, session="b")
        sp.queue.append(server.Job("a", "queued", "bm_george", 1.0))
        sp.stop("a")
        self.assertTrue(sp.current.cancelled)
        self.assertEqual([j.session for j in sp.queue], ["b"])
        self.assertFalse(sp.queue[0].cancelled)

    def test_unknown_voice_falls_back(self):
        sp = speaker()
        self.assertEqual(sp.resolve_voice("bm_george"), "bm_george")
        self.assertEqual(sp.resolve_voice("xx_nobody"), "af_heart")


class ReplayTest(unittest.TestCase):
    """Samples are opaque to the replay logic, so plain strings stand in for numpy arrays."""

    def remembered(self, sp, session, chunks=("c1", "c2")):
        sp._remember(server.Job(session, "text", "bm_george", 1.0), list(chunks), 24000)

    def test_replay_plays_stored_chunks_without_synthesis(self):
        sp = speaker()
        sp.synth = mock.Mock(side_effect=AssertionError("synthesised on replay"))
        self.remembered(sp, "a")
        self.assertTrue(sp.replay())
        self.assertEqual(list(sp._audio(sp.queue[0])), [("c1", 24000), ("c2", 24000)])

    def test_replay_goes_first_and_interrupts_the_current_clip(self):
        sp = speaker()
        self.remembered(sp, "a")
        sp.current = server.Job("b", "playing", "bm_george", 1.0)
        sp.speak("queued", "bm_george", 1.0, session="c")
        self.assertTrue(sp.replay("a"))
        self.assertTrue(sp.current.cancelled)
        self.assertEqual([(j.session, j.clip is not None) for j in sp.queue], [("a", True), ("c", False)])

    def test_nothing_stored_or_unknown_session(self):
        sp = speaker()
        self.assertFalse(sp.replay())
        self.remembered(sp, "a")
        self.assertFalse(sp.replay("b"))
        self.assertEqual(sp.queue, [])

    def test_default_is_the_most_recent_session(self):
        sp = speaker()
        self.remembered(sp, "a", ["a1"])
        self.remembered(sp, "b", ["b1"])
        sp.replay()
        self.assertEqual(sp.queue[0].clip.chunks, ["b1"])
        sp.replay("a")
        self.assertEqual(sp.queue[0].clip.chunks, ["a1"])

    def test_only_fully_made_speech_is_kept_even_if_stopped(self):
        sp = speaker()
        long_text = "One sentence of a longer reply, padded out to fill space. " * 10
        self.assertGreater(len(server.split_chunks(long_text)), 1)
        sp._remember(server.Job("a", long_text, "bm_george", 1.0, cancelled=True), ["x"], 24000)
        sp._remember(server.Job("a", "text", "bm_george", 1.0), [], 24000)
        self.assertEqual(sp.clips, {})
        stopped = server.Job("a", "Short reply.", "bm_george", 1.0, cancelled=True)
        sp._remember(stopped, ["whole"], 24000)
        self.assertEqual(sp.clips["a"].chunks, ["whole"])

    def test_speech_already_stopped_or_superseded_is_not_restarted(self):
        sp = speaker()
        self.remembered(sp, "a", ["stored"])
        sp.current = server.Job("a", "Outdated reply.", "bm_george", 1.0, cancelled=True, made=["old"])
        self.assertTrue(sp.replay())
        self.assertEqual(sp.queue[0].clip.chunks, ["stored"])

    def test_stale_sessions_are_dropped(self):
        sp = speaker()
        self.remembered(sp, "old")
        sp.clips["old"].stored_at -= server.REPLAY_KEEP + 1
        self.remembered(sp, "new")
        self.assertEqual(set(sp.clips), {"new"})

    def test_speech_still_being_made_restarts_from_the_top_not_an_older_clip(self):
        sp = speaker()
        self.remembered(sp, "a", ["older"])
        long_text = " ".join(f"Sentence {i} of a long question, padded out to fill space." for i in range(12))
        sp.current = server.Job("a", long_text, "bm_george", 1.2, made=["c1"], rate=24000)
        self.assertTrue(sp.replay())
        self.assertTrue(sp.current.cancelled)
        job = sp.queue[0]
        self.assertEqual((job.session, job.voice, job.speed, job.clip.chunks), ("a", "bm_george", 1.2, ["c1"]))
        sp.synth = mock.Mock(side_effect=lambda chunk, *_: (chunk, 24000))
        audio = list(sp._audio(job))
        chunks = server.split_chunks(long_text)
        self.assertGreater(len(chunks), 1)
        # The made chunk plays as is; only the rest is synthesised.
        self.assertEqual(audio, [("c1", 24000)] + [(c, 24000) for c in chunks[1:]])
        self.assertEqual(sp.synth.call_count, len(chunks) - 1)

    def test_fully_made_speech_restarts_without_synthesis(self):
        sp = speaker()
        sp.synth = mock.Mock(side_effect=AssertionError("synthesised on replay"))
        sp.current = server.Job("b", "Short.", "bm_george", 1.0, made=["b1"], rate=24000)
        self.assertTrue(sp.replay())
        self.assertEqual(list(sp._audio(sp.queue[0])), [("b1", 24000)])

    def test_a_replay_playing_restarts_with_all_its_chunks(self):
        sp = speaker()
        self.remembered(sp, "a", ["a1", "a2"])
        sp.replay()
        sp.current = sp.queue.pop(0)
        sp.current.made = ["a1"]  # only its first chunk has been produced so far
        sp.replay()
        self.assertEqual(sp.queue[0].clip.chunks, ["a1", "a2"])

    def test_a_finished_restart_is_kept_as_the_last_thing_said(self):
        sp = speaker()
        self.remembered(sp, "a", ["older"])
        restart = server.Job("a", "text", "bm_george", 1.0, clip=server.Clip(["c1"], 24000, 0), replay=True)
        sp._remember(restart, ["c1", "c2"], 24000)
        self.assertEqual(sp.clips["a"].chunks, ["c1", "c2"])

    def test_asking_for_another_session_ignores_the_current_speech(self):
        sp = speaker()
        self.remembered(sp, "a", ["a1"])
        sp.current = server.Job("b", "Now.", "bm_george", 1.0)
        self.assertTrue(sp.replay("a"))
        self.assertEqual(sp.queue[0].clip.chunks, ["a1"])

    def test_a_double_tap_plays_once(self):
        sp = speaker()
        self.remembered(sp, "a")
        sp.speak("queued", "bm_george", 1.0, session="c")
        sp.replay()
        sp.replay()
        self.assertEqual([j.replay for j in sp.queue], [True, False])

    def test_a_double_tap_after_the_replay_started_is_ignored(self):
        sp = speaker()
        self.remembered(sp, "a", ["a1", "a2"])
        sp.replay()
        sp.current = sp.queue.pop(0)
        sp.current.started = time.time()  # just picked up by the playback loop
        self.assertTrue(sp.replay())
        self.assertFalse(sp.current.cancelled)
        self.assertEqual(sp.queue, [])

    def test_a_later_press_restarts_the_replay(self):
        sp = speaker()
        self.remembered(sp, "a", ["a1", "a2"])
        sp.replay()
        sp.current = sp.queue.pop(0)
        sp.current.started = time.time() - server.DOUBLE_TAP - 0.1
        self.assertTrue(sp.replay())
        self.assertTrue(sp.current.cancelled)
        self.assertEqual(sp.queue[0].clip.chunks, ["a1", "a2"])

    def test_clips_older_than_the_keep_time_are_not_replayed(self):
        sp = speaker()
        self.remembered(sp, "a")
        sp.clips["a"].stored_at -= server.REPLAY_KEEP + 1
        self.assertFalse(sp.replay())

    @unittest.skipIf(not hasattr(server.np, "zeros"), "needs numpy (the stub has none)")
    def test_playback_stores_the_samples_without_the_lead_in(self):
        np = server.np
        sp = speaker()
        made = [np.ones(10, np.float32), np.full(5, 2, np.float32)]
        sp.player, sp.lead_in = ["true"], lambda: 0.5
        sp.synth = mock.Mock(side_effect=[(made[0], 24000), (made[1], 24000)])
        played = []
        sp._spawn = lambda path: played.append(Path(path).stat().st_size)
        sp._reap = lambda proc: None
        sp._run(server.Job("a", "One sentence. " * 30, "bm_george", 1.0))
        self.assertEqual(len(played), 2)
        clip = sp.clips["a"]
        self.assertEqual((len(clip.chunks), clip.rate), (2, 24000))
        self.assertTrue(all(np.array_equal(a, b) for a, b in zip(clip.chunks, made)))

    @unittest.skipIf(not hasattr(server.np, "zeros"), "needs numpy (the stub has none)")
    def test_a_cancelled_job_does_not_wait_for_synthesis_in_flight(self):
        np = server.np
        sp = speaker()
        job = server.Job("a", "One sentence. " * 30, "bm_george", 1.0)
        release, first = threading.Event(), [True]

        def synth(*_):
            if not first[0]:
                release.wait(5)  # the second chunk is slow to make
            first[0] = False
            return np.ones(10, np.float32), 24000

        def spawn(path):
            job.cancelled = True  # stopped while its first chunk plays
        sp.player, sp.lead_in, sp.synth = ["true"], lambda: 0.0, synth
        sp._spawn, sp._reap = spawn, lambda proc: None
        before = set(Path(tempfile.gettempdir()).glob("claude-speak-*.wav"))
        runner = threading.Thread(target=sp._run, args=(job,))
        runner.start()
        runner.join(1)
        self.assertFalse(runner.is_alive(), "_run waited for the slow chunk")
        release.set()
        time.sleep(0.2)
        self.assertEqual(set(Path(tempfile.gettempdir()).glob("claude-speak-*.wav")), before)

    @unittest.skipIf(not hasattr(server.np, "zeros"), "needs numpy (the stub has none)")
    def test_playback_waits_for_a_slow_chunk_when_nothing_is_cancelled(self):
        np = server.np
        sp = speaker()
        job = server.Job("a", "One sentence of a longer reply, padded out. " * 12, "bm_george", 1.0)
        n = len(server.split_chunks(job.text))
        self.assertGreater(n, 1)
        calls = []

        def synth(*_):
            if calls:
                time.sleep(0.2)  # later chunks take several 50 ms polls to make
            calls.append(1)
            return np.ones(10, np.float32), 24000
        played = []
        sp.player, sp.lead_in, sp.synth = ["true"], lambda: 0.0, synth
        sp._spawn, sp._reap = played.append, lambda proc: None
        sp._run(job)
        self.assertEqual(len(played), n)

    @unittest.skipIf(not hasattr(server.np, "zeros"), "needs numpy (the stub has none)")
    def test_files_queued_by_a_cancelled_job_are_deleted(self):
        np = server.np
        sp = speaker()
        # Long enough that the producer blocks on the full queue before making every chunk.
        job = server.Job("a", "One sentence of a longer reply, padded out. " * 60, "bm_george", 1.0)
        self.assertGreater(len(server.split_chunks(job.text)), 6)
        spawned = []

        def spawn(path):
            spawned.append(path)
            time.sleep(0.3)  # the producer fills the queue meanwhile
            job.cancelled = True
        sp.player, sp.lead_in = ["true"], lambda: 0.0
        sp.synth = lambda *_: (np.ones(10, np.float32), 24000)
        sp._spawn, sp._reap = spawn, lambda proc: None
        before = set(Path(tempfile.gettempdir()).glob("claude-speak-*.wav"))
        sp._run(job)
        self.assertEqual(len(spawned), 1)
        time.sleep(0.3)
        self.assertEqual(set(Path(tempfile.gettempdir()).glob("claude-speak-*.wav")), before)
        self.assertNotIn("a", sp.clips)  # cut off before all its chunks were made

    @unittest.skipIf(not hasattr(server.np, "zeros"), "needs numpy (the stub has none)")
    def test_fully_made_speech_stopped_while_queued_chunks_wait_is_kept(self):
        np = server.np
        sp = speaker()
        job = server.Job("a", "One sentence of a longer reply, padded out. " * 20, "bm_george", 1.0)
        n = len(server.split_chunks(job.text))
        self.assertEqual(n, 4)  # one playing, two queued, the last made and waiting to be queued

        def spawn(path):
            time.sleep(0.3)
            job.cancelled = True
        sp.player, sp.lead_in = ["true"], lambda: 0.0
        sp.synth = lambda *_: (np.ones(10, np.float32), 24000)
        sp._spawn, sp._reap = spawn, lambda proc: None
        sp._run(job)
        self.assertEqual(len(sp.clips["a"].chunks), n)

    def test_at_most_the_session_cap_is_kept_oldest_first_out(self):
        sp = speaker()
        for i in range(server.REPLAY_SESSIONS + 2):
            self.remembered(sp, f"s{i}")
            sp.clips[f"s{i}"].stored_at -= server.REPLAY_SESSIONS + 2 - i  # s0 is the oldest
        self.assertEqual(len(sp.clips), server.REPLAY_SESSIONS)
        self.assertNotIn("s0", sp.clips)
        self.assertNotIn("s1", sp.clips)
        self.assertIn(f"s{server.REPLAY_SESSIONS + 1}", sp.clips)

    def test_synthesis_stops_when_the_job_is_cancelled(self):
        sp = speaker()
        job = server.Job("a", "One sentence. " * 40, "bm_george", 1.0)

        def synth(*_):
            job.cancelled = True
            return "s", 24000
        sp.synth = synth
        self.assertEqual(len(list(sp._audio(job))), 1)


class ServerSocketTest(unittest.TestCase):
    def test_only_the_user_can_connect_whatever_the_umask(self):
        tmp = tempfile.mkdtemp()
        old = os.umask(0o000)  # the most permissive umask a /tmp fallback could see
        try:
            srv = server.Server(os.path.join(tmp, "s.sock"), None, "model")
        finally:
            os.umask(old)
        try:
            self.assertEqual(os.stat(srv.server_address).st_mode & 0o777, 0o600)
            self.assertEqual(os.umask(old), old, "umask restored after bind")
        finally:
            srv.server_close()


class ReplayEndpointTest(unittest.TestCase):
    """POST /replay over a real unix socket, with a stand-in speaker."""

    def post(self, has_clip, body):
        fake = mock.Mock()
        fake.replay.return_value = has_clip
        path = os.path.join(tempfile.mkdtemp(), "s.sock")
        srv = server.Server(path, fake, "model")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            conn = claude_speak._UnixConnection(Path(path), 5)
            conn.request("POST", "/replay", body=json.dumps(body),
                         headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            return resp.status, json.loads(resp.read()), fake
        finally:
            srv.shutdown()
            srv.server_close()

    def test_replays_the_session_asked_for(self):
        status, body, fake = self.post(True, {"session": "s1"})
        self.assertEqual((status, body), (200, {"ok": True}))
        fake.replay.assert_called_once_with("s1")

    def test_nothing_to_replay_is_404(self):
        status, body, fake = self.post(False, {})
        self.assertEqual((status, body), (404, {"error": "nothing to replay"}))
        fake.replay.assert_called_once_with("")


class WatchDictationTest(unittest.TestCase):
    def test_stops_once_per_press_and_ignores_missing_file(self):
        state = Path(tempfile.mkdtemp()) / "state"
        stops = []
        threading.Thread(target=server.watch_dictation,
                         args=(state, lambda: stops.append(1), 0.005), daemon=True).start()

        def settle(text):
            if text is None:
                state.unlink(missing_ok=True)
            else:
                state.write_text(text)
            time.sleep(0.05)

        settle(None)
        settle("idle\n")
        self.assertEqual(stops, [])
        settle("recording\n")
        settle("")  # a write caught halfway is not idle
        settle("transcribing\n")
        self.assertEqual(len(stops), 1)
        settle("idle\n")
        settle("recording")
        self.assertEqual(len(stops), 2)


if __name__ == "__main__":
    unittest.main()
