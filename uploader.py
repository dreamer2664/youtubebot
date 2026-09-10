"""YouTube upload client: OAuth, resumable upload, retries, audit gate."""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from config import Config

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

API_NAME = "youtube"
API_VERSION = "v3"

# Retry only on these; anything else is a real error worth showing.
RETRIABLE_STATUS = {500, 502, 503, 504}
MAX_RETRIES = 6


class UploadBlocked(RuntimeError):
    pass


def get_credentials(cfg: Config, interactive: bool = True) -> Credentials:
    """Load cached credentials, refreshing or re-authorising as needed."""
    token_path = cfg.token_file

    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as exc:  # noqa: BLE001 - corrupt cache should not be fatal
            print(f"[auth] cached token unreadable ({exc}); re-authorising.")
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
            print("[auth] refreshed existing token.")
            return creds
        except Exception as exc:  # noqa: BLE001
            print(f"[auth] refresh failed ({exc}); re-authorising.")

    if not interactive:
        raise UploadBlocked("No valid credentials and not allowed to prompt for login.")

    if not cfg.client_secret_file.exists():
        raise UploadBlocked(
            f"Missing {cfg.client_secret_file.name}. Download the OAuth Desktop-app "
            "client JSON from the Google Cloud Console and place it in the project folder."
        )

    print("[auth] opening a browser to authorise. This happens once.")
    print("[auth] You will see an 'unverified app' warning — that is expected for a")
    print("[auth] personal tool. Click Advanced, then Go to (unsafe).")
    flow = InstalledAppFlow.from_client_secrets_file(str(cfg.client_secret_file), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    token_path.write_text(creds.to_json(), encoding="utf-8")
    try:
        token_path.chmod(0o600)
    except OSError:
        pass
    print("[auth] authorised. Token cached — you will not be asked again.")
    return creds


def build_service(cfg: Config, interactive: bool = True):
    return build(API_NAME, API_VERSION, credentials=get_credentials(cfg, interactive))


def assert_audit_gate(cfg: Config, requested_privacy: str) -> str:
    """Enforce the private-lock rule before wasting an upload.

    YouTube force-locks videos to private when they come from a project that has
    not passed the Compliance Audit, and locked videos cannot be unlocked or
    appealed — they must be re-uploaded. So refuse public uploads until the user
    confirms the audit passed.
    """
    privacy = (requested_privacy or cfg.privacy_status).lower()
    if privacy == "public" and not cfg.audit_passed:
        raise UploadBlocked(
            "Refusing to upload as PUBLIC.\n\n"
            "  Videos uploaded from a project that has not passed YouTube's Compliance\n"
            "  Audit are force-locked to private, permanently. They cannot be unlocked,\n"
            "  not via the API and not via YouTube Studio, and there is no appeal —\n"
            "  you would have to re-upload every one of them.\n\n"
            "  So generate and queue videos now, and upload once Google approves you.\n"
            "  When that happens, set in config.yaml:\n\n"
            "      privacy:\n"
            "        status: public\n"
            "        audit_passed: true\n\n"
            "  To upload as private or unlisted right now, pass --privacy private."
        )
    return privacy


def _backoff_delay(attempt: int) -> float:
    return min(2 ** attempt + random.uniform(0, 1), 60.0)


def upload_video(
    youtube,
    video_path: Path,
    meta: dict,
    privacy: str,
    chunk_size: int = 8 * 1024 * 1024,
) -> dict:
    """Resumable upload with retry/backoff. Returns the inserted video resource."""
    snippet = {
        "title": meta["title"][:100],
        "description": meta.get("description", "")[:5000],
        "tags": (meta.get("tags") or [])[:30],
        "categoryId": str(meta.get("categoryId", "22")),
    }
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}

    body = {"snippet": snippet, "status": status}
    if privacy == "public" and meta.get("publishAt"):
        status["publishAt"] = meta["publishAt"]

    media = MediaFileUpload(
        str(video_path), chunksize=chunk_size, resumable=True, mimetype="video/*"
    )
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    attempt = 0
    while response is None:
        attempt += 1
        try:
            progress, response = request.next_chunk()
            if progress:
                print(f"    uploaded {int(progress.progress() * 100)}%")
        except HttpError as exc:
            code = exc.resp.status
            if code in RETRIABLE_STATUS and attempt <= MAX_RETRIES:
                delay = _backoff_delay(attempt)
                print(f"    HTTP {code}, retrying in {delay:.1f}s ({attempt}/{MAX_RETRIES})")
                time.sleep(delay)
                continue
            raise
        except Exception as exc:  # noqa: BLE001 - network hiccup during chunk send
            if attempt <= MAX_RETRIES:
                delay = _backoff_delay(attempt)
                print(f"    {type(exc).__name__}, retrying in {delay:.1f}s ({attempt}/{MAX_RETRIES})")
                time.sleep(delay)
                continue
            raise

    return response


def wait_for_processing(youtube, video_id: str, timeout: int = 1800, poll: int = 20) -> str:
    """Poll until YouTube finishes transcoding. Returns the final status."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = (
                youtube.videos()
                .list(part="status,processingDetails", id=video_id)
                .execute()
            )
            items = response.get("items") or []
            if items:
                details = items[0].get("processingDetails", {})
                state = details.get("processingStatus", "unknown")
                if state in ("succeeded", "failed", "rejected", "terminated"):
                    return state
                print(f"    processing: {state}")
        except HttpError as exc:
            print(f"    poll failed: {exc}")
        time.sleep(poll)
    return "timeout"


def set_public(youtube, video_id: str) -> dict:
    """Flip an uploaded video to public. Only works if the project passed audit."""
    body = {"id": video_id, "status": {"privacyStatus": "public"}}
    return youtube.videos().update(part="status", body=body).execute()


def set_thumbnail(youtube, video_id: str, thumbnail_path: Path) -> dict:
    media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
    return youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
