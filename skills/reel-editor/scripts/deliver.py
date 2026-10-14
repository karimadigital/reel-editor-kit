#!/usr/bin/env python3
"""Send a finished reel to your phone through iCloud Drive: no AirDrop, no cables.

Copies the 720p phone copy plus plain-text captions into
  <readyDir>/<YYYY-MM-DD Ddd> - <Theme> - <Title>/
      <Title> reel.mp4
      Instagram caption.txt
      Threads caption.txt            (only if the project has one)
On the iPhone: Files > iCloud Drive > Ready to Post > that folder. Open the video, Share > Save Video, then copy
the caption.

Captions come from the project's caption.md, sections headed "## Instagram" and "## Threads" (markdown stripped).
Copies, never moves: the project keeps its renders.

Usage:  python3 deliver.py <project> --date 2026-10-15 --title "Advisory Lounge" [--theme Events]
                           [--video renders/x-v3-phone.mp4] [--ready-dir <folder>]
        --video defaults to the newest renders/*-phone.mp4
        --ready-dir defaults to readyDir in ../config.json, else iCloud Drive/Ready to Post
"""
import datetime
import glob
import json
import os
import re
import shutil
import sys

ICLOUD = '~/Library/Mobile Documents/com~apple~CloudDocs'


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def plain(md):
    md = re.sub(r'\*\*(.+?)\*\*|__(.+?)__', lambda m: m.group(1) or m.group(2), md)
    md = re.sub(r'(?<!\w)[*_](.+?)[*_](?!\w)', r'\1', md)
    md = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1 \2', md)
    md = re.sub(r'^#+\s*', '', md, flags=re.M)
    return md.strip() + '\n'


def sections(path):
    if not os.path.exists(path):
        return {}
    out, cur = {}, None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m:
            cur = m.group(1).lower()
            out[cur] = ''
        elif cur:
            out[cur] += line
    return out


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith('--'):
        sys.exit(__doc__)
    proj = os.path.expanduser(sys.argv[1])
    date, title = opt('--date'), opt('--title')
    if not date or not title:
        sys.exit('--date YYYY-MM-DD and --title are required (ask which day this posts)')
    day = datetime.date.fromisoformat(date).strftime('%a')
    theme = opt('--theme')
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    cfg = json.load(open(cfg_path, encoding='utf-8')) if os.path.exists(cfg_path) else {}
    ready = os.path.expanduser(opt('--ready-dir') or cfg.get('readyDir') or os.path.join(ICLOUD, 'Ready to Post'))
    if not os.path.isdir(os.path.dirname(ready.rstrip('/'))):
        sys.exit(f'{os.path.dirname(ready)} not found: is iCloud Drive turned on for this Mac? '
                 '(System Settings > your name > iCloud > iCloud Drive)')

    video = opt('--video')
    if video:
        video = os.path.join(proj, video) if not os.path.isabs(video) else video
    else:
        phones = sorted(glob.glob(os.path.join(proj, 'renders', '*-phone.mp4')), key=os.path.getmtime)
        if not phones:
            sys.exit('no renders/*-phone.mp4 yet: run check_cuts.py with --phone on the final render')
        video = phones[-1]

    name = ' - '.join(x for x in (f'{date} {day}', theme, title) if x)
    dst = os.path.join(ready, name)
    os.makedirs(dst, exist_ok=True)
    shutil.copy2(video, os.path.join(dst, f'{title} reel.mp4'))
    caps = sections(os.path.join(proj, 'caption.md'))
    wrote = []
    for key, label in (('instagram', 'Instagram caption'), ('instagram (short)', 'Instagram caption (short)'),
                       ('threads', 'Threads caption')):
        if caps.get(key, '').strip():
            open(os.path.join(dst, f'{label}.txt'), 'w', encoding='utf-8').write(plain(caps[key]))
            wrote.append(label)
    print(f'DELIVERED {os.path.basename(video)} + {", ".join(wrote) or "no captions (caption.md missing)"}')
    print(f'On your phone: Files > iCloud Drive > {os.path.basename(ready)} > {name}')


if __name__ == '__main__':
    main()
