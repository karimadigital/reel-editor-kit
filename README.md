# Reel Editor Kit

Film on your phone. Tell Claude "edit my reel." Get a finished, captioned vertical video in your iPhone's Files app,
ready to post.

This kit is the video editing setup Karima ([@karima.digital](https://instagram.com/karima.digital)) uses for her
talking-head reels. It runs on your Mac inside Claude Code, and it costs nothing beyond your Claude plan: no
ElevenLabs, no editing app, no paid transcription.

## How it works

Two pieces work together:

1. **The engine: [Tenfold's `/video-edit`](https://github.com/tenfoldmarc/video-edit-skill)** by
   [@tenfoldmarc](https://instagram.com/tenfoldmarc). It picks your best take of every line, cuts dead air,
   transcribes on your computer with Whisper, cuts you out of the background so words can sit behind your head,
   renders the reel, and checks every cut. It installs from its own repo, so you always get Marc's latest version.
2. **The add-on: `/reel-editor` (this repo).** The way Karima actually runs the engine:
   - Fixes iPhone clips first (HDR and sideways 4K files that otherwise render washed out or crop wrong).
   - Shows you the plan (which lines, which takes, how long, which look) and **waits for your yes** before rendering.
   - Aims for about 60 seconds by trimming the middle, never the hook or your call to action.
   - Uses **your** look, which it sets up with you on the first run.
   - Snaps every cut to your real voice, so no clipped words and no dead air.
   - Puts the finished reel and plain-text captions in **iCloud Drive > Ready to Post** so you post from your phone.
   - Treats small notes as small changes: swapping one word doesn't rebuild the whole video.

## What you need

- A Mac (Apple Silicon is fastest) with iCloud Drive turned on.
- [Claude Code](https://claude.com/claude-code): the Code tab in the Claude desktop app works.
- About 10 GB of free disk space for rendering.
- ffmpeg, Node.js and Python. You don't need to install these first: on the first run the engine checks your Mac
  and gives you the exact line to paste for anything missing.

## Install (about 5 minutes)

Open Claude Code and paste this message:

```
Install these two Claude Code skills for me:
1. https://github.com/tenfoldmarc/video-edit-skill into ~/.claude/skills/video-edit
2. The skills/reel-editor folder from https://github.com/karimadigital/reel-editor-kit into ~/.claude/skills/reel-editor
Then run /reel-editor so it can finish setup.
```

Prefer the terminal? Run this instead, then open Claude Code and type `/reel-editor`:

```bash
git clone https://github.com/karimadigital/reel-editor-kit.git && bash reel-editor-kit/install.sh
```

The first run asks a few questions (your name, Instagram handle, where clips land, where finished reels go) and
offers a three-minute look interview: show it a few reels you love and it writes your look down so every reel
matches.

## Every reel after that

1. Film your clips. Turn HDR off first: **Settings > Camera > Record Video > HDR Video**, and pick 4K at 30 fps.
   Repeat a line as many times as you like; it keeps the best take.
2. Get the clips onto your Mac (AirDrop to Downloads, or drop them in an iCloud folder).
3. In Claude Code, type `/reel-editor` (or just "edit my reel from the clips in Downloads").
4. Read the plan, say yes or change it.
5. Watch the phone copy, give notes, repeat until you love it.
6. Say it's final, approve the caption, tell it the posting day.
7. On your iPhone: **Files > iCloud Drive > Ready to Post**. Open the video, Share > Save Video, copy the caption,
   post.

Claude never posts anything for you. Your phone is the finish line.

## What's in this repo

```
skills/reel-editor/
  SKILL.md                    the /reel-editor workflow
  references/lessons.md       traps already hit on real iPhone footage
  references/my-look.md       your look (filled in with you on the first run)
  references/example-looks.md four finished looks to borrow from
  assets/reel-brief-template.md   optional brief for a reel
  scripts/prep_iphone.py      HDR and sideways iPhone clips -> clean copies (originals untouched)
  scripts/tighten_edl.py      snaps every cut to the real voice
  scripts/deliver.py          copies the final + captions to iCloud Ready to Post
install.sh                    terminal installer
```

## Updating

Run the install again. The engine updates from Tenfold's repo; your `config.json` and `my-look.md` are kept.

## Credits

- Editing engine: [video-edit-skill](https://github.com/tenfoldmarc/video-edit-skill) by
  [@tenfoldmarc](https://instagram.com/tenfoldmarc). Not included in this repo; installed from its source. Issues
  with the engine itself go to [his repo](https://github.com/tenfoldmarc/video-edit-skill/issues).
- Approval layer, iPhone prep, cut tightening and phone delivery: Karima Williams,
  [karima.digital](https://karima.digital). MIT licensed (see LICENSE); the license covers this repo's files only.
