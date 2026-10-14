#!/usr/bin/env bash
# Installs Tenfold's /video-edit engine (from its own repo) and the /reel-editor add-on into ~/.claude/skills.
# Safe to re-run: updates both, keeps your config.json and my-look.md.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$HOME/.claude/skills"
ENGINE="$SKILLS/video-edit"
ADDON="$SKILLS/reel-editor"
mkdir -p "$SKILLS"

command -v git >/dev/null || { echo "git is missing: run  xcode-select --install  then try again"; exit 1; }

if [ -d "$ENGINE/.git" ]; then
  echo "Updating the /video-edit engine..."
  git -C "$ENGINE" pull --ff-only
elif [ -e "$ENGINE" ]; then
  echo "$ENGINE already exists (not a git checkout); leaving it as is."
else
  echo "Installing the /video-edit engine by @tenfoldmarc..."
  git clone https://github.com/tenfoldmarc/video-edit-skill.git "$ENGINE"
fi

echo "Installing /reel-editor..."
mkdir -p "$ADDON"
KEEP="$(mktemp -d)"
for f in config.json references/my-look.md; do
  [ -f "$ADDON/$f" ] && mkdir -p "$KEEP/$(dirname "$f")" && cp "$ADDON/$f" "$KEEP/$f"
done
cp -R "$HERE/skills/reel-editor/." "$ADDON/"
cp -R "$KEEP/." "$ADDON/"
rm -rf "$KEEP"

echo
echo "Done. Open Claude Code and type:  /reel-editor"
echo "The first run checks your Mac for ffmpeg, Node and Python and tells you exactly what to paste if anything is missing."
