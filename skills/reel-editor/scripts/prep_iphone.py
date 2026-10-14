#!/usr/bin/env python3
"""Make iPhone clips safe for /video-edit: SDR, upright, originals untouched.

iPhone 4K .MOV files are usually HDR (HLG) and stored sideways (3840x2160 plus a -90 rotation tag). Cut straight,
HDR looks washed out and the HyperFrames render asks for ~30 GB of scratch space; the rotation tag makes the
punch-in crop land in the wrong place. This script writes a fixed copy of each clip that needs it:

  HDR clip        -> macOS `avconvert` tone-maps it to SDR (bt709) and bakes the rotation in
  sideways clip   -> ffmpeg re-encodes it upright (high quality), no rotation tag
  already fine    -> left alone, reported as OK

Copies keep the original's file time, so /video-edit still orders takes oldest to newest.

Usage:  python3 prep_iphone.py <clip or folder> [more ...] [--out <folder>]
        default --out is a "prepped" folder next to the first input
Prints one line per clip, then the folder to pass to ingest.py.
"""
import json
import os
import shutil
import subprocess
import sys

VIDEO = ('.mov', '.mp4', '.m4v')


def probe(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height,color_transfer:stream_side_data=rotation:stream_tags=rotate',
                        '-of', 'json', f], capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)['streams'][0]
    rot = s.get('tags', {}).get('rotate') or next((d['rotation'] for d in s.get('side_data_list', []) if 'rotation' in d), 0)
    return {'hdr': s.get('color_transfer') in ('arib-std-b67', 'smpte2084'),
            'sideways': abs(int(float(rot))) % 180 == 90}


def clips(args):
    for a in args:
        a = os.path.expanduser(a)
        if os.path.isdir(a):
            yield from sorted(os.path.join(a, n) for n in os.listdir(a) if n.lower().endswith(VIDEO) and not n.startswith('.'))
        else:
            yield a


def main():
    argv = sys.argv[1:]
    out = None
    if '--out' in argv:
        k = argv.index('--out')
        out = os.path.expanduser(argv[k + 1])
        del argv[k:k + 2]
    if not argv:
        sys.exit(__doc__)
    files = list(clips(argv))
    if not files:
        sys.exit('no video files found')
    out = out or os.path.join(os.path.dirname(os.path.abspath(files[0])), 'prepped')
    os.makedirs(out, exist_ok=True)
    for f in files:
        p = probe(f)
        dst = os.path.join(out, os.path.splitext(os.path.basename(f))[0] + '.mov')
        if p['hdr']:
            if not shutil.which('avconvert'):
                sys.exit(f'{f}: HDR clip, and avconvert (built into macOS) is missing. On the iPhone turn off '
                         'Settings > Camera > Record Video > HDR Video, then film again.')
            subprocess.run(['avconvert', '-s', f, '-p', 'Preset3840x2160', '-o', dst, '--replace'], check=True,
                           capture_output=True)
            if probe(dst)['hdr']:
                sys.exit(f'{f}: avconvert left this clip HDR. Re-export it from Photos as SDR (or film with HDR Video '
                         'off) and run this again.')
            if probe(dst)['sideways']:  # avconvert normally bakes the rotation; make sure
                tmp = dst + '.upright.mov'
                upright(dst, tmp)
                os.replace(tmp, dst)
            note = 'HDR -> SDR copy'
        elif p['sideways']:
            upright(f, dst)
            note = 'rotated upright copy'
        else:
            # hard link (no extra disk space) so the prepped folder holds every take; copy across drives
            dst = os.path.join(out, os.path.basename(f))
            if os.path.exists(dst):
                os.remove(dst)
            try:
                os.link(f, dst)
            except OSError:
                shutil.copy2(f, dst)
            print(f'OK      {f}  (already SDR and upright)')
            continue
        st = os.stat(f)
        os.utime(dst, (st.st_atime, st.st_mtime))
        print(f'FIXED   {f}  -> {note}: {dst}')
    print(f'READY   ingest this folder: {out}')


def upright(src, dst):
    # ffmpeg applies the rotation tag on decode, so a plain re-encode comes out upright with no tag
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-map', '0:v:0', '-map', '0:a:0?',
                    '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', dst], check=True)


if __name__ == '__main__':
    main()
