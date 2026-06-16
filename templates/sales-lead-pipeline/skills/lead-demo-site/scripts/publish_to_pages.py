#!/usr/bin/env python3
"""Publish a built lead demo to a GitHub Pages repo.

This is intended to be run by Hermes (terminal tool), after build.sh succeeds.

Behavior:
- Copies ~/.hermes/leads/demos/{slug}/ into a local checkout of hermes-demos repo
- Writes/updates demos/manifest.json
- Commits and pushes
- Prints JSON: {"ok": true, "slug": "...", "url": "..."}

Prereqs:
- GitHub token auth already configured for git push (via gh auth or a token helper)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


HERMES_HOME = Path.home() / ".hermes"
LOCAL_DEMOS = HERMES_HOME / "leads" / "demos"


def run(cmd: list[str], cwd: Path) -> str:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stdout}\n{p.stderr}".strip())
    return (p.stdout or "").strip()


def ensure_repo(repo_dir: Path) -> None:
    if not (repo_dir / ".git").exists():
        raise RuntimeError(f"Pages repo not found at {repo_dir}. Clone it first.")


def copy_demo(slug: str, src: Path, dst: Path) -> None:
    if not src.exists():
        raise RuntimeError(f"Missing local demo folder: {src}")
    (dst.parent).mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def update_manifest(repo_dir: Path, slug: str, template_used: str | None) -> None:
    manifest = repo_dir / "demos" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    data = {"updated_at": datetime.now(timezone.utc).isoformat(), "demos": {}}
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            pass
        data.setdefault("demos", {})
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["demos"][slug] = {
        "slug": slug,
        "template_used": template_used,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "path": f"demos/{slug}/index.html",
    }
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_local_meta(slug: str) -> dict:
    meta_path = LOCAL_DEMOS / slug / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_local_demo_url(slug: str, url: str) -> None:
    meta_path = LOCAL_DEMOS / slug / "meta.json"
    if not meta_path.exists():
        return
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        meta = {}
    meta["demo_url"] = url
    meta["published_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: publish_to_pages.py <slug> [--repo /path/to/hermes-demos] [--base-url https://...]", file=sys.stderr)
        return 1

    slug = sys.argv[1].strip().lower().replace("_", "-")
    repo_dir = Path(os.environ.get("HERMES_DEMOS_REPO", "")).expanduser() if os.environ.get("HERMES_DEMOS_REPO") else None
    base_url = os.environ.get("HERMES_DEMOS_BASE_URL")

    args = sys.argv[2:]
    while args:
        a = args.pop(0)
        if a == "--repo" and args:
            repo_dir = Path(args.pop(0)).expanduser()
        elif a == "--base-url" and args:
            base_url = args.pop(0).strip()

    if not repo_dir:
        # default local checkout path used in this workspace; override via --repo in Hermes
        repo_dir = Path.home() / "DevSpace" / "Projects" / "cheetclaw" / "hermes-demos"

    if not base_url:
        # default for this GitHub user/repo
        base_url = "https://zedted0112.github.io/hermes-demos"

    ensure_repo(repo_dir)

    src = LOCAL_DEMOS / slug
    dst = repo_dir / "demos" / slug
    copy_demo(slug, src, dst)

    meta = read_local_meta(slug)
    update_manifest(repo_dir, slug, meta.get("template_used"))

    # Ensure Pages root has .nojekyll (workflow also touches it, but keep it in repo)
    (repo_dir / ".nojekyll").write_text("", encoding="utf-8")

    run(["git", "add", "."], repo_dir)
    msg = f"Publish demo: {slug}"
    run(["git", "commit", "-m", msg], repo_dir)
    run(["git", "push"], repo_dir)

    url = f"{base_url.rstrip('/')}/demos/{slug}/"
    write_local_demo_url(slug, url)
    print(json.dumps({"ok": True, "slug": slug, "url": url}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        raise

