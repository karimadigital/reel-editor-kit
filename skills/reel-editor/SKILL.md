---
name: reel-editor
description: "Edits raw phone footage into finished vertical reels the approval-first way: fixes iPhone HDR and sideways clips, proposes the cut before rendering, aims for about 60 seconds, applies your own saved look, tightens every cut to the real voice, and drops the final into iCloud Drive so you post from your phone. Runs on top of Tenfold's /video-edit engine, fully local (no ElevenLabs, no paid transcription). Trigger with /reel-editor or 'edit my reel', 'cut these clips', 'make this a reel', 'send it to my phone'."
---

# /reel-editor

An approval-first layer on top of [@tenfoldmarc](https://instagram.com/tenfoldmarc)'s `/video-edit` engine. Tenfold
does the heavy lifting (take picking, assembly, Whisper word timing, background cutout, HyperFrames render, cut QA).
This skill adds: iPhone footage prep, a plan you approve before anything renders, your own look, energy-checked
cuts, a ~60 second target, and delivery to your phone.

Everything runs on this computer. Transcription is local Whisper (faster-whisper). There is no ElevenLabs step and
no API key to set up.

## Folders

- `SK` = Tenfold's skill folder, `~/.claude/skills/video-edit` (expand `~` to the full home path).
- `RE` = this skill's folder, the one holding this SKILL.md, usually `~/.claude/skills/reel-editor`.
- `PY` and `HF` come from `SK/.platform.json` exactly as Tenfold's SKILL.md explains. Run every Python script in
  this skill with `PY` too.

## Step 0: Before every run

1. `SK/SKILL.md` missing: Tenfold is not installed. Tell the user to paste
   `Install this skill for me: https://github.com/tenfoldmarc/video-edit-skill` into Claude Code, then stop.
2. Read `SK/SKILL.md` completely and follow its Step 0 (first-time setup, or the quick check on later runs) until
   its setup prints READY. Its hard rules all apply here. Then read `SK/references/looks.md`, `layout.md` and
   `gotchas.md` completely, plus `overlays.md` when an animated insert is planned.
3. Read `RE/references/lessons.md` (traps already hit on real iPhone footage) and `RE/references/my-look.md`.
4. `RE/config.json` missing: ask, in one message, and save it (no secrets, ever):
   - Where finished reels should go. Default: iCloud Drive `Ready to Post`
     (`~/Library/Mobile Documents/com~apple~CloudDocs/Ready to Post`). Create the folder if they say yes.
   - Target length for talking-head reels. Default 60 seconds.
   - Whether they want a raw-footage drop folder in iCloud (default `Video Inbox`, with theme subfolders they name).
   ```json
   {"readyDir": "~/Library/Mobile Documents/com~apple~CloudDocs/Ready to Post",
    "inboxDir": "~/Library/Mobile Documents/com~apple~CloudDocs/Video Inbox", "targetSeconds": 60}
   ```
5. `my-look.md` still says `STATUS: EMPTY`: offer the look interview (below) once, or use Tenfold's look from its
   `config.json` and say so.

## The look interview (first run, about 3 minutes)

Ask, one message: two or three reels they love (links or files), one they never want to look like, their fonts
(or "pick for me"), up to three colors, and whether captions should be one word at a time or short phrases.
Fetch the reference reels and look at frames before writing anything (Tenfold's `overlays.md` says how). Then fill
in `RE/references/my-look.md`, show them the filled file, and change `STATUS: EMPTY` to `STATUS: ACTIVE` only
after they say yes. `RE/references/example-looks.md` shows four finished looks as models for the format.

## Workflow

### 1. Find and prep the footage
- Clips: the files they name, else the newest videos in Tenfold's `clipsDir`, else their `inboxDir`.
- A `brief.md` in the clips folder (template: `RE/assets/reel-brief-template.md`) answers questions up front.
- iCloud placeholders: with Optimize Mac Storage on, a phone upload can be a cloud-only stub. Run
  `brctl download "<file>"` and wait until the real size shows before touching it.
- Never move or edit originals. Prep them:
  ```bash
  PY RE/scripts/prep_iphone.py <clips or folder> --out <projectsDir>/<slug>/source
  ```
  It writes SDR, upright copies (HDR iPhone clips go through macOS `avconvert`) and prints the folder to ingest.

### 2. Ingest
Run Tenfold's ingest on the prepped folder (`PY SK/scripts/ingest.py <project> <project>/source`). Look at
`work/sheets.jpg` and `transcript.txt`. Note where the face sits in the frame (see lessons.md: selfie framing).

### 3. Propose the edit, then WAIT
Post a short plan and stop until they approve it. This is the one place this skill overrides Tenfold, which keeps
going after posting its EDL:
- The edit as a table: section, the line, which take, approximate length.
- Total runtime. Aim for `targetSeconds` from the first draft. Trim the middle, not the ends: cut side
  explanations, repeated asks and "almost there" filler first. Keep the hook, any blooper that gives it
  personality, the spoken call to action, and the closing line.
- The look (from `my-look.md`), where captions sit for this framing, and any behind-head words.
- Any word Whisper may have misheard (names, brands, events) and the spelling you will use on screen.

### 4. Build the EDL and tighten it
Write `edl.json` the Tenfold way, then snap every edge to the real voice:
```bash
PY RE/scripts/tighten_edl.py <project>
```
It prints every edge it moved. Whisper word starts run late on stretched or tongue-click words, so check each
segment head it did NOT move against the waveform too.

### 5. Assemble, transcribe, cut out, build, render
Follow Tenfold steps 4 to 7 exactly, with the look from `my-look.md` in place of the upstream preset (keep
Tenfold's machinery; change fonts, colors, caption treatment and placement). Fix caption spellings by hand from
what was actually said. One render or cutout at a time on this machine (lessons.md).

Show the 720p phone copy and wait for notes. Every round of notes is a re-render; keep every version in `renders/`.

### 6. Captions and delivery
When they say it is final:
1. Write `<project>/caption.md` with `## Instagram` and `## Threads` sections (add `## Instagram (short)` if
   useful), in their voice, with the call to action they actually use. Show it in chat and get a yes.
2. Ask which day it posts and which theme or series it belongs to, then:
   ```bash
   PY RE/scripts/deliver.py <project> --date YYYY-MM-DD --title "<Short Title>" --theme "<Theme>"
   ```
3. Tell them exactly where it is: **Files > iCloud Drive > Ready to Post > <folder>**, then Share > Save Video.

## Small changes

A small note (swap one image, fix a word, move a caption, nudge a cut) is a small change. Edit only that value in
`build.py` or `edl.json` and re-render. Do not rethink the edit, restyle the look or rewrite other sections unless
asked. Say what you changed in one line.

## Boundaries

- Never publish, schedule, upload or post anything. Delivery to their own iCloud is the finish line.
- Never delete or overwrite their footage. Copies only.
- Never call a render finished before Tenfold's cut check and the audio check pass.
- Credit other creators on screen whenever their reels appear.
- Record what they keep, reject or change in `<project>/notes.md`. Promote a note into `my-look.md` only when they
  say it should apply to every reel.

---
Engine by [@tenfoldmarc](https://instagram.com/tenfoldmarc). Approval layer by
[@karima.digital](https://instagram.com/karima.digital).
