#!/usr/bin/env python3
"""Tighten edl.json heads and tails to the real speech energy, so cuts land on the voice, not on Whisper's guess.

Whisper word times can be 0.1-0.3s off: word ends run into silence, and word STARTS run late when the speaker
stretches a word ("Iii am") or clicks her tongue first. This reads each take's audio (work/<clip>.wav, written by
ingest.py), finds where speech actually is, and moves every segment edge onto it:

  tail: last loud moment inside the segment + 0.12s of natural decay (never later than the old out)
  head: skips leading silence longer than 0.15s (never earlier than the old in)
  never overlaps the previous segment when both come from the same take

Run after you write edl.json and before assemble.py. It prints every edge it moved and the new runtime.
--check only reports. Anything that looks wrong: listen to that join and hand-set in/out in edl.json.

Usage:  python3 tighten_edl.py <project> [--check] [--floor 34]
        --floor: dB below the take's loudest moment that still counts as speech (default 34; raise it for a
                 noisy room, lower it if quiet word endings get clipped)
"""
import array
import json
import math
import os
import sys
import wave


def energy(wav_path):
    wf = wave.open(wav_path)
    sr, ch = wf.getframerate(), wf.getnchannels()
    a = array.array('h', wf.readframes(wf.getnframes()))
    if ch > 1:
        a = a[::ch]
    hop = sr // 100  # 10ms windows
    return [10 * math.log10(sum(x * x for x in a[k:k + hop]) / hop / 32768 ** 2 + 1e-12)
            for k in range(0, len(a) - hop, hop)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    proj = os.path.expanduser(args[0])
    check = '--check' in sys.argv
    floor = float(sys.argv[sys.argv.index('--floor') + 1]) if '--floor' in sys.argv else 34
    p = os.path.join(proj, 'edl.json')
    edl = json.load(open(p, encoding='utf-8'))
    takes = {}
    for s in edl:
        if s['clip'] not in takes:
            w = os.path.join(proj, 'work', f"{s['clip']}.wav")
            if not os.path.exists(w):
                sys.exit(f'{w} missing: run ingest.py on this project first')
            db = energy(w)
            th = max(db) - floor
            hot = [x > th for x in db]
            # voice = at least 3 of the 5 windows around this 10ms are loud, so a click or breath blip does not count
            takes[s['clip']] = [sum(hot[max(i - 2, 0):i + 3]) >= 3 for i in range(len(hot))]

    for k, s in enumerate(edl):
        voice = takes[s['clip']]

        def loud(t):
            return voice[min(max(int(t * 100), 0), len(voice) - 1)]

        t = s['out']
        while t > s['in'] + .2 and not loud(t):
            t -= .01
        new_out = min(s['out'], round(t + .12, 2))
        h = s['in']
        while h < new_out - .2 and not loud(h):
            h += .01
        new_in = max(s['in'], round(h - .07, 2)) if h - s['in'] > .15 else s['in']
        prev = edl[k - 1] if k else None
        if prev and prev['clip'] == s['clip'] and prev['in'] < new_in < prev['out']:
            new_in = prev['out']
        if round(s['out'] - new_out, 2) or round(new_in - s['in'], 2):
            print(f"  {s.get('id', k)!s:12s} in {s['in']:.2f} -> {new_in:.2f}   out {s['out']:.2f} -> {new_out:.2f}")
        if not check:
            s['in'], s['out'] = new_in, new_out
    total = sum(s['out'] - s['in'] for s in edl)
    if not check:
        json.dump(edl, open(p, 'w', encoding='utf-8'), indent=1)
    print(f"{'would be' if check else 'now'} {total:.1f}s across {len(edl)} segments")


if __name__ == '__main__':
    main()
