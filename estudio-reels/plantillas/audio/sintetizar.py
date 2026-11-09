#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Música y efectos ORIGINALES para los reels, sintetizados con numpy + scipy.

- Sin samples, sin grabaciones de terceros y sin IA generativa de música: cada sonido
  sale de osciladores y ruido programados en este archivo. La composición (acordes,
  ritmos, estructura) está escrita acá a mano → derechos limpios para uso comercial.
- Los temas son "loopeables": las colas (reverb, delay, notas largas) que pasan del final
  vuelven al principio, así el reel puede repetirse sin salto.

Uso:
    python3 sintetizar.py                 # escribe en ../remotion/public/audio/
    python3 sintetizar.py otra/carpeta    # o donde digas
"""
import os
import sys
import wave

import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(20261109)  # semilla fija: siempre sale igual


# ----------------------------------------------------------------------------- utilidades
def S(sec):
    return int(round(sec * SR))


def tt(n):
    return np.arange(n) / SR


NOTE_IDX = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
            'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(name):
    """'A3', 'C#4', 'Bb2' → frecuencia en Hz."""
    if name[1] in '#b':
        p, o = name[:2], int(name[2:])
    else:
        p, o = name[0], int(name[1:])
    midi = 12 * (o + 1) + NOTE_IDX[p]
    return 440.0 * 2 ** ((midi - 69) / 12)


def noise(n):
    return RNG.standard_normal(n)


def _sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output='sos')


def lp(x, f, order=2):
    return signal.sosfilt(_sos('lowpass', min(f, SR * 0.45), order), x, axis=0)


def hp(x, f, order=2):
    return signal.sosfilt(_sos('highpass', f, order), x, axis=0)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_sos('bandpass', [lo, min(hi, SR * 0.45)], order), x, axis=0)


def rbj_lowpass(f0, q):
    w0 = 2 * np.pi * f0 / SR
    cw, alpha = np.cos(w0), np.sin(w0) / (2 * q)
    b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
    a = np.array([1 + alpha, -2 * cw, 1 - alpha])
    return np.concatenate([b / a[0], a / a[0]])


def dyn_lp(x, cut, q=0.9, block=128):
    """Filtro pasa-bajos que se mueve en el tiempo (cut = array en Hz, mismo largo que x)."""
    y = np.zeros_like(x)
    zi = np.zeros((1, 2))
    for i in range(0, len(x), block):
        c = float(np.clip(cut[i], 40.0, SR * 0.45))
        sos = rbj_lowpass(c, q)[None, :]
        y[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return y


def fade(y, fin=0.002, fout=0.01):
    n = len(y)
    e = np.ones(n)
    a, b = min(S(fin), n), min(S(fout), n)
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    if b > 0:
        e[-b:] *= np.linspace(1, 0, b)
    return y * (e if y.ndim == 1 else e[:, None])


def norm(y, peak=1.0):
    m = np.max(np.abs(y)) + 1e-12
    return y / m * peak


def to_stereo(sig, pan=0.0):
    if sig.ndim == 2:
        return sig
    l = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    r = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    return np.stack([sig * l, sig * r], axis=1)


class Bus:
    """Pista de mezcla. Con wrap=True lo que sobra al final vuelve al principio (loop)."""

    def __init__(self, dur, wrap=True):
        self.n = S(dur)
        self.x = np.zeros((self.n, 2))
        self.wrap = wrap

    def add(self, sig, t0, gain=1.0, pan=0.0):
        sig = to_stereo(np.asarray(sig, dtype=np.float64), pan) * gain
        n, m = self.n, len(sig)
        i0 = S(t0)
        if self.wrap:
            i0 %= n
            pos = 0
            while pos < m:
                start = (i0 + pos) % n
                take = min(m - pos, n - start)
                self.x[start:start + take] += sig[pos:pos + take]
                pos += take
        elif i0 < n:
            take = min(m, n - i0)
            self.x[i0:i0 + take] += sig[:take]


# ----------------------------------------------------------------------------- osciladores
def osc_saw(f, n, ph0=0.0):
    dt = f / SR
    ph = (ph0 + dt * np.arange(n)) % 1.0
    y = 2.0 * ph - 1.0
    m = ph < dt
    x = ph[m] / dt
    y[m] -= x + x - x * x - 1.0
    m = ph > 1.0 - dt
    x = (ph[m] - 1.0) / dt
    y[m] -= x * x + x + x + 1.0
    return y


def osc_sqr(f, n, duty=0.5):
    return osc_saw(f, n, 0.0) - osc_saw(f, n, duty)


def osc_sin(f, n, ph0=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + ph0)


def sweep_sin(f_arr):
    return np.sin(2 * np.pi * np.cumsum(f_arr) / SR)


def sweep_saw(f_arr):
    ph = (np.cumsum(f_arr) / SR) % 1.0
    return 2 * ph - 1


# ----------------------------------------------------------------------------- batería
def kick(f0=160, f1=48, pdec=0.03, adec=0.18, dur=0.5, click=0.5, drive=2.0):
    n = S(dur)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / pdec)
    body = sweep_sin(f) * np.exp(-t / adec)
    cl = hp(noise(n), 2000) * np.exp(-t / 0.003) * click
    y = np.tanh(drive * (body + cl)) / np.tanh(drive)
    return fade(y, 0.0005, 0.02)


def snare(tone=185, dur=0.4, ndec=0.09, tdec=0.06, lo=1500, hi=9000, mix_tone=0.5):
    n = S(dur)
    t = tt(n)
    body = (osc_sin(tone, n) + 0.5 * osc_sin(tone * 1.47, n)) * np.exp(-t / tdec)
    nz = bp(noise(n), lo, hi) * np.exp(-t / ndec)
    return fade(norm(mix_tone * body + 1.2 * nz), 0.0005, 0.02)


def clap(dur=0.45):
    n = S(dur)
    nz = bp(noise(n), 900, 5000)
    env = np.zeros(n)
    for k, off in enumerate([0, 0.010, 0.021]):
        i = S(off)
        env[i:] = np.maximum(env[i:], np.exp(-tt(n - i) / 0.005) * (0.8 if k < 2 else 1.0))
    i = S(0.021)
    env[i:] = np.maximum(env[i:], np.exp(-tt(n - i) / 0.09) * 0.6)
    return fade(norm(nz * env))


def hat(open_=False, dec=None):
    dur = 0.45 if open_ else 0.08
    dec = dec or (0.11 if open_ else 0.016)
    n = S(dur)
    t = tt(n)
    metal = sum(osc_sqr(f, n) for f in [3240, 4150, 5310, 6520, 7710, 8960]) / 6
    y = hp(0.6 * noise(n) + 0.8 * metal, 7000, order=4) * np.exp(-t / dec)
    return fade(norm(y), 0.0003, 0.01)


def shaker(dur=0.09):
    n = S(dur)
    t = tt(n)
    env = np.minimum(t / 0.012, 1) * np.exp(-np.maximum(t - 0.012, 0) / 0.025)
    return norm(bp(noise(n), 4000, 11000) * env)


def crash(dur=2.2):
    n = S(dur)
    t = tt(n)
    metal = sum(osc_sqr(f, n) for f in [3011, 3937, 4621, 5893, 7127, 8471]) / 6
    y = hp(0.7 * noise(n) + 0.5 * metal, 4000, order=2) * np.exp(-t / 0.55)
    return fade(norm(y), 0.0005, 0.2)


def tom(f=110, dur=0.35):
    n = S(dur)
    t = tt(n)
    y = sweep_sin(f * (1 + 0.6 * np.exp(-t / 0.03))) * np.exp(-t / 0.12)
    return fade(norm(y), 0.0005, 0.02)


# ----------------------------------------------------------------------------- instrumentos
def bass(f, dur, kind='saw', cut0=1600, cut1=180, cdec=0.09, sub=0.7, q=1.1, drive=1.5, rel=0.03):
    n = S(dur)
    t = tt(n)
    o = {'saw': osc_saw, 'sqr': osc_sqr}.get(kind, None)
    o = o(f, n) if o else osc_sin(f, n)
    y = dyn_lp(o, cut1 + (cut0 - cut1) * np.exp(-t / cdec), q=q) + sub * osc_sin(f, n)
    y = np.tanh(drive * y) / np.tanh(drive)
    return fade(y, 0.003, rel)


def sub_bass(f, dur, drive=1.8):
    """Bajo redondo tipo 808/boom-bap."""
    n = S(dur)
    t = tt(n)
    y = osc_sin(f, n) + 0.25 * osc_sin(2 * f, n) * np.exp(-t / 0.08)
    y = np.tanh(drive * y) / np.tanh(drive)
    return fade(y * np.exp(-t / max(dur * 1.5, 0.2)), 0.004, 0.04)


def epiano(f, dur, vel=1.0):
    n = S(dur + 1.0)
    t = tt(n)
    index = 1.8 * np.exp(-t / 0.35) + 0.25
    car = np.sin(2 * np.pi * f * t + index * osc_sin(f, n))
    tine = 0.15 * np.sin(2 * np.pi * f * 14.0 * t) * np.exp(-t / 0.05)
    env = np.exp(-t / 1.6)
    r = S(dur)
    env[r:] *= np.exp(-tt(n - r) / 0.15)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return fade((car + tine) * env * vel * trem, 0.003, 0.02)


def pad(freqs, dur, cutoff=1800, att=0.12, rel=0.3):
    n = S(dur + rel)
    t = tt(n)
    L, R = np.zeros(n), np.zeros(n)
    for f in freqs:
        for v, cents in enumerate([-9, 0, 9]):
            o = osc_saw(f * 2 ** (cents / 1200), n, RNG.random())
            pan = (v - 1) * 0.6
            L += o * np.cos((pan + 1) * np.pi / 4)
            R += o * np.sin((pan + 1) * np.pi / 4)
    env = np.minimum(t / att, 1.0)
    r = S(dur)
    env[r:] *= np.exp(-tt(n - r) / (rel / 4))
    y = lp(np.stack([L, R], axis=1) * env[:, None], cutoff)
    return y / (len(freqs) * 3) * 2.5


def pluck(f, dur=0.25, cut0=6000, cut1=500, cdec=0.07, q=1.0):
    n = S(dur)
    t = tt(n)
    o = 0.6 * osc_saw(f, n) + 0.4 * osc_sqr(f, n)
    y = dyn_lp(o, cut1 + (cut0 - cut1) * np.exp(-t / cdec), q=q) * np.exp(-t / 0.18)
    return fade(y, 0.001, 0.01)


def clav(freqs, dur=0.14):
    n = S(dur)
    t = tt(n)
    y = sum(0.6 * osc_sqr(f, n) + 0.2 * osc_saw(2 * f, n) for f in freqs)
    return fade(bp(y, 500, 3500) * np.exp(-t / 0.06) / len(freqs), 0.001, 0.01)


def brass(freqs, dur=0.35):
    n = S(dur)
    t = tt(n)
    y = sum(osc_saw(f, n, RNG.random()) + osc_saw(f * 1.004, n, RNG.random()) for f in freqs)
    cut = 600 + 2600 * np.minimum(t / 0.03, 1) * np.exp(-t / 0.25)
    y = dyn_lp(y, cut, q=0.8) * np.minimum(t / 0.015, 1)
    return fade(y / len(freqs) / 2, 0.002, 0.04)


def crackle(n, density=14):
    y = np.zeros(n)
    k = RNG.poisson(density * n / SR)
    pos = RNG.integers(0, n, k)
    y[pos] = RNG.uniform(-1, 1, k) * RNG.uniform(0.2, 1, k)
    y = hp(y, 1500)
    hiss = lp(hp(noise(n), 2000), 7000) * 0.02
    return y * 0.35 + hiss


# ----------------------------------------------------------------------------- efectos de mezcla
def reverb(x, wet=0.2, seconds=1.8, bright=6000, wrap=True, seed=3):
    n_ir = S(seconds)
    t = tt(n_ir)
    r = np.random.default_rng(seed)
    env = np.exp(-t / (seconds / 6.9))
    pre = S(0.012)
    out = np.zeros_like(x)
    n = len(x)
    for c in range(2):
        ir = np.zeros(n_ir + pre)
        ir[pre:] = lp(r.standard_normal(n_ir), bright) * env
        ir /= np.sqrt(np.sum(ir ** 2))
        y = signal.fftconvolve(x[:, c], ir)
        full = y[:n].copy()
        if wrap:
            tail = y[n:]
            k = 0
            while k < len(tail):
                seg = tail[k:k + n]
                full[:len(seg)] += seg
                k += n
        out[:, c] = full
    return x + out * wet


def delay(x, time, fb=0.35, wet=0.3, hicut=4500, wrap=True, ping=True):
    d = S(time)
    out = np.zeros_like(x)
    cur = x.copy()
    for k in range(1, 7):
        cur = lp(cur, hicut)
        g = wet * fb ** (k - 1)
        if wrap:
            sh = np.roll(cur, d * k, axis=0)
        else:
            sh = np.zeros_like(cur)
            sh[d * k:] = cur[:-d * k] if d * k < len(cur) else 0
        if ping:
            sh = sh[:, ::-1] if k % 2 else sh
        out += sh * g
    return x + out


def sidechain_env(n, kick_times, depth=0.55, release=0.15):
    g = np.ones(n)
    m = S(release * 5)
    duck = 1 - depth * np.exp(-tt(m) / release)
    a = S(0.004)
    duck[:a] = 1 - depth * np.linspace(0, 1, a)
    for tk in kick_times:
        idx = (S(tk) + np.arange(m)) % n
        g[idx] = np.minimum(g[idx], duck)
    return g


def master(x, peak_db=-1.0, drive=1.35):
    x = hp(x, 28)
    x = norm(x)
    x = np.tanh(drive * x) / np.tanh(drive)
    return norm(x, 10 ** (peak_db / 20))


def write_wav(path, x):
    x = np.clip(to_stereo(np.asarray(x, dtype=np.float64)), -1.0, 1.0)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())
    print(f'  ✓ {os.path.basename(path):34s} {len(x) / SR:6.2f} s')


# ----------------------------------------------------------------------------- estilos (por compás)
def swing_time(step, s16, swing):
    """Tiempo de un semicorchea (0..15) dentro del compás, con swing."""
    return (step // 2) * 2 * s16 + (step % 2) * 2 * s16 * swing


def estilo_electro(dur, bpm, chords, voicings, roots, *, kick_skip=lambda t: False,
                   arp_on=lambda t: True, breakdown=lambda t: False, fills=(), ghost16=lambda t: False):
    """4/4 con bajo en contratiempo, pad y arpegio. Devuelve (drums, bass, music, kicks)."""
    beat = 60 / bpm
    bar = 4 * beat
    drums, bassb, music = Bus(dur), Bus(dur), Bus(dur)
    K, CL, HC, HO = kick(), clap(), hat(), hat(open_=True, dec=0.05)
    kicks = []
    for b, ch in enumerate(chords):
        t0 = b * bar
        root = hz(roots[ch])
        for q in range(4):
            tb = t0 + q * beat
            if kick_skip(tb) or breakdown(tb):
                if breakdown(tb):
                    drums.add(HC, tb + beat / 2, 0.10)
                continue
            drums.add(K, tb, 0.95)
            kicks.append(tb)
            if q in (1, 3):
                drums.add(CL, tb, 0.55)
            drums.add(HO, tb + beat / 2, 0.22)
            if ghost16(tb):
                for s in (1, 3):
                    drums.add(HC, tb + s * beat / 4, 0.10)
            f = root * (2 if q == 3 else 1)
            bassb.add(bass(f, beat * 0.45, cut0=1400, cut1=220), tb + beat / 2, 0.55)
        music.add(pad([hz(nn) for nn in voicings[ch]], bar * 0.98,
                      cutoff=2400 if breakdown(t0 + beat) else 1500), t0, 0.22)
        notes = [hz(nn) * 2 for nn in voicings[ch]]
        seq = [notes[0], notes[1], notes[2], notes[1]] if len(notes) >= 3 else notes * 2
        for s in range(16):
            ts = t0 + s * beat / 4
            if arp_on(ts):
                music.add(pluck(seq[s % len(seq)], 0.2), ts, 0.10 if not breakdown(ts) else 0.13,
                          pan=0.25 if s % 2 else -0.25)
    for (t_start, t_end) in fills:  # redoble de caja (16avos)
        k = 0
        tf = t_start
        SN = snare(tone=200, dur=0.2)
        while tf < t_end - 1e-6:
            prog = (tf - t_start) / max(t_end - t_start, 1e-6)
            drums.add(SN, tf, 0.15 + 0.35 * prog)
            tf += beat / 4
            k += 1
    return drums, bassb, music, kicks


def mezclar(dur, drums, bassb, music, kicks, fx=None, *, wet_music=0.25, wet_drums=0.06,
            sc_depth=0.55, delay_time=None):
    n = S(dur)
    g = sidechain_env(n, kicks, depth=sc_depth)[:, None]
    m = music.x
    if delay_time:
        m = delay(m, delay_time, fb=0.35, wet=0.28)
    m = reverb(m, wet=wet_music, seconds=2.0)
    d = reverb(drums.x, wet=wet_drums, seconds=1.2, bright=8000)
    d = np.tanh(1.3 * d) / np.tanh(1.3)
    mix = d + bassb.x * g + m * g
    if fx is not None:
        mix = mix + fx.x
    return mix


# ----------------------------------------------------------------------------- temas
EL_VOX = {'Am': ['A3', 'C4', 'E4'], 'F': ['A3', 'C4', 'F4'], 'C': ['G3', 'C4', 'E4'], 'G': ['G3', 'B3', 'D4'],
          'Em': ['E3', 'G3', 'B3'], 'C2': ['E3', 'G3', 'C4'], 'G2': ['D3', 'G3', 'B3'], 'D': ['D3', 'F#3', 'A3']}
EL_ROOT = {'Am': 'A1', 'F': 'F1', 'C': 'C2', 'G': 'G1', 'Em': 'E2', 'C2': 'C2', 'G2': 'G1', 'D': 'D2'}


def tema_vendedor():
    """Reel vendedor: 30 s, 120 BPM. 2–5 s 'ahogado' (¿O así?), subida a los 16 s, drop en 18 s,
    momento íntimo 23–25 s ("Te los hago yo"), vuelve en 25 s, empalma con el inicio."""
    bpm, dur = 120, 30.0
    chords = ['Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'G', 'Am', 'F', 'C', 'G', 'F', 'G']
    drums, bassb, music, kicks = estilo_electro(
        dur, bpm, chords, EL_VOX, EL_ROOT,
        kick_skip=lambda t: 17.5 <= t < 18.0,
        arp_on=lambda t: (t >= 5.0 and not (16.0 <= t < 18.0)),
        breakdown=lambda t: 23.0 <= t < 25.0,
        fills=[(16.0, 17.5), (24.5, 25.0)],
        ghost16=lambda t: 18.0 <= t < 23.0)
    fx = Bus(dur)
    r = riser(2.0)
    fx.add(r, 16.0, 0.55)
    fx.add(impacto(), 18.0, 0.75)
    fx.add(crash(), 18.0, 0.35)
    fx.add(crash(), 5.0, 0.18)
    fx.add(riser(1.0), 29.0, 0.25)    # sube hacia el loop
    fx.add(crash(), 0.0, 0.22)        # golpe al arrancar (y en cada vuelta del loop)
    mix = mezclar(dur, drums, bassb, music, kicks, fx, delay_time=0.375)
    # 2–5 s: suena "ahogado", como un video sin editar
    n = len(mix)
    mask = np.zeros(n)
    a, b = S(2.0), S(5.0)
    mask[a:b] = 1
    mask[a:a + S(0.012)] = np.linspace(0, 1, S(0.012))
    mask[b - S(0.04):b] = np.linspace(1, 0, S(0.04))
    muff = lp(mix, 380, order=4) * 1.25
    mix = mix * (1 - mask[:, None]) + muff * mask[:, None] * 0.8
    return master(mix)


def tema_padel():
    """Pádel: 16 s, 120 BPM, Em–C–G–D, electrónica nocturna; redoble al final para el loop."""
    bpm, dur = 120, 16.0
    chords = ['Em', 'C2', 'G2', 'D'] * 2
    drums, bassb, music, kicks = estilo_electro(
        dur, bpm, chords, EL_VOX, EL_ROOT,
        arp_on=lambda t: not (14.0 <= t < 15.0),
        fills=[(15.0, 16.0)],
        ghost16=lambda t: 10.0 <= t < 13.0)
    fx = Bus(dur)
    fx.add(crash(), 0.0, 0.25)
    for tb in np.arange(10.0, 13.0, 0.5):  # tambores en el peloteo
        fx.add(tom(140 if int(tb * 2) % 2 else 100), tb + 0.25, 0.25)
    return master(mezclar(dur, drums, bassb, music, kicks, fx, delay_time=0.375))


def base_electro():
    bpm, dur = 120, 16.0
    chords = ['Am', 'F', 'C', 'G'] * 2
    drums, bassb, music, kicks = estilo_electro(dur, bpm, chords, EL_VOX, EL_ROOT, fills=[(15.5, 16.0)])
    return master(mezclar(dur, drums, bassb, music, kicks, delay_time=0.375))


BB_CH = {'Dm9': (['F3', 'A3', 'C4', 'E4'], 'D2'), 'Bbmaj7': (['D3', 'F3', 'A3', 'C4'], 'Bb1'),
         'Gm9': (['Bb3', 'D4', 'F4', 'A4'], 'G1'), 'A7b9': (['C#4', 'E4', 'G4', 'Bb4'], 'A1'),
         'Cmaj7': (['E3', 'G3', 'B3', 'D4'], 'C2'), 'Am7': (['C4', 'E4', 'G4', 'B4'], 'A1'),
         'Dm7': (['F3', 'A3', 'C4', 'E4'], 'D2'), 'G7': (['F3', 'A3', 'B3', 'E4'], 'G1')}


def estilo_boombap(dur, bpm, bars, *, swing=0.58, soft=False, crackle_gain=0.5):
    """bars: lista de compases; cada compás = lista de (acorde, desde_semicorchea, hasta_semicorchea)."""
    beat = 60 / bpm
    bar = 4 * beat
    s16 = beat / 4
    drums, bassb, music, fx = Bus(dur), Bus(dur), Bus(dur), Bus(dur)
    K = kick(f0=140, f1=50, adec=0.22, drive=2.4) if not soft else lp(kick(f0=120, f1=50, adec=0.2), 2500)
    SN = snare(tone=200, ndec=0.12, mix_tone=0.7) if not soft else lp(snare(tone=190, ndec=0.1), 3500)
    HC = hat(dec=0.02)
    HO = hat(open_=True, dec=0.08)
    kicks = []
    for b, segs in enumerate(bars):
        t0 = b * bar
        kick_steps = [0, 7, 10] + ([15] if b % 2 else [])
        for st in kick_steps:
            ts = t0 + swing_time(st, s16, swing)
            drums.add(K, ts, 0.9 if st == 0 else 0.75)
            kicks.append(ts)
        for st, gn in [(4, 0.8), (12, 0.8), (9, 0.12), (14, 0.1)]:
            drums.add(SN, t0 + swing_time(st, s16, swing), gn * (0.7 if soft else 1))
        for st in range(0, 16, 2):
            drums.add(HC, t0 + swing_time(st, s16, swing), 0.22 if st % 4 == 0 else 0.15)
        for st in (3, 11):
            drums.add(HC, t0 + swing_time(st, s16, swing), 0.08)
        if b % 2 == 1:
            drums.add(HO, t0 + swing_time(14, s16, swing), 0.12)
        for (ch, a, z) in segs:
            vox, root = BB_CH[ch]
            ta = t0 + swing_time(a, s16, swing)
            length = (z - a) * s16
            for k, nn in enumerate(vox):
                music.add(epiano(hz(nn), length * 0.95, vel=0.9), ta + k * 0.012, 0.16,
                          pan=(k - 1.5) * 0.25)
            for st in [s for s in kick_steps if a <= s < z]:
                f = hz(root) * (1.5 if st == 10 else 1)
                bassb.add(sub_bass(f, 3 * s16 if st != 0 else 6 * s16), t0 + swing_time(st, s16, swing), 0.6)
    n = S(dur)
    fx.add(crackle(n), 0.0, crackle_gain)
    return drums, bassb, music, fx, kicks


def tema_barberia():
    """Barbería: 18,67 s, 90 BPM boom-bap; Dm9–Bbmaj7–Gm9–A7(b9)."""
    bpm = 90
    bars = [[('Dm9', 0, 16)], [('Bbmaj7', 0, 16)], [('Gm9', 0, 16)], [('A7b9', 0, 16)],
            [('Dm9', 0, 16)], [('Bbmaj7', 0, 16)], [('Gm9', 0, 8), ('A7b9', 8, 16)]]
    dur = len(bars) * 4 * 60 / bpm
    drums, bassb, music, fx, kicks = estilo_boombap(dur, bpm, bars)
    return master(mezclar(dur, drums, bassb, music, kicks, fx, wet_music=0.3, sc_depth=0.25))


def base_boombap():
    bpm = 90
    bars = [[('Dm9', 0, 16)], [('Bbmaj7', 0, 16)], [('Gm9', 0, 16)], [('A7b9', 0, 16)]] * 2
    dur = len(bars) * 4 * 60 / bpm
    drums, bassb, music, fx, kicks = estilo_boombap(dur, bpm, bars)
    return master(mezclar(dur, drums, bassb, music, kicks, fx, wet_music=0.3, sc_depth=0.25))


def base_suave():
    """Lo-fi tranqui (estética, cafés): 80 BPM, Cmaj7–Am7–Dm7–G7."""
    bpm = 80
    bars = [[('Cmaj7', 0, 16)], [('Am7', 0, 16)], [('Dm7', 0, 16)], [('G7', 0, 16)]] * 2
    dur = len(bars) * 4 * 60 / bpm
    drums, bassb, music, fx, kicks = estilo_boombap(dur, bpm, bars, swing=0.6, soft=True, crackle_gain=0.8)
    mix = mezclar(dur, drums, bassb, music, kicks, fx, wet_music=0.4, sc_depth=0.15)
    return master(lp(mix, 9000))


FK_CH = {'F': (['A3', 'C4', 'E4'], 'F2'), 'Dm': (['F3', 'A3', 'C4'], 'D2'),
         'Gm': (['F3', 'Bb3', 'D4'], 'G2'), 'C7': (['E3', 'G3', 'Bb3'], 'C2')}


def estilo_funk(dur, bpm, bars, swing=0.54):
    beat = 60 / bpm
    bar = 4 * beat
    s16 = beat / 4
    drums, bassb, music = Bus(dur), Bus(dur), Bus(dur)
    K = kick(f0=150, f1=52, adec=0.16)
    SN = snare(tone=210, ndec=0.08, mix_tone=0.6)
    HC = hat(dec=0.012)
    SH = shaker()
    kicks = []
    for b, segs in enumerate(bars):
        t0 = b * bar
        for st in ([0, 3, 8, 10] if b % 2 == 0 else [0, 6, 8, 11]):
            ts = t0 + swing_time(st, s16, swing)
            drums.add(K, ts, 0.85)
            kicks.append(ts)
        for st, gn in [(4, 0.75), (12, 0.75), (7, 0.12), (15, 0.1)]:
            drums.add(SN, t0 + swing_time(st, s16, swing), gn)
        for st in range(16):
            ts = t0 + swing_time(st, s16, swing)
            drums.add(HC, ts, [0.2, 0.07, 0.13, 0.07][st % 4])
            drums.add(SH, ts, 0.05, pan=0.4)
        for (ch, a, z) in segs:
            vox, root = FK_CH[ch]
            r = hz(root)
            for st, mul, ln in [(0, 1, 2), (3, 1, 1), (6, 2, 1), (8, 1, 2), (10, 1.5, 1), (13, 2, 1), (14, 1.78, 2)]:
                if a <= st < z:
                    bassb.add(bass(r * mul, ln * s16 * 0.9, kind='saw', cut0=2200, cut1=300, cdec=0.05,
                                   sub=0.5, q=1.6), t0 + swing_time(st, s16, swing), 0.5)
            for st in [2, 6, 11, 14]:
                if a <= st < z:
                    music.add(clav([hz(nn) for nn in vox]), t0 + swing_time(st, s16, swing), 0.35, pan=-0.2)
            if a == 0 and b % 2 == 0:
                music.add(brass([hz(nn) for nn in vox]), t0, 0.22, pan=0.2)
    return drums, bassb, music, kicks


def tema_resto():
    """Hamburguesería: 16,8 s, 100 BPM funk; F–Dm–Gm–C7."""
    bpm = 100
    bars = [[('F', 0, 16)], [('Dm', 0, 16)], [('Gm', 0, 16)], [('C7', 0, 16)],
            [('F', 0, 16)], [('Dm', 0, 16)], [('Gm', 0, 8), ('C7', 8, 16)]]
    dur = len(bars) * 4 * 60 / bpm
    drums, bassb, music, kicks = estilo_funk(dur, bpm, bars)
    return master(mezclar(dur, drums, bassb, music, kicks, wet_music=0.18, sc_depth=0.3))


def base_funk():
    bpm = 100
    bars = [[('F', 0, 16)], [('Dm', 0, 16)], [('Gm', 0, 16)], [('C7', 0, 16)]] * 2
    dur = len(bars) * 4 * 60 / bpm
    drums, bassb, music, kicks = estilo_funk(dur, bpm, bars)
    return master(mezclar(dur, drums, bassb, music, kicks, wet_music=0.18, sc_depth=0.3))


# ----------------------------------------------------------------------------- efectos (SFX)
def whoosh(dur=0.6, f_lo=300, f_hi=5000):
    n = S(dur)
    t = tt(n)
    p = t / dur
    amp = np.sin(np.pi * p) ** 2
    cut = f_lo * (f_hi / f_lo) ** np.sin(np.pi * p)
    y = dyn_lp(hp(noise(n), 150), cut, q=1.8) * amp
    pan = -0.7 + 1.4 * p
    out = np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], axis=1)
    return norm(fade(out, 0.002, 0.02), 0.9)


def riser(dur=2.0):
    n = S(dur)
    t = tt(n)
    p = t / dur
    nz = dyn_lp(hp(noise(n), 200), 300 + 9000 * p ** 2, q=2.5)
    tone = lp(sweep_saw(200 * 2 ** (2 * p)), 3000) * 0.25
    return norm(fade((0.8 * nz + tone) * p ** 1.8, 0.01, 0.01), 0.9)


def pop(f0=900, f1=320, dur=0.08):
    n = S(dur)
    t = tt(n)
    y = sweep_sin(f1 + (f0 - f1) * np.exp(-t / 0.012)) * np.exp(-t / 0.025)
    y += hp(noise(n), 3000) * np.exp(-t / 0.0015) * 0.3
    return norm(fade(y, 0.0005, 0.01), 0.9)


def bell(f, dur=0.7):
    n = S(dur)
    t = tt(n)
    index = 3 * np.exp(-t / 0.15)
    y = np.sin(2 * np.pi * f * t + index * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t / 0.25)
    return fade(y, 0.001, 0.02)


def ding():
    out = np.zeros(S(0.85))
    a, b = bell(1318.5, 0.5), bell(1975.5, 0.7)
    out[:len(a)] += a * 0.8
    i = S(0.09)
    out[i:i + len(b)] += b[:len(out) - i] * 0.8
    return norm(out, 0.9)


def impacto(dur=1.6):
    n = S(dur)
    t = tt(n)
    boom = sweep_sin(34 + 60 * np.exp(-t / 0.06)) * np.exp(-t / 0.45)
    crack = hp(noise(n), 1200) * np.exp(-t / 0.05) * 0.6
    tail = lp(noise(n), 900) * np.exp(-t / 0.35) * 0.3
    return norm(fade(np.tanh(1.6 * (boom + crack + tail)), 0.0005, 0.05), 0.95)


def golpe():
    k = kick(f0=220, f1=55, adec=0.12, dur=0.35, click=0.9)
    s = snare(tone=180, dur=0.35, ndec=0.06)
    return norm(k + 0.6 * s, 0.95)


def click():
    n = S(0.05)
    t = tt(n)
    y = osc_sin(2400, n) * np.exp(-t / 0.004) + hp(noise(n), 4000) * np.exp(-t / 0.0015) * 0.5
    return norm(fade(y, 0.0002, 0.005), 0.8)


def maquina(dur=2.6):
    n = S(dur)
    t = tt(n)
    motor = osc_saw(118, n) + 0.5 * osc_sqr(236, n)
    am = 0.75 + 0.25 * np.sin(2 * np.pi * 31 * t)
    y = bp(motor * am, 140, 3200) + 0.15 * bp(noise(n), 2000, 7000)
    env = np.minimum(t / 0.08, 1) * np.clip((dur - t) / 0.15, 0, 1)
    return norm(y * env, 0.8)


def brillo(dur=0.7):
    n = S(dur)
    y = np.zeros(n)
    for k, f in enumerate([2637, 3520, 4186, 5274]):
        st = S(0.045 * k)
        y[st:] += osc_sin(f, n - st) * np.exp(-tt(n - st) / 0.12)
    y += hp(noise(n), 6000) * np.exp(-tt(n) / 0.2) * 0.15
    return norm(fade(y, 0.001, 0.05), 0.7)


def womp(dur=0.9):
    n = S(dur)
    t = tt(n)
    o = sweep_saw(233 * 2 ** (-1.2 * t / dur))
    wah = 500 + 1400 * (0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t)) * np.exp(-t / 0.5)
    y = dyn_lp(o, wah, q=3.0) * np.minimum(t / 0.03, 1) * np.exp(-t / 0.6)
    return norm(fade(y, 0.002, 0.05), 0.85)


def plop():
    n = S(0.16)
    t = tt(n)
    y = sweep_sin(140 + 260 * np.exp(-t / 0.02)) * np.exp(-t / 0.05)
    y += lp(noise(n), 800) * np.exp(-t / 0.01) * 0.4
    return norm(fade(y, 0.0005, 0.01), 0.9)


def pelota():
    n = S(0.18)
    t = tt(n)
    y = (0.8 * osc_sin(820, n) + 0.4 * osc_sin(1630, n)) * np.exp(-t / 0.022)
    y += bp(noise(n), 800, 5000) * np.exp(-t / 0.004) * 0.8
    y += lp(noise(n), 400) * np.exp(-t / 0.01) * 0.4
    return norm(fade(y, 0.0003, 0.01), 0.9)


def tick():
    n = S(0.04)
    t = tt(n)
    return norm(fade(osc_sin(1800, n) * np.exp(-t / 0.008), 0.0003, 0.005), 0.6)


# ----------------------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'remotion', 'public', 'audio')
    os.makedirs(out, exist_ok=True)
    print('Música (original, loopeable):')
    for name, fn in [('musica-vendedor.wav', tema_vendedor), ('musica-barberia.wav', tema_barberia),
                     ('musica-resto.wav', tema_resto), ('musica-padel.wav', tema_padel),
                     ('base-energica-120.wav', base_electro), ('base-groove-100.wav', base_funk),
                     ('base-urbana-90.wav', base_boombap), ('base-suave-80.wav', base_suave)]:
        write_wav(os.path.join(out, name), fn())
    print('Efectos:')
    sfx = {'whoosh': whoosh(), 'swipe': whoosh(0.28, 600, 7000), 'subida': riser(2.0),
           'pop': pop(), 'pop-suave': pop(560, 260, 0.07), 'ding': ding(), 'impacto': impacto(),
           'golpe': golpe(), 'click': click(), 'maquina': maquina(), 'brillo': brillo(),
           'womp': womp(), 'plop': plop(), 'pelota': pelota(), 'tick': tick()}
    for k, v in sfx.items():
        write_wav(os.path.join(out, f'sfx-{k}.wav'), v)


if __name__ == '__main__':
    main()
