"""Add (or remove) a playable WebGL build on the site.

Add a version - copies the build into games/<slug>/<version-id>/ and lists it first (= newest)
in games.json. A slug that isn't in games.json yet becomes a new game card.

A non-temporary version goes to games/<slug>/play/ instead, and games.json's "play" names it.
Unity's web player keys its save (PlayerPrefs in IndexedDB) off the build folder's URL, so a
fixed folder for the newest proper version is what lets web progress carry over to the next
one. The version that held play/ before moves out to its own games/<slug>/<id>/ folder:

    python tools/add_build.py prismix path/to/WebGLBuild --id 2026-10-20 --label "0.2 테스트판" \
        --notes "새 스테이지" --temporary

    python tools/add_build.py newgame path/to/build --id 0.1 --label "0.1 첫 프로토타입" \
        --title "New Game" --tagline "한 줄 소개" --temporary

Remove an old version (folder and entry) to keep the site small:

    python tools/add_build.py prismix --remove 2026-10-20

Then commit and push; GitHub Pages republishes in a minute or two. Limits worth knowing:
GitHub rejects files over 100 MB and Pages sites should stay under 1 GB in total, so prune old
temporary versions now and then.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "games.json")
PLAY = "play"  # folder name of the stable URL; never a version id
FILE_LIMIT = 100 * 1024 * 1024
SITE_WARN = 900 * 1024 * 1024


def load():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def folder_size(path):
    total = 0
    for dirpath, _, files in os.walk(path):
        for name in files:
            total += os.path.getsize(os.path.join(dirpath, name))
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="game id used in the URL, e.g. prismix")
    ap.add_argument("build", nargs="?", help="folder with the WebGL build (index.html + Build/)")
    ap.add_argument("--id", help="version folder name, e.g. 2026-10-20 or 0.2 (letters, digits, . - _)")
    ap.add_argument("--label", help="version name shown on the site")
    ap.add_argument("--notes", default="", help="one line about what changed")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--temporary", action="store_true", help="mark as a 임시 (work-in-progress) build")
    ap.add_argument("--replace", action="store_true", help="overwrite an existing version folder")
    ap.add_argument("--title", help="new game only: title")
    ap.add_argument("--tagline", default="", help="new game only: one-line description")
    ap.add_argument("--remove", metavar="ID", help="delete version ID instead of adding one")
    args = ap.parse_args()

    data = load()
    games = data.setdefault("games", [])
    game = next((g for g in games if g["slug"] == args.slug), None)

    if args.remove:
        if game is None:
            sys.exit(f"no game '{args.slug}' in games.json")
        game["versions"] = [v for v in game.get("versions", []) if v["id"] != args.remove]
        folder = args.remove
        if game.get("play") == args.remove:
            folder = PLAY
            del game["play"]
            print(f"note: {args.remove} was on {PLAY}/ - the next proper version you add takes it")
        target = os.path.join(ROOT, "games", args.slug, folder)
        if os.path.isdir(target):
            shutil.rmtree(target)
        save(data)
        print(f"removed {args.slug}/{args.remove}")
        return

    if not args.build or not args.id or not args.label:
        sys.exit("adding a version needs: build folder, --id and --label")
    if not all(c.isalnum() or c in ".-_" for c in args.id):
        sys.exit("--id may only use letters, digits, '.', '-' and '_' (it becomes part of the URL)")
    if args.id == PLAY:
        sys.exit(f"--id '{PLAY}' is the stable URL's folder - pick another id")
    build = os.path.abspath(args.build)
    if not os.path.isfile(os.path.join(build, "index.html")) or not os.path.isdir(os.path.join(build, "Build")):
        sys.exit(f"{build} doesn't look like a WebGL build (needs index.html and Build/)")
    for dirpath, _, files in os.walk(build):
        for name in files:
            if os.path.getsize(os.path.join(dirpath, name)) > FILE_LIMIT:
                sys.exit(f"{name} is over 100 MB - GitHub will reject it")

    if game is None:
        if not args.title:
            sys.exit(f"'{args.slug}' is a new game - add --title (and ideally --tagline)")
        game = {"slug": args.slug, "title": args.title, "tagline": args.tagline, "description": "",
                "status": "개발 중", "platforms": ["PC"], "controls": [], "cover": "", "screenshots": [], "versions": []}
        games.append(game)
        print("new game card added - fill in description, controls, cover and platforms in games.json")

    game_dir = os.path.join(ROOT, "games", args.slug)
    own = os.path.join(game_dir, args.id)
    play = os.path.join(game_dir, PLAY)
    already = os.path.exists(own) or (game.get("play") == args.id and os.path.exists(play))
    if already and not args.replace:
        sys.exit(f"{args.slug}/{args.id} already exists - pick another --id or pass --replace")

    if args.temporary:
        if game.get("play") == args.id:  # a proper version re-added as temporary leaves play/
            shutil.rmtree(play, ignore_errors=True)
            del game["play"]
        target = own
    else:
        old = game.get("play")
        if old and old != args.id and os.path.isdir(play):
            moved = os.path.join(game_dir, old)
            if os.path.exists(moved):
                sys.exit(f"can't move {PLAY}/ out to {old}/ - that folder already exists")
            shutil.move(play, moved)
            print(f"moved {old} from {PLAY}/ to {old}/")
        game["play"] = args.id
        target = play
    for stale in (own, play) if target == play else (own,):
        if os.path.exists(stale):
            shutil.rmtree(stale)
    shutil.copytree(build, target)

    versions = [v for v in game.get("versions", []) if v["id"] != args.id]
    versions.insert(0, {"id": args.id, "label": args.label, "date": args.date, "temporary": args.temporary, "notes": args.notes})
    game["versions"] = versions
    save(data)

    total = folder_size(os.path.join(ROOT, "games"))
    where = f"{args.slug}/{PLAY}/" if target == play else f"{args.slug}/{args.id}/"
    print(f"added {args.id} at {where} ({folder_size(target) / 1048576:.1f} MB); games/ is now {total / 1048576:.0f} MB")
    if total > SITE_WARN:
        print("warning: close to GitHub Pages' 1 GB limit - remove old temporary versions with --remove")


if __name__ == "__main__":
    main()
