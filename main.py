#!/usr/bin/env python3
"""Free YouTube auto-upload pipeline.

    python main.py preflight     check setup before anything else
    python main.py generate      AI script -> images -> voice -> finished MP4
    python main.py upload        upload everything in the queue
    python main.py queue         show queue status
    python main.py auth          (re)authorise with YouTube
    python main.py publish       flip queued videos to public (post-audit)

Nothing here costs money. Quota, not currency, is the limit:
100 videos.insert calls/day, 10,000 units/day for everything else.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import traceback
from pathlib import Path

from config import load_config
from jobqueue import Queue
from scriptgen import get_provider

BANNER = """\
======================================================================
  Free YouTube uploader
  Cost: 0. Limits are quota, not money.
======================================================================
"""


def die(message: str, code: int = 1) -> None:
    print(f"\n\u274c {message}\n")
    sys.exit(code)


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------
def cmd_preflight(cfg, args) -> int:
    print(BANNER)
    print("Checking your setup. Everything here is free.\n")
    problems: list[str] = []
    warnings: list[str] = []

    def ok(label: str, detail: str = "") -> None:
        print(f"  \u2705 {label}{(' — ' + detail) if detail else ''}")

    def bad(label: str, detail: str = "") -> None:
        print(f"  \u274c {label}{(' — ' + detail) if detail else ''}")
        problems.append(label)

    def warn(label: str, detail: str = "") -> None:
        print(f"  \u26a0\ufe0f  {label}{(' — ' + detail) if detail else ''}")
        warnings.append(label)

    # 1. binaries
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool):
            ok(f"{tool} installed")
        else:
            bad(
                f"{tool} missing",
                "install with: brew install ffmpeg / sudo apt install ffmpeg / "
                "winget install Gyan.FFmpeg",
            )

    # 2. python deps
    for module in ("googleapiclient", "google_auth_oauthlib", "edge_tts", "requests"):
        try:
            __import__(module)
            ok(f"python module {module}")
        except ImportError:
            bad(f"python module {module}", "run: pip install -r requirements.txt")

    # 3. client secret
    if cfg.client_secret_file.exists():
        ok(f"{cfg.client_secret_file.name} present")
    else:
        bad(
            "client_secret.json missing",
            "download the Desktop-app OAuth JSON from the Google Cloud Console "
            "and put it in this folder",
        )

    # 4. script provider
    if cfg.ai_provider == "template":
        warn("script provider is 'template'", "offline, lower quality. Fine to start with.")
    elif cfg.gemini_api_key:
        ok(f"Gemini key present, model {cfg.gemini_model}")
    else:
        warn(
            "no Gemini API key",
            "will fall back to templates. Free key: https://aistudio.google.com/apikey",
        )

    # 5. privacy gate
    print()
    if cfg.privacy_status == "public" and not cfg.audit_passed:
        bad(
            "privacy is 'public' but audit_passed is false",
            "uploads would be force-locked private forever. Set status: private, "
            "or set audit_passed: true once Google approves your audit.",
        )
    elif cfg.audit_passed:
        ok(f"privacy {cfg.privacy_status}, audit_passed true — public uploads allowed")
    else:
        ok(f"privacy {cfg.privacy_status} (safe). Flip to public after your audit passes.")

    # 6. live check against YouTube (costs ~1 quota unit)
    print()
    if not args.skip_api:
        print("  Live check against YouTube (costs about 1 quota unit)...")
        try:
            from uploader import build_service

            youtube = build_service(cfg, interactive=not args.no_login)
            response = youtube.channels().list(part="snippet", mine=True).execute()
            items = response.get("items") or []
            if items:
                snippet = items[0]["snippet"]
                ok("YouTube API reachable")
                print(f"       channel : {snippet.get('title')}")
                print(f"       handle  : {snippet.get('customUrl', 'n/a')}")
            else:
                warn(
                    "authorised, but no channel found on this account",
                    "create a channel at youtube.com/channel_switcher",
                )
        except Exception as exc:  # noqa: BLE001
            text = str(exc)
            bad("YouTube API check failed", text.splitlines()[0][:160])
            if "accessNotConfigured" in text or "has not been used in project" in text:
                print(
                    "       \u2192 Enable 'YouTube Data API v3' in your project:\n"
                    "         https://console.cloud.google.com/apis/library/youtube.googleapis.com"
                )
            if "invalid_grant" in text or "Token has been expired" in text:
                print("       \u2192 Delete token.json and re-run: python main.py auth")
            if "Access blocked" in text or "app has not completed" in text:
                print(
                    "       \u2192 Add your own email as a Test user:\n"
                    "         https://console.cloud.google.com/auth/audience"
                )
    else:
        print("  (skipped live check with --skip-api)")

    print()
    if problems:
        print(f"\u274c {len(problems)} problem(s) to fix before this will work:")
        for problem in problems:
            print(f"   - {problem}")
        return 1
    print("\u2705 Setup looks good." + (" (with warnings above)" if warnings else ""))
    print("   Next: python main.py generate")
    return 0


# --------------------------------------------------------------------------
# generate
# --------------------------------------------------------------------------
def cmd_generate(cfg, args) -> int:
    print(BANNER)
    provider = get_provider(cfg)
    queue = Queue(cfg.state_file)
    count = args.count

    for number in range(1, count + 1):
        topic = args.topic or cfg.topic
        if count > 1:
            topic = f"{topic} (variation {number} of {count}: choose a different specific story each time)"
        print(f"[{number}/{count}] topic: {topic}")

        job = queue.add(topic)
        job_dir = cfg.work_dir / job.id
        job_dir.mkdir(parents=True, exist_ok=True)

        try:
            print("  1/4 script")
            script = provider.generate(cfg, args.topic)
            print(f"      title   : {script.title}")
            print(f"      scenes  : {len(script.scenes)}")
            print(f"      est. len: {script.estimated_seconds()}s (target {cfg.target_seconds}s)")
            (job_dir / "script.json").write_text(
                json.dumps(
                    {
                        "title": script.title,
                        "description": script.description,
                        "tags": script.tags,
                        "provider": script.provider,
                        "scenes": [
                            {"narration": s.narration, "image_prompt": s.image_prompt}
                            for s in script.scenes
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            print("  2/4 voiceover")
            from voiceover import generate_scene_audio

            audio_paths = generate_scene_audio(script, cfg, job_dir / "audio")

            print("  3/4 images")
            from images import generate_scene_images

            image_paths = generate_scene_images(script, cfg, job_dir / "images")

            print("  4/4 assembling video")
            from assembler import (
                assemble_video,
                build_segments,
                build_thumbnail,
                write_metadata,
            )

            segments, padded, durations = build_segments(
                image_paths, audio_paths, job_dir, cfg
            )
            out_path = cfg.out_dir / f"{job.id}.mp4"
            assemble_video(segments, padded, out_path, cfg, work_dir=job_dir)
            build_thumbnail(image_paths[0], script.title, out_path.with_suffix(".jpg"), cfg)
            meta_path = write_metadata(script, out_path, cfg)

            total = sum(durations)
            size_mb = out_path.stat().st_size / (1024 * 1024)
            queue.update(
                job,
                status="generated",
                title=script.title,
                video_file=str(out_path),
                meta_file=str(meta_path),
            )
            print(f"  \u2705 {out_path.name}  {total:.0f}s  {size_mb:.1f} MB")

            if not args.keep_work:
                shutil.rmtree(job_dir, ignore_errors=True)

        except Exception as exc:  # noqa: BLE001
            queue.update(job, status="failed", error=str(exc)[:400])
            print(f"  \u274c failed: {exc}")
            if args.verbose:
                traceback.print_exc()
            if not args.keep_going:
                return 1

    print()
    print(queue.format_table())
    print("\nNext: python main.py upload")
    return 0


# --------------------------------------------------------------------------
# upload
# --------------------------------------------------------------------------
def cmd_upload(cfg, args) -> int:
    print(BANNER)
    queue = Queue(cfg.state_file)
    pending = queue.pending()

    if not pending:
        print("Nothing to upload. Run: python main.py generate")
        return 0

    privacy = args.privacy or cfg.privacy_status
    limit = min(len(pending), args.limit or cfg.max_uploads_per_run)

    print(f"Uploading {limit} of {len(pending)} queued videos as '{privacy}'.")
    print(f"Daily YouTube allowance is 100 uploads; this run is capped at {limit}.\n")

    try:
        from uploader import UploadBlocked, assert_audit_gate

        privacy = assert_audit_gate(cfg, privacy)
    except UploadBlocked as exc:
        print(exc)
        print("\nMeanwhile these videos stay safely in your queue.")
        return 1

    from uploader import build_service, set_thumbnail, upload_video, wait_for_processing

    try:
        youtube = build_service(cfg)
    except UploadBlocked as exc:
        die(str(exc))

    succeeded = 0
    for index, job in enumerate(pending[:limit], start=1):
        video_path = Path(job.video_file)
        if not video_path.exists():
            queue.update(job, status="failed", error=f"missing file {video_path}")
            print(f"[{index}/{limit}] \u274c {job.id}: file missing")
            continue

        meta = json.loads(Path(job.meta_file).read_text(encoding="utf-8"))
        print(f"[{index}/{limit}] {meta['title']}")

        try:
            response = upload_video(youtube, video_path, meta, privacy)
            video_id = response["id"]
            queue.update(job, status="uploaded", youtube_id=video_id, privacy=privacy)
            print(f"    uploaded \u2192 https://youtu.be/{video_id}")

            if not args.no_thumbnail:
                thumb = video_path.with_suffix(".jpg")
                if thumb.exists():
                    try:
                        set_thumbnail(youtube, video_id, thumb)
                        print("    thumbnail set")
                    except Exception as exc:  # noqa: BLE001
                        print(f"    thumbnail failed (needs a verified channel): {exc}")

            if not args.no_wait:
                state = wait_for_processing(youtube, video_id)
                queue.update(job, status="done" if state == "succeeded" else "failed",
                             error="" if state == "succeeded" else f"processing {state}")
                print(f"    processing: {state}")
            succeeded += 1

        except Exception as exc:  # noqa: BLE001
            queue.update(job, status="failed", error=str(exc)[:400])
            print(f"    \u274c {str(exc).splitlines()[0][:160]}")
            if "quotaExceeded" in str(exc):
                print("    Daily quota hit. Resets at midnight Pacific (09:00 Italy, summer).")
                break
            if "locked" in str(exc).lower() or "private" in str(exc).lower():
                queue.update(job, status="private_locked")

    print(f"\n\u2705 {succeeded}/{limit} uploaded.")
    print(queue.format_table())
    return 0


# --------------------------------------------------------------------------
# publish (post-audit)
# --------------------------------------------------------------------------
def cmd_publish(cfg, args) -> int:
    print(BANNER)
    queue = Queue(cfg.state_file)

    if not cfg.audit_passed:
        print(
            "Refusing to publish.\n\n"
            "  Videos uploaded from a project that has not passed the Compliance Audit\n"
            "  are force-locked to private and cannot be unlocked, so this call would\n"
            "  change nothing.\n\n"
            "  Once Google approves your audit, set in config.yaml:\n"
            "      privacy:\n"
            "        audit_passed: true\n"
        )
        return 1

    from uploader import build_service, set_public

    youtube = build_service(cfg)
    targets = queue.in_status("uploaded") + queue.in_status("done")
    if not targets:
        print("No uploaded videos to publish.")
        return 0

    for job in targets:
        if not job.youtube_id:
            continue
        try:
            set_public(youtube, job.youtube_id)
            queue.update(job, privacy="public", status="done")
            print(f"  \u2705 public: {job.url}  {job.title[:50]}")
        except Exception as exc:  # noqa: BLE001
            print(f"  \u274c {job.id}: {str(exc).splitlines()[0][:140]}")
    return 0


# --------------------------------------------------------------------------
# queue / auth
# --------------------------------------------------------------------------
def cmd_queue(cfg, args) -> int:
    print(Queue(cfg.state_file).format_table())
    return 0


def cmd_auth(cfg, args) -> int:
    if cfg.token_file.exists() and args.fresh:
        cfg.token_file.unlink()
        print("[auth] cleared cached token.")
    from uploader import build_service

    youtube = build_service(cfg)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    items = response.get("items") or []
    if items:
        print(f"\u2705 Authorised as: {items[0]['snippet'].get('title')}")
    else:
        print("\u26a0\ufe0f  Authorised, but no channel found on this account.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Free YouTube auto-upload pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", help="path to config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preflight", help="check your setup")
    p.add_argument("--skip-api", action="store_true", help="skip the live YouTube check")
    p.add_argument("--no-login", action="store_true", help="do not open a browser")

    p = sub.add_parser("generate", help="make videos")
    p.add_argument("--topic", help="override the configured channel topic")
    p.add_argument("--count", type=int, default=1, help="how many videos to make")
    p.add_argument("--keep-work", action="store_true", help="keep intermediate files")
    p.add_argument("--keep-going", action="store_true", help="continue after a failure")
    p.add_argument("--verbose", action="store_true")

    p = sub.add_parser("upload", help="upload queued videos")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"])
    p.add_argument("--limit", type=int, help="max uploads this run")
    p.add_argument("--no-thumbnail", action="store_true")
    p.add_argument("--no-wait", action="store_true", help="do not wait for processing")

    sub.add_parser("queue", help="show the queue")
    sub.add_parser("publish", help="make uploaded videos public (post-audit)")

    p = sub.add_parser("auth", help="authorise with YouTube")
    p.add_argument("--fresh", action="store_true", help="discard the cached token first")

    args = parser.parse_args()
    cfg = load_config(args.config)

    handlers = {
        "preflight": cmd_preflight,
        "generate": cmd_generate,
        "upload": cmd_upload,
        "publish": cmd_publish,
        "queue": cmd_queue,
        "auth": cmd_auth,
    }
    return handlers[args.command](cfg, args)


if __name__ == "__main__":
    sys.exit(main())
