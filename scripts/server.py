# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "kokoro-onnx>=0.4,<1",
#     "numpy>=2",
# ]
# ///
"""claude-speak TTS server: keeps Kokoro loaded and plays speech on request.

Listens for HTTP on a unix socket in the data dir. Speech from different
sessions is queued; a new /speak from the same session replaces its older one.
Exits by itself after a period with nothing to do.

Speech plays in lanes: a replay first, then "urgent" (questions), "normal" (replies),
"low" (status lines), first come first served within a lane. Speech from another
session in a higher lane cuts a status line at once and a reply at its next chunk;
the reply resumes afterwards. A status line not started 5 s after "at" is dropped.

  GET  /health   model, player, voices, busy, version and quitting
  POST /speak    {"text", "voice", "speed", "session", "label", "priority"?, "at"?}; returns
                 at once, plays in turn; "priority" is urgent, normal (default) or low, "at"
                 the epoch time of the hook that asked for it; priority is a request, not
                 checked: anyone who can reach the socket (only the user) may ask for urgent
  POST /warm     play silence to wake the output device before speech is ready
  POST /synth    same body; returns the whole utterance as a WAV
  POST /stop     stop playback and clear the queue; {"session"} stops only that session
  POST /replay   {"session"?}; say the last thing again at once: the speech playing now restarts
                 from the top, else that session's (or the most recent) stored utterance plays
                 without synthesis; 404 when there is none
  POST /quit     exit once nothing is queued or playing, for a newer version; meanwhile
                 /speak, /replay and /warm answer 503
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import queue
import re
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import wave
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro

RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODELS = {
    "fp32": "kokoro-v1.0.onnx",       # ~310 MB, best quality
    "fp16": "kokoro-v1.0.fp16.onnx",  # ~170 MB
    "int8": "kokoro-v1.0.int8.onnx",  # ~90 MB, fastest on slow CPUs
}
VOICES_FILE = "voices-v1.0.bin"


MANIFEST = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"


def plugin_version(manifest: Path = MANIFEST) -> str:
    """The plugin version this server runs; the client restarts an older server after an update.
    claude_speak.plugin_version is its twin: this script runs standalone under uv and imports
    nothing from the client."""
    try:
        return str(json.loads(manifest.read_text()).get("version") or "")
    except (OSError, ValueError, AttributeError):
        return ""


VERSION = plugin_version()
# A quitting server stops what it is still playing after this long and exits, so a hung player
# can't keep it alive. Below the client's RETIRE_WAIT (120 s), so the waiting client still sees
# it go and starts the new server.
DRAIN_CAP = 100

# Kokoro voice names start with a language code.
LANGS = {"a": "en-us", "b": "en-gb", "e": "es", "f": "fr-fr", "h": "hi",
         "i": "it", "j": "ja", "p": "pt-br", "z": "cmn"}

# Start speaking after the first chunk instead of waiting for the whole text. Small, because
# speech from another session waits for the chunk being synthesised (it can't be interrupted)
# and, over a reply, for the chunk playing to end.
CHUNK_CHARS = 80

# How long the output must be playing before speech starts, so the first words
# aren't lost while an idle device (Bluetooth especially) wakes up. Time already
# spent playing, e.g. silence from /warm while a summary is written, counts.
LEAD_IN = float(os.environ.get("CLAUDE_SPEAK_LEAD_IN", 2.0))
MIN_LEAD_IN = 0.25

# Longest /warm keeps the output awake while it waits for speech.
WARM_SECS = 20

# Output that went quiet less than this long ago is still awake. PipeWire
# suspends idle outputs after 5 seconds.
STAY_AWAKE = 3.0

# While another session has spoken this recently, speech starts with the name
# of the project it came from.
OTHERS_ACTIVE = 300.0

# How long a session's last utterance is kept for /replay (in memory only).
REPLAY_KEEP = 3600.0
# At most this many sessions' utterances are kept; the oldest goes first.
REPLAY_SESSIONS = 32
# A second /replay this soon after a replay started is a double tap: it is ignored.
DOUBLE_TAP = 0.5

# Speech lanes: a smaller number plays first. A replay ranks above them all.
PRIORITIES = {"urgent": 0, "normal": 1, "low": 2}
NORMAL, LOW, REPLAY_PRIORITY = PRIORITIES["normal"], PRIORITIES["low"], -1
# A status line (low) not started this long after its hook is no longer worth hearing.
STALE_LOW = 5.0

# Dictation state file (voxtype's default). Speech stops when it leaves "idle",
# so Claude never talks over the user.
DICTATION_STATE = os.environ.get("CLAUDE_SPEAK_DICTATION_STATE") or os.path.join(
    os.environ.get("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid()), "voxtype", "state")


def log(message: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}", flush=True)


def download(name: str, dest_dir: Path) -> Path:
    dest = dest_dir / name
    if dest.exists():
        return dest
    log(f"downloading {name} ...")
    part = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(f"{RELEASE}/{name}") as resp, open(part, "wb") as out:
        shutil.copyfileobj(resp, out, length=1 << 20)
    part.rename(dest)
    log(f"downloaded {name} ({dest.stat().st_size // (1 << 20)} MB)")
    return dest


def find_player() -> list[str] | None:
    """A command that plays a WAV file given as its last argument."""
    candidates = [
        ["afplay"],                                       # macOS
        ["pw-play"],                                      # PipeWire
        ["paplay"],                                       # PulseAudio
        ["aplay", "-q"],                                  # ALSA
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
    ]
    override = os.environ.get("CLAUDE_SPEAK_PLAYER")
    if override:
        candidates.insert(0, override.split())
    for cmd in candidates:
        if shutil.which(cmd[0]):
            return cmd
    return None


def _pack(parts, limit: int) -> list[str]:
    """Join consecutive parts into chunks of up to limit characters; a longer part stays whole."""
    chunks, current = [], ""
    for part in filter(None, (p.strip() for p in parts)):
        if current and len(current) + len(part) > limit:
            chunks.append(current)
            current = part
        else:
            current = f"{current} {part}".strip()
    if current:
        chunks.append(current)
    return chunks


def split_chunks(text: str) -> list[str]:
    """Chunks of about CHUNK_CHARS: sentences, a long one split at commas and semicolons
    (not colons, so a "project: " label stays with its words), short ones packed together.
    A piece with no such break stays whole; _pack ignores the joining space, so a chunk can
    be one character over."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return _pack([c for s in sentences for c in re.split(r"(?<=[,;])\s+", s)], CHUNK_CHARS)


def wav_bytes(samples: np.ndarray, rate: int) -> bytes:
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


@dataclass
class Job:
    session: str
    text: str
    voice: str
    speed: float
    cancelled: bool = False
    clip: Clip | None = None  # on a replay: chunks already made, played before synthesising the rest
    replay: bool = False      # queued by /replay; a newer /replay replaces it
    made: list = field(default_factory=list)  # chunks produced so far (no lead-in)
    rate: int = 0
    started: float = 0.0  # when the playback loop picked it up
    priority: int = NORMAL
    at: float = 0.0       # when the hook asked for it (epoch); a stale status line is dropped
    played: int = 0       # chunks fully played; a resumed job starts after them
    preempt: bool = False  # stop at the next chunk boundary, then resume
    prefetched: threading.Event | None = None  # set once _prefetch has made (or failed) chunk 1
    count: int = -1  # chunks in text, split once (chunk_count()); -1: not split yet

    def chunk_count(self) -> int:
        if self.count < 0:
            self.count = len(split_chunks(self.text))
        return self.count


@dataclass
class Clip:
    chunks: list  # per-chunk samples, without the lead-in silence
    rate: int
    stored_at: float


def hook_time(at, now: float) -> float:
    """The hook time a client sent, or now when it is missing, unreadable or in the future."""
    try:
        at = float(at)
    except (TypeError, ValueError, OverflowError):  # OverflowError: a huge JSON integer
        return now
    return at if math.isfinite(at) and at <= now else now


class Closed(Exception):
    """The server is exiting: speech can no longer be queued."""


class Speaker:
    """Plays utterances one at a time, by lane (PRIORITIES), in order within a lane.

    Sessions take turns: speech from one session waits for another's in the same or a
    higher lane. A newer utterance from the same session replaces its older one, playing
    or queued, since that reply is out of date; a status line never replaces a question
    or reply, it is dropped instead.
    """

    prefetcher: threading.Thread | None = None  # the one _prefetch worker running, if any
    prefetch_next: Job | None = None  # the question it makes chunk 1 for next
    closed = False  # under state_lock: set by close() (/quit) or by watch_idle as it exits
    synths = 0  # under state_lock: /synth requests in flight; the server doesn't exit mid-reply

    def __init__(self, kokoro: Kokoro, player: list[str] | None, silence: Path):
        self.kokoro = kokoro
        self.player = player
        self.silence = silence
        self.voices = set(kokoro.get_voices())
        self.synth_lock = threading.Lock()
        self.state_lock = threading.Lock()
        self.wake = threading.Condition(self.state_lock)
        self.queue: list[Job] = []
        self.current: Job | None = None
        self.last_seen: dict[str, float] = {}  # session -> last /speak time
        self.clips: dict[str, Clip] = {}  # session -> last fully synthesised utterance
        self.last_clip = ""  # session whose clip was stored most recently
        self.proc: subprocess.Popen | None = None
        self.warm_proc: subprocess.Popen | None = None
        self.busy_until = 0.0
        # Output-awake tracking, guarded by state_lock.
        self.playing = 0
        self.awake_since = 0.0
        self.quiet_since = 0.0
        threading.Thread(target=self._loop, daemon=True).start()

    def resolve_voice(self, voice: str) -> str:
        return voice if voice in self.voices else "af_heart"

    def synth(self, text: str, voice: str, speed: float, unless=None) -> tuple[np.ndarray, int] | None:
        """unless: checked once the lock is held; when true, nothing is synthesised (None)."""
        voice = self.resolve_voice(voice)
        with self.synth_lock:
            if unless and unless():
                return None
            return self.kokoro.create(text, voice=voice, speed=speed,
                                      lang=LANGS.get(voice[:1], "en-us"))

    def stop(self, session: str = "") -> None:
        """Stop everything: what's playing and what's queued. With a session, only its speech."""
        with self.state_lock:
            if session:
                self._cancel_session(session)
                return
            for job in self.queue:
                job.cancelled = True
            self.queue.clear()
            self._cancel_current()
            self._end_warm()
            self.busy_until = time.time()

    def _cancel_session(self, session: str) -> None:
        """Drop the session's queued speech and stop it if playing; call with state_lock held."""
        for job in self.queue:
            job.cancelled |= job.session == session
        self.queue = [job for job in self.queue if not job.cancelled]
        if self.current and self.current.session == session:
            self._cancel_current()

    def _cancel_current(self) -> None:
        """Call with state_lock held."""
        if self.current:
            self.current.cancelled = True
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()

    def close(self) -> None:
        """Refuse new speech, replays and warm-ups from now on; what is queued still plays."""
        with self.state_lock:
            self.closed = True

    @contextlib.contextmanager
    def synth_request(self):
        """Hold while answering /synth: refused once closed, and counted so watch_idle waits
        for the reply to be written before the server exits."""
        with self.state_lock:
            if self.closed:
                raise Closed
            self.synths += 1
        try:
            yield
        finally:
            with self.state_lock:
                self.synths -= 1

    def warm(self) -> None:
        with self.state_lock:
            if self.closed:
                raise Closed
            if (not self.player or self.current or self.queue
                    or any(p and p.poll() is None for p in (self.proc, self.warm_proc))):
                return
            proc = self.warm_proc = self._spawn(self.silence)
        threading.Thread(target=self._reap, args=(proc,), daemon=True).start()

    def _end_warm(self) -> None:
        if self.warm_proc and self.warm_proc.poll() is None:
            self.warm_proc.terminate()

    def _spawn(self, path: Path | str) -> subprocess.Popen:
        """Start the player; call with state_lock held."""
        now = time.time()
        if self.playing == 0 and now - self.quiet_since > STAY_AWAKE:
            self.awake_since = now
        self.playing += 1
        return subprocess.Popen(self.player + [str(path)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _reap(self, proc: subprocess.Popen) -> None:
        proc.wait()
        with self.state_lock:
            self.playing -= 1
            if self.playing == 0:
                self.quiet_since = time.time()

    def lead_in(self) -> float:
        """Silence to put before speech so the output has been awake for LEAD_IN."""
        with self.state_lock:
            now = time.time()
            awake = self.playing > 0 or now - self.quiet_since <= STAY_AWAKE
            woke = now - self.awake_since if awake else 0.0
        return max(MIN_LEAD_IN, LEAD_IN - woke)

    def speak(self, text: str, voice: str, speed: float, session: str = "", label: str = "",
              priority=None, at=None) -> None:
        # Read before anything changes: a request that fails here cancels nothing.
        # priority is the client's request; any process that can reach the socket (the user's) may ask.
        lane = PRIORITIES.get(priority, NORMAL) if isinstance(priority, str) else NORMAL
        with self.state_lock:
            if self.closed:
                raise Closed
            now = time.time()
            asked_at = hook_time(at, now)
            if lane == LOW and any(j.session == session and j.priority < LOW and not j.cancelled
                                   for j in self.queue + [self.current] if j):
                return  # a status line never replaces this session's question or reply
            others = any(s != session and now - seen < OTHERS_ACTIVE for s, seen in self.last_seen.items())
            if session:
                self.last_seen[session] = now
            if label and others:
                text = f"{re.sub(r'[-_.]+', ' ', label)}: {text}"
            self._cancel_session(session)
            job = Job(session, text, voice, speed, priority=lane, at=asked_at)
            self._enqueue(job)
            self._preempt_for(job)
            self.busy_until = now + 3600
            self.wake.notify()

    def _enqueue(self, job: Job, front: bool = False) -> None:
        """Queue at the end of the job's lane, or its start with front; call with state_lock held."""
        at = next((i for i, j in enumerate(self.queue)
                   if j.priority > job.priority or (front and j.priority == job.priority)),
                  len(self.queue))
        self.queue.insert(at, job)

    def _preempt_for(self, job: Job) -> None:
        """Make way for another session's speech in a higher lane; call with state_lock held.

        A status line is cut at once and dropped; a reply stops at its next chunk boundary
        and resumes after (_run). Questions and replays are never preempted.
        """
        cur = self.current
        if not cur or cur.cancelled or cur.session == job.session or cur.priority <= job.priority:
            return
        if cur.priority == LOW:
            self._cancel_current()
        else:
            cur.preempt = True
            if self.queue and self.queue[0] is job and job.prefetched is None:
                job.prefetched = threading.Event()
                if self.prefetcher:  # one worker at a time: it takes the newest question next
                    if self.prefetch_next:
                        self.prefetch_next.prefetched.set()  # replaced before its turn
                    self.prefetch_next = job
                    return
                try:
                    self.prefetcher = threading.Thread(target=self._prefetch, args=(job,), daemon=True)
                    self.prefetcher.start()
                except RuntimeError as exc:  # can't start a thread: the job makes chunk 1 itself
                    log(f"prefetch not started: {exc}")
                    self.prefetcher = None
                    job.prefetched.set()

    def _prefetch(self, job: Job | None) -> None:
        """Make a job's first chunk while the reply it preempts finishes its chunk, so it
        starts right at the boundary instead of after its own synthesis. Then the next job
        handed over by _preempt_for, until there is none."""
        while job:
            try:
                chunks = split_chunks(job.text)
                if chunks and not job.cancelled:
                    # A question replaced while this waited for the lock is not synthesised.
                    made = self.synth(chunks[0], job.voice, job.speed, unless=lambda: job.cancelled)
                    with self.state_lock:
                        if made and not job.cancelled and job.clip is None:
                            job.clip = Clip([made[0]], made[1], time.time())
            except Exception as exc:  # the job then synthesises chunk 1 itself
                log(f"prefetch failed: {exc}")
            finally:
                job.prefetched.set()
            with self.state_lock:
                job, self.prefetch_next = self.prefetch_next, None
                if job is None:
                    self.prefetcher = None

    @staticmethod
    def _resumed(job: Job) -> Job:
        """The rest of a preempted job: chunks made but not yet played are reused."""
        rest = Job(job.session, job.text, job.voice, job.speed, priority=job.priority, at=job.at,
                   clip=Clip(list(job.made), job.rate, time.time()), played=job.played)
        rest.made = rest.clip.chunks[:job.played]  # whole once the rest is made, for /replay
        return rest

    def replay(self, session: str = "") -> bool:
        """Play the last thing said again, ahead of the queue. False when there is nothing.

        Speech still playing is the last thing said (unless another session is asked for): it
        restarts from the top, reusing the chunks already made and synthesising only the rest.
        Otherwise the session's stored utterance plays (default: the most recent).
        It interrupts what is playing; queued speech plays after it.
        """
        with self.state_lock:
            if self.closed:
                raise Closed
            queued = next((j for j in self.queue if j.replay), None)
            if queued and session in ("", queued.session):
                return True  # a double tap: the replay already queued plays once
            self.queue = [j for j in self.queue if not j.replay]  # another session was asked for
            now, cur = time.time(), self.current
            if cur and cur.replay and not cur.cancelled and session in ("", cur.session) \
                    and now - cur.started < DOUBLE_TAP:
                return True  # a double tap: the replay that just started keeps playing
            # A cancelled current job was stopped or superseded; it is only finishing up.
            if cur and not cur.cancelled and session in ("", cur.session):
                done = max(cur.clip.chunks if cur.clip else [], list(cur.made), key=len)
                rate = cur.rate or (cur.clip.rate if cur.clip else 0)
                job = Job(cur.session, cur.text, cur.voice, cur.speed,
                          clip=Clip(done, rate, now), replay=True, priority=REPLAY_PRIORITY)
            else:
                key = session or self.last_clip
                clip = self.clips.get(key)
                if not clip or now - clip.stored_at >= REPLAY_KEEP:
                    return False
                job = Job(key, "", "", 1.0, clip=clip, replay=True, priority=REPLAY_PRIORITY)
            self._cancel_current()
            self.queue.insert(0, job)
            self.busy_until = now + 3600
            self.wake.notify()
            return True

    def _remember(self, job: Job, chunks: list, rate: int) -> None:
        """Keep an utterance for /replay once all its chunks are made, even if it is then stopped.

        Speech stopped before all its chunks were made is not kept. A replay is kept like any
        other speech: it is the same audio, now the last thing said.
        """
        whole = job.chunk_count() or (len(job.clip.chunks) if job.clip else 0)
        if not chunks or len(chunks) < whole:
            return
        with self.state_lock:
            now = time.time()
            self.clips = {s: c for s, c in self.clips.items() if now - c.stored_at < REPLAY_KEEP}
            self.clips[job.session] = Clip(list(chunks), rate, now)
            self.last_clip = job.session
            while len(self.clips) > REPLAY_SESSIONS:
                del self.clips[min(self.clips, key=lambda s: self.clips[s].stored_at)]

    def _audio(self, job: Job):
        """Yield (samples, rate) per chunk after the ones played (a resume): chunks already
        made (a replay or resume), then synthesis of the rest."""
        if job.prefetched:
            job.prefetched.wait()  # its first chunk is being made; don't synthesise it twice
        done = job.clip.chunks if job.clip else []
        for samples in done[job.played:]:
            yield samples, job.clip.rate
        for chunk in split_chunks(job.text)[max(len(done), job.played):]:
            if job.cancelled or job.preempt:  # preempt: free the synth lock for the speech waiting
                return
            yield self.synth(chunk, job.voice, job.speed)

    def _next(self) -> Job:
        """Wait for the next job, dropping stale status lines; call with state_lock held."""
        while True:
            while not self.queue:
                self.wake.wait()
            job = self.queue.pop(0)
            if job.priority == LOW and time.time() - job.at > STALE_LOW:
                log(f"dropped a stale status line {job.session[:8] or '-'}")
                if not self.queue:
                    self.busy_until = time.time()  # else /health stays busy and blocks interjections
                continue
            return job

    def _loop(self) -> None:
        while True:
            with self.state_lock:
                job = self._next()
                self.current = job
                job.started = time.time()
            try:
                self._run(job)
            finally:
                with self.state_lock:
                    self.current = None
                    if not self.queue:
                        self.busy_until = time.time()

    def _run(self, job: Job) -> None:
        if not self.player:
            log("no audio player found (tried afplay, pw-play, paplay, aplay, ffplay)")
            return
        clips: queue.Queue = queue.Queue(maxsize=2)

        def produce():
            try:
                for i, (samples, rate) in enumerate(self._audio(job)):
                    if job.cancelled:
                        break
                    job.rate = rate  # before the append: replay() reads made, then rate
                    job.made.append(samples)
                    # Stored as soon as the last chunk is made, before a put that may wait.
                    self._remember(job, job.made, job.rate)
                    if i == 0:
                        lead = np.zeros(int(self.lead_in() * rate), samples.dtype)
                        samples = np.concatenate([lead, samples])
                    fd, path = tempfile.mkstemp(prefix="claude-speak-", suffix=".wav")
                    with os.fdopen(fd, "wb") as fh:
                        fh.write(wav_bytes(samples, rate))
                    clips.put(path)
            except Exception as exc:
                log(f"synthesis failed: {exc}")
            finally:
                clips.put(None)

        def drain():
            while (path := clips.get()) is not None:
                os.unlink(path)

        threading.Thread(target=produce, daemon=True).start()
        while True:
            try:
                path = clips.get(timeout=0.05)
            except queue.Empty:
                if job.cancelled or job.preempt:
                    break
                continue
            if path is None:
                # The producer stops early when preempted (_audio); chunks left unplayed resume.
                if job.preempt and job.played < job.chunk_count():
                    clips.put(None)  # put the end back: drain() below waits for it
                    break
                return
            try:
                with self.state_lock:
                    if job.cancelled or job.preempt:  # preempt: here, between two chunks
                        break
                    self._end_warm()
                    proc = self.proc = self._spawn(path)
                self._reap(proc)
                job.played += 1
            finally:
                os.unlink(path)
        with self.state_lock:
            if job.preempt and not job.cancelled:
                self._enqueue(self._resumed(job), front=True)
            job.cancelled = True  # the producer stops; a resume synthesises what is missing
        # Cancelled or preempted: don't wait for the chunk being synthesised, so the next job
        # (a replay, a newer reply, a question) starts now; the producer's leftovers are
        # deleted in the background.
        threading.Thread(target=drain, daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    server: "Server"

    def log_message(self, *_):  # unix sockets have no client address to log
        pass

    def _json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        self.server.touch()
        if self.path == "/health":
            speaker = self.server.speaker
            self._json(200, {"ok": True, "model": self.server.model_name,
                             "player": " ".join(speaker.player or ["none"]),
                             "voices": sorted(speaker.voices),
                             "busy": time.time() < speaker.busy_until,
                             "version": VERSION,
                             "quitting": self.server.quit.is_set() or speaker.closed})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        self.server.touch()
        speaker = self.server.speaker
        try:
            body = self._body()
            text = str(body.get("text", "")).strip()
            voice = str(body.get("voice") or "af_heart")
            speed = min(2.0, max(0.5, float(body.get("speed") or 1.0)))
            if self.path == "/quit":
                if not self.server.quit.is_set():
                    log("quitting for a newer version once nothing is queued or playing")
                speaker.close()  # a chatty old client must not keep a quitting server alive
                self.server.quit.set()
                self._json(202, {"ok": True})
            elif self.path == "/stop":
                speaker.stop(str(body.get("session") or ""))
                self._json(200, {"ok": True})
            elif self.path == "/replay":
                if speaker.replay(str(body.get("session") or "")):
                    self._json(200, {"ok": True})
                else:
                    self._json(404, {"error": "nothing to replay"})
            elif self.path == "/warm":
                speaker.warm()
                self._json(202, {"ok": True})
            elif self.path == "/speak" and text:
                session = str(body.get("session") or "")
                log(f"speak [{voice} x{speed}] {session[:8] or '-'}: {text[:100]!r}{'...' if len(text) > 100 else ''}")
                speaker.speak(text, voice, speed, session, str(body.get("label") or ""),
                              body.get("priority"), body.get("at"))
                self._json(202, {"ok": True})
            elif self.path == "/synth" and text:
                with speaker.synth_request():
                    samples, rate = speaker.synth(text, voice, speed)
                    payload = wav_bytes(samples, rate)
                    self.send_response(200)
                    self.send_header("Content-Type", "audio/wav")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
            else:
                self._json(400, {"error": "expected /speak or /synth with text, /warm, /stop, /replay or /quit"})
        except Closed:
            log(f"refused {self.path}: quitting")
            self._json(503, {"error": "quitting"})
        except Exception as exc:
            self._json(500, {"error": str(exc)})


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, path: str, speaker: Speaker, model_name: str):
        self.speaker = speaker
        self.model_name = model_name
        self.last_used = time.time()
        self.quit = threading.Event()  # set by /quit
        # Only this user may connect (the socket can land in a shared /tmp). Set at bind, so
        # there is no window; nothing else runs yet that could be affected by the umask.
        old_umask = os.umask(0o177)
        try:
            super().__init__(path, Handler)
        finally:
            os.umask(old_umask)

    def touch(self) -> None:
        self.last_used = time.time()


def watch_dictation(path: Path, stop, interval: float = 0.1) -> None:
    """Call stop() each time the dictation state turns from idle to anything else.

    Exact names of the busy states are not relied on; a missing file reads as idle.
    An empty read is a write caught halfway, so it changes nothing.
    """
    was_idle = True
    while True:
        try:
            state = path.read_text().strip()
        except OSError:
            state = "idle"
        if state:
            idle = state == "idle"
            if was_idle and not idle:
                stop()
            was_idle = idle
        time.sleep(interval)


def watch_idle(server: Server, speaker: Speaker, idle_timeout: float,
               tick: float = 15, drain_tick: float = 0.2, drain_cap: float = DRAIN_CAP) -> None:
    """Shut the server down once nothing is queued, playing or being sent by /synth and either
    /quit was asked or no request came for idle_timeout seconds. /quit wakes it at once, not at
    the next tick; a drain longer than drain_cap stops the speech and exits anyway.

    /quit closes the speaker first. On an idle exit the decision and speaker.closed are set
    under state_lock, so a /speak racing the exit either lands before it (and keeps the server
    busy) or is refused, never accepted and lost."""
    quit_at = None
    while True:
        quitting = server.quit.wait(tick)
        if quitting and quit_at is None:
            quit_at = time.time()
        overran = quitting and time.time() - quit_at > drain_cap
        if overran:
            log(f"still draining after {drain_cap:.0f} s; stopping speech")
            speaker.stop()
        with speaker.state_lock:
            now = time.time()
            exiting = overran or (now > speaker.busy_until and not speaker.synths
                                  and (quitting or now - server.last_used > idle_timeout))
            if exiting:
                speaker.closed = True
        if exiting:
            log("quit for a newer version; exiting" if quitting else "idle; exiting")
            server.shutdown()
            return
        if quitting:
            time.sleep(drain_tick)


def remove_socket(path: Path, inode: int) -> None:
    """Remove the socket only if it is still ours: a newer server may already have bound the
    same path while this one was exiting."""
    with contextlib.suppress(OSError):
        if path.stat().st_ino == inode:
            path.unlink()


def socket_in_use(path: Path) -> bool:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(str(path))
        return True
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--model", default=os.environ.get("CLAUDE_SPEAK_MODEL", "fp32"), choices=MODELS)
    parser.add_argument("--idle-timeout", type=float,
                        default=float(os.environ.get("CLAUDE_SPEAK_IDLE_TIMEOUT", 1800)),
                        help="seconds without requests before the server exits")
    args = parser.parse_args()

    data = Path(args.data_dir).expanduser()
    sock = Path(args.socket)
    if socket_in_use(sock):
        log("already running")
        return
    sock.unlink(missing_ok=True)

    models = data / "models"
    models.mkdir(parents=True, exist_ok=True)
    model_file = download(MODELS[args.model], models)
    voices_file = download(VOICES_FILE, models)

    started = time.time()
    kokoro = Kokoro(str(model_file), str(voices_file))
    silence = data / "silence.wav"
    silence.write_bytes(wav_bytes(np.zeros(WARM_SECS * 24000, np.float32), 24000))
    speaker = Speaker(kokoro, find_player(), silence)
    speaker.synth("Ready.", "af_heart", 1.0)  # warm up before accepting requests
    log(f"loaded {MODELS[args.model]} in {time.time() - started:.1f}s; "
        f"player: {' '.join(speaker.player or ['none'])}")

    server = Server(str(sock), speaker, MODELS[args.model])
    inode = sock.stat().st_ino

    threading.Thread(target=watch_idle, args=(server, speaker, args.idle_timeout), daemon=True).start()
    dictation = Path(DICTATION_STATE)
    if dictation.is_file():
        threading.Thread(target=watch_dictation, args=(dictation, speaker.stop), daemon=True).start()
        log(f"watching dictation state {dictation}")
    log(f"listening on {sock}; version {VERSION or 'unknown'}")
    try:
        server.serve_forever()
    finally:
        server.server_close()
        remove_socket(sock, inode)


if __name__ == "__main__":
    sys.exit(main())
