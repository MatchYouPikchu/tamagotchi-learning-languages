"""Procedural sound effects using sine wave synthesis."""

import math
import struct
import pygame
from settings import SAMPLE_RATE


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
        self._generate_sounds()

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

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
