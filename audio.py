"""Procedural sound effects using sine wave synthesis."""

import math
import struct
import threading
from pathlib import Path
import pygame
from settings import SAMPLE_RATE

SPEECH_DIR = Path(__file__).parent / "assets" / "speech"


def _generate_wave(frequency, duration, volume=0.3, wave_type="sine", fade_out=True):
    """Generate a sound wave as a pygame Sound object."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        if wave_type == "sine":
            val = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "square":
            val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "triangle":
            val = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
        else:
            val = math.sin(2 * math.pi * frequency * t)

        # Fade out
        if fade_out:
            envelope = 1.0 - (i / n_samples)
            val *= envelope

        val *= volume
        val = max(-1.0, min(1.0, val))
        samples.append(int(val * 32767))

    raw = struct.pack(f"<{len(samples)}h", *samples)
    sound = pygame.mixer.Sound(buffer=raw)
    return sound


def _generate_multi_tone(tones, volume=0.3):
    """Generate a sound with multiple frequency/duration segments."""
    all_samples = []
    for freq, duration in tones:
        n_samples = int(SAMPLE_RATE * duration)
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            val = math.sin(2 * math.pi * freq * t)
            envelope = 1.0 - (i / n_samples) * 0.5
            val *= volume * envelope
            val = max(-1.0, min(1.0, val))
            all_samples.append(int(val * 32767))

    raw = struct.pack(f"<{len(all_samples)}h", *all_samples)
    return pygame.mixer.Sound(buffer=raw)


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._speech_ready = {}  # word -> True when MP3 is cached
        self._speech_lock = threading.Lock()
        self._generate_sounds()
        self._start_speech_cache()

    def _generate_sounds(self):
        # Feed sound: happy ascending notes
        self.sounds["feed"] = _generate_multi_tone([
            (440, 0.1), (554, 0.1), (659, 0.15),
        ], volume=0.25)

        # Play sound: bouncy ascending
        self.sounds["play"] = _generate_multi_tone([
            (523, 0.08), (659, 0.08), (784, 0.08), (880, 0.12),
        ], volume=0.25)

        # Clean sound: swoosh-like descending
        self.sounds["clean"] = _generate_multi_tone([
            (800, 0.06), (700, 0.06), (600, 0.06), (500, 0.08),
        ], volume=0.2)

        # Sleep sound: gentle low tone
        self.sounds["sleep"] = _generate_wave(220, 0.4, volume=0.15, wave_type="sine")

        # Wake sound: ascending bright
        self.sounds["wake"] = _generate_multi_tone([
            (330, 0.1), (440, 0.1), (550, 0.12),
        ], volume=0.2)

        # Sick sound: dissonant low
        self.sounds["sick"] = _generate_multi_tone([
            (200, 0.15), (190, 0.15), (180, 0.2),
        ], volume=0.2)

        # Run away sound: sad descending
        self.sounds["runaway"] = _generate_multi_tone([
            (440, 0.2), (370, 0.2), (330, 0.2), (260, 0.3),
        ], volume=0.25)

        # Menu select
        self.sounds["select"] = _generate_wave(660, 0.12, volume=0.2)

        # Button click
        self.sounds["click"] = _generate_wave(880, 0.06, volume=0.15)

        # Mini game: catch treat / click ball
        self.sounds["catch"] = _generate_wave(880, 0.06, volume=0.2)

        # Mini game: pop bubble
        self.sounds["pop"] = _generate_wave(1200, 0.04, volume=0.2)

        # Poop event: low comedic descending tone
        self.sounds["poop"] = _generate_multi_tone([
            (220, 0.12), (180, 0.1),
        ], volume=0.2)

        # Medicine success: bright ascending
        self.sounds["medicine"] = _generate_multi_tone([
            (440, 0.08), (660, 0.08), (880, 0.12),
        ], volume=0.25)

        # Wrong click: dissonant buzz
        self.sounds["wrong"] = _generate_wave(150, 0.1, volume=0.15,
                                               wave_type="square")

        # Edu: correct answer ding
        self.sounds["correct"] = _generate_multi_tone([
            (880, 0.06), (1100, 0.1),
        ], volume=0.25)

        # Edu: incorrect answer buzz
        self.sounds["incorrect"] = _generate_wave(200, 0.12, volume=0.1)

        # Edu: level up fanfare
        self.sounds["level_up"] = _generate_multi_tone([
            (523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.2),
        ], volume=0.3)

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # --- Text-to-Speech via gTTS ---

    def _start_speech_cache(self):
        """Pre-generate TTS MP3 files for all vocabulary words in background."""
        SPEECH_DIR.mkdir(parents=True, exist_ok=True)
        # Mark already-cached words as ready (skip zero-byte failures)
        for mp3 in SPEECH_DIR.glob("*.mp3"):
            if mp3.stat().st_size > 0:
                self._speech_ready[mp3.stem] = True
            else:
                mp3.unlink()  # remove failed download so it retries
        # Generate missing ones in background thread
        thread = threading.Thread(target=self._generate_speech_cache, daemon=True)
        thread.start()

    def _generate_speech_cache(self):
        """Background thread: generate MP3 for each vocab word via gTTS."""
        try:
            from gtts import gTTS
        except ImportError:
            return  # gTTS not installed, skip silently
        try:
            from vocabulary import ALL_VOCAB
        except ImportError:
            return

        # Extra words beyond vocabulary (food/clean names spoken during gameplay)
        EXTRA_SPEECH_WORDS = ["apple", "fish", "cake", "milk",
                              "bath", "brush", "towel"]
        for extra_word in EXTRA_SPEECH_WORDS:
            filepath = SPEECH_DIR / f"{extra_word}.mp3"
            if filepath.exists() and filepath.stat().st_size > 0:
                with self._speech_lock:
                    self._speech_ready[extra_word] = True
                continue
            try:
                tts = gTTS(text=extra_word, lang="en", slow=True)
                tts.save(str(filepath))
                if filepath.stat().st_size > 0:
                    with self._speech_lock:
                        self._speech_ready[extra_word] = True
                else:
                    filepath.unlink(missing_ok=True)
            except Exception:
                pass

        for entry in ALL_VOCAB:
            word = entry[1]  # English word
            filepath = SPEECH_DIR / f"{word}.mp3"
            if filepath.exists() and filepath.stat().st_size > 0:
                with self._speech_lock:
                    self._speech_ready[word] = True
                continue
            try:
                tts = gTTS(text=word, lang="en", slow=True)
                tts.save(str(filepath))
                if filepath.stat().st_size > 0:
                    with self._speech_lock:
                        self._speech_ready[word] = True
                else:
                    filepath.unlink(missing_ok=True)
            except Exception:
                pass  # network error, skip this word

    def speak(self, word):
        """Pronounce an English word using cached gTTS MP3."""
        with self._speech_lock:
            ready = self._speech_ready.get(word, False)
        if not ready:
            return
        filepath = SPEECH_DIR / f"{word}.mp3"
        if not filepath.exists():
            return
        try:
            pygame.mixer.music.load(str(filepath))
            pygame.mixer.music.play()
        except Exception:
            pass
