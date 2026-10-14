# Lessons from real iPhone footage

Every trap here was hit at least once on a real edit. Read before ingesting.

## Filming
- **Turn HDR off on the iPhone:** Settings > Camera > Record Video > HDR Video off, and record 4K at 30 fps.
  HDR clips still work (`prep_iphone.py` converts them), but the conversion takes minutes per clip.
- 4K gives room to punch in. A 1080p source only holds about a 1.18-1.28x punch-in before it gets soft.

## iPhone files
- iPhone 4K .MOV is stored sideways (3840x2160 plus a -90 rotation tag). Cropped as-is, punch-ins land in the
  wrong place. `prep_iphone.py` writes an upright copy.
- HDR (HLG) cut straight to 8-bit looks washed out, and the HyperFrames render then asks for ~30 GB of HDR scratch
  and fails on a full disk. `prep_iphone.py` tone-maps to SDR with macOS `avconvert` (most Homebrew ffmpeg builds
  have no `zscale`, so ffmpeg cannot do this well).
- Re-run the cutout after any re-assemble.

## Framing
- Selfie-mode framing is close: eyes sit around y 780-920 and the chin around y 1130-1300 on a 1080x1920 frame.
  Tenfold's default chest-band captions then cover the face. Put caption stacks in the top band, use the
  behind-head slot for one punch word at a time, and keep orbit effects as a halo around the head.
- Check `headpos.py` output per segment before placing behind-head words. If the speaker leans in, use the highest
  head top in that segment so the word stays readable.

## Word timing (local Whisper)
- Whisper word starts run late on words the speaker stretches ("Iii am") or opens with a tongue click ("So").
  `tighten_edl.py` snaps edges to the real voice; still energy-check every segment head before assembling.
- Whisper mishears names, brands and event names. Pass them in the `transcribe_cut.py` prompt and still fix captions
  by hand. Use the official spelling of an event on screen even when the speaker shortens it.
- Word ends run into silence. Trim to the end of the voice plus ~0.1s of natural decay, not to Whisper's end time.

## Machine
- A HyperFrames render needs ~7 GB of temporary space (`$TMPDIR/hyperframes-extract-cache-*`). Check free disk
  before rendering; on a nearly full Mac add `--low-memory-mode` and watch disk while it runs.
- One heavy job at a time. A cutout started while another render is running ran out of memory and stalled at
  frame 8. Wait for the other process to exit.

## Taste defaults that held up
- Talking-head reels around 60 seconds. Trim the middle; keep hook, personality, spoken call to action, closing.
- Captions move around: some in the top band, some behind the head. Not every word in the same place.
- Natural, clean cuts with a punch in or out on every jump so a trimmed pause never reads as a glitch.
- Proper capitalization on title cards.
- Small notes get small changes. A one-image swap should never turn into a rebuild.
