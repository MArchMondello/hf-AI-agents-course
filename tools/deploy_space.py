"""Change a Hugging Face Space safely: download a working copy, see the diff, upload it as ONE commit.

    # 1. a working copy of the Space (anonymous); remembers which Space and which commit it came from
    .venv/bin/python tools/deploy_space.py get <owner>/<space> <folder> [--sha <commit>]

    # 2. edit and test the files in <folder>, then see what would change (dry run, anonymous)
    .venv/bin/python tools/deploy_space.py put <folder> -m "what changed" [-d description.md]

    # 3. upload: one commit on top of the commit you started from, then restart the Space
    .venv/bin/python tools/deploy_space.py put <folder> -m "what changed" [-d description.md] --commit

Rollback = the same two steps with an older commit: `get ... --sha <older>` then `put ... --commit`.

Safety, by design:
- the write token (HF_TOKEN_SPACE_WRITE, from the .env found by searching upwards) is read ONLY by --commit;
  everything else is anonymous, so a dry run can't change anything;
- if the Space changed after `get` (e.g. an edit in the web UI), `put` stops: the commit is pinned to the
  commit you started from (`parent_commit`), so nobody's change is overwritten;
- only new and changed files are uploaded; a file you removed from <folder> is deleted from the Space
  only with --delete (the dry run lists them).
"""
import argparse
import filecmp
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")   # set before importing huggingface_hub
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
from huggingface_hub import CommitOperationAdd, CommitOperationDelete, HfApi, snapshot_download

STAMP = ".deployed-from.json"                     # written by `get`, never uploaded
SKIP = {"__pycache__", ".pytest_cache", ".cache", ".git"}


def files(folder: Path) -> set[str]:
    """Relative paths of the files that belong to the Space (no caches, no stamp)."""
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*")
            if p.is_file() and p.name != STAMP and not SKIP & set(p.relative_to(folder).parts)}


# --- 1. get: download the Space at a commit, and stamp the folder with where it came from ---
def get(space: str, folder: Path, sha: str | None) -> None:
    api = HfApi(token=False)
    head = api.space_info(space).sha                    # the Space now: the parent of the next commit
    sha = sha or head
    snapshot_download(space, repo_type="space", revision=sha, local_dir=folder, token=False)
    (folder / STAMP).write_text(json.dumps({"space": space, "files_from": sha, "parent": head}, indent=1))
    print(f"{space} @ {sha[:7]} → {folder}  ({len(files(folder))} files; parent of the next commit: {head[:7]})")


# --- 2. put: diff against the parent, then (only with --commit) upload ---
def put(folder: Path, message: str, description: Path | None, commit: bool, delete: bool) -> None:
    stamp = json.loads((folder / STAMP).read_text())
    space, parent = stamp["space"], stamp["parent"]
    api = HfApi(token=False)

    # 2a. has anyone changed the Space since `get`?
    head = api.space_info(space).sha
    moved = head != parent
    if moved:
        print(f"⚠ the Space moved: {parent[:7]} when you started, {head[:7]} now. Run `get` again and redo the change.")
        if commit:
            sys.exit("stopped: the Space moved")

    # 2b. what changes: the working copy vs the files at the parent
    live = Path(snapshot_download(space, repo_type="space", revision=parent, token=False))
    mine, theirs = files(folder), files(live)
    added = sorted(mine - theirs)
    changed = sorted(p for p in mine & theirs if not filecmp.cmp(folder / p, live / p, shallow=False))
    removed = sorted(theirs - mine)
    print(f"{space} @ {parent[:7]}: {len(added)} new, {len(changed)} changed, {len(removed)} removed, "
          f"{len(mine & theirs) - len(changed)} unchanged")
    for label, paths in (("new", added), ("changed", changed), ("removed", removed)):
        for p in paths:
            print(f"  {label:8} {p}")

    if not commit:
        print("DRY RUN: nothing uploaded (add --commit to upload)")
        return
    # 2c. the other checks that stop a commit
    if not (added or changed or removed):
        sys.exit("stopped: nothing to upload")
    if removed and not delete:
        sys.exit("stopped: files would be deleted from the Space; add --delete if that is what you want")

    # 2d. upload as one commit pinned to the parent, then restart
    from dotenv import dotenv_values, find_dotenv
    token = dotenv_values(find_dotenv(usecwd=True)).get("HF_TOKEN_SPACE_WRITE")
    if not token:
        sys.exit("stopped: HF_TOKEN_SPACE_WRITE is not set in .env")
    api = HfApi(token=token)
    ops = [CommitOperationAdd(path_in_repo=p, path_or_fileobj=str(folder / p)) for p in added + changed]
    ops += [CommitOperationDelete(path_in_repo=p) for p in removed]
    info = api.create_commit(space, repo_type="space", operations=ops, parent_commit=parent,
                             commit_message=message,
                             commit_description=description.read_text() if description else None)
    print("commit:", info.oid[:7], info.commit_url)
    print("restart:", api.restart_space(space).stage)
    print(f"rollback: get {space} <folder> --sha {parent[:7]}, then put --commit")


# --- 3. Command line ---
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", help="download a working copy")
    g.add_argument("space"); g.add_argument("folder", type=Path); g.add_argument("--sha")
    u = sub.add_parser("put", help="dry run, or upload with --commit")
    u.add_argument("folder", type=Path); u.add_argument("-m", "--message", required=True)
    u.add_argument("-d", "--description", type=Path)
    u.add_argument("--commit", action="store_true"); u.add_argument("--delete", action="store_true")
    a = ap.parse_args()
    if a.cmd == "get":
        get(a.space, a.folder, a.sha)
    else:
        put(a.folder, a.message, a.description, a.commit, a.delete)
